---
case_id: case_20240215_945031900
project: reth
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2024-02-15
source_refs:
  - git:94503190022f12fb316d3ab66889df689ebda58e
  - "crates/primitives/src/transaction/eip4844.rs:140"
  - "crates/primitives/src/transaction/sidecar.rs:36"
  - "crates/transaction-pool/src/error.rs:144"
  - "crates/primitives/src/transaction/sidecar.rs:12"
bug_class: missing-protocol-validation
impact_type:
  - protocol-integrity
  - transaction-validation-bypass
confidence: medium
tags:
  - transaction-processing
  - eip-4844
  - protocol-validation
  - cryptographic-binding
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied patch fixes a concrete validation bug in the EIP-4844 blob path. In the shown pre-patch code, the validator derived a versioned hash from each sidecar commitment but did not reject a mismatch against the transaction-declared blob_versioned_hashes. The patch adds that comparison and introduces a dedicated WrongVersionedHash error, so malformed commitment-to-hash bindings are now rejected instead of slipping past this validator.

## Observed Patch Facts

1. In `crates/primitives/src/transaction/eip4844.rs`, the patch replaces `// Calculate the versioned hash` with `// calculate & verify the versioned hash`.

2. In `crates/primitives/src/transaction/sidecar.rs`, the patch adds `/// The versioned hash is incorrect.`.

3. In `crates/transaction-pool/src/error.rs`, the patch replaces `/// Thrown if an EIP-4844 without any blobs arrives` with `/// Thrown if an EIP-4844 transaction without any blobs arrives`.

4. In `crates/primitives/src/transaction/sidecar.rs`, the patch replaces `Signature, Transaction, TransactionSigned, TxEip4844, TxHash, EIP4844_TX_TYPE_ID,` with `Signature, Transaction, TransactionSigned, TxEip4844, TxHash, B256, EIP4844_TX_TYPE_ID,`.

## Project Context

The changed code sits primarily in `crates/primitives/src/transaction`, `crates/primitives/src`, `crates/transaction-pool/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/transaction-pool/src/traits.rs`, `crates/primitives/src/transaction/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/transaction-pool/src/traits.rs`, `crates/primitives/src/transaction/mod.rs`. The strongest project-level identifiers around this patch are `versioned`, `hash`, `have`, and `transaction`. Nearby tests or test-like files include `crates/transaction-pool/tests/it/evict.rs`, `crates/transaction-pool/tests/it/blobs.rs`.

## Before/After Behavior

Before the patch, validate_blob checked list lengths and computed a versioned hash from each commitment, but the provided pre-patch snippet does not show any equality check against the transaction's declared versioned hash. After the patch, the function compares the declared and derived values and returns WrongVersionedHash on mismatch.

# Root Cause

A required protocol check was missing: the validator computed the canonical versioned hash from each supplied KZG commitment but did not enforce that it matched the transaction metadata carrying the claimed blob versioned hashes.

## Walkthrough

1. In crates/primitives/src/transaction/eip4844.rs, validate_blob first ensures the number of declared versioned hashes matches the number of sidecar commitments.

2. It then iterates over each declared versioned hash and corresponding commitment and derives the versioned hash from the commitment.

3. The pre-patch excerpt shows that derivation step but no rejection when the derived value differs from the declared one.

4. The patch inserts an explicit comparison and returns WrongVersionedHash when the values differ.

5. In crates/primitives/src/transaction/sidecar.rs, the error enum gains a WrongVersionedHash variant with have and expected B256 fields to represent that failure mode.

6. The crates/transaction-pool/src/error.rs hunk is documentation wording only and does not materially affect the fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/primitives/src/transaction/eip4844.rs | 120 | Primary EIP-4844 blob sidecar validator; now rejects commitment-to-versioned-hash mismatches before accepting the blob transaction. |
| crates/primitives/src/transaction/sidecar.rs | 30 | Validation error surface for blob transaction checks; adds explicit mismatch reporting for wrong versioned hashes. |
| crates/transaction-pool/src/error.rs | 144 | Pool-facing comment wording only; not part of the security-relevant invariant change. |

## Code Snippets

## Snippet 1

Context: `crates/primitives/src/transaction/eip4844.rs:140` (changes a sensitive control or state-update path)

Before
```rust
let commitment = KzgCommitment::from(*commitment.deref());

            // Calculate the versioned hash
            //
            // TODO: should this method distinguish the type of validation failure? For example
            // whether a certain versioned hash does not match, or whether the blob proof
            // validation failed?
            let calculated_versioned_hash = kzg_to_versioned_hash(commitment);
```
After
```rust
let commitment = KzgCommitment::from(*commitment.deref());

            // calculate & verify the versioned hash
            // https://eips.ethereum.org/EIPS/eip-4844#execution-layer-validation
            let calculated_versioned_hash = kzg_to_versioned_hash(commitment);
            if *versioned_hash != calculated_versioned_hash {
                return Err(BlobTransactionValidationError::WrongVersionedHash {
                    have: *versioned_hash,
```

## Snippet 2

Context: `crates/primitives/src/transaction/sidecar.rs:36` (changes a sensitive control or state-update path)

Before
```rust
#[error("unable to verify proof for non blob transaction: {0}")]
    NotBlobTransaction(u8),
}
```
After
```rust
#[error("unable to verify proof for non blob transaction: {0}")]
    NotBlobTransaction(u8),
    /// The versioned hash is incorrect.
    #[error("wrong versioned hash: have {have}, expected {expected}")]
    WrongVersionedHash {
        /// The versioned hash we got
        have: B256,
        /// The versioned hash we expected
```

## Snippet 3

Context: `crates/transaction-pool/src/error.rs:144` (changes a sensitive control or state-update path)

Before
```rust
#[error("blob sidecar not found for EIP4844 transaction")]
    MissingEip4844BlobSidecar,
    /// Thrown if an EIP-4844 without any blobs arrives
    #[error("blobless blob transaction")]
    NoEip4844Blobs,
    /// Thrown if an EIP-4844 without any blobs arrives
    #[error("too many blobs in transaction: have {have}, permitted {permitted}")]
    TooManyEip4844Blobs {
```
After
```rust
#[error("blob sidecar not found for EIP4844 transaction")]
    MissingEip4844BlobSidecar,
    /// Thrown if an EIP-4844 transaction without any blobs arrives
    #[error("blobless blob transaction")]
    NoEip4844Blobs,
    /// Thrown if an EIP-4844 transaction without any blobs arrives
    #[error("too many blobs in transaction: have {have}, permitted {permitted}")]
    TooManyEip4844Blobs {
```

## Snippet 4

Context: `crates/primitives/src/transaction/sidecar.rs:12` (changes signature or replay validation logic)

Before
```rust
self, Blob, Bytes48, KzgSettings, BYTES_PER_BLOB, BYTES_PER_COMMITMENT, BYTES_PER_PROOF,
    },
    Signature, Transaction, TransactionSigned, TxEip4844, TxHash, EIP4844_TX_TYPE_ID,
};
use alloy_rlp::{Decodable, Encodable, Error as RlpError, Header};
```
After
```rust
self, Blob, Bytes48, KzgSettings, BYTES_PER_BLOB, BYTES_PER_COMMITMENT, BYTES_PER_PROOF,
    },
    Signature, Transaction, TransactionSigned, TxEip4844, TxHash, B256, EIP4844_TX_TYPE_ID,
};
use alloy_rlp::{Decodable, Encodable, Error as RlpError, Header};
```

# Fix Pattern

Add an explicit protocol-invariant check that compares canonical data derived from cryptographic inputs against the transaction-declared value, and fail closed with a specific validation error on mismatch.

## How It Was Fixed

The validator was changed from merely computing the commitment-derived versioned hash to computing and enforcing it. After deriving the versioned hash from each KZG commitment, the code now compares it to the corresponding transaction-provided blob_versioned_hash and rejects mismatches via WrongVersionedHash. The supporting error type was extended to carry the observed and expected hashes.

# Why It Matters

1. It prevents this validator from accepting a blob sidecar whose commitments do not match the transaction's declared versioned hashes.

2. It enforces the binding between transaction metadata and blob commitments, which is part of EIP-4844 validation.

3. It makes the failure mode explicit instead of collapsing it into a generic proof error.

# Evidence Notes

The substantive change is in `TxEip4844::validate_blob`, where the code previously computed a versioned hash from each commitment but, from the shown patch, did not reject mismatches. The fix adds an explicit equality check and a dedicated `WrongVersionedHash` error, which is a concrete protocol-validation invariant rather than a refactor or API cleanup. Deep context indicates the touched transaction-pool file is only commentary cleanup; the real business path is primitive-layer EIP-4844 blob/sidecar validation that pool code consumes. Protocol security invariant: For an EIP-4844 blob transaction, each blob versioned hash declared in the transaction must match the versioned hash derived from the corresponding KZG commitment in the supplied blob sidecar. Proof validity alone is not sufficient if that binding check is missing. Verification notes: The patch does not by itself prove a consensus-split or chain-acceptance exploit; it proves a missing protocol check in validation logic. The evidence does not show whether every block-import path reused this validator, so full network impact is not established from the patch alone. The patch does not indicate proof verification was broken; the gap is the missing binding check between declared versioned hashes and commitments. No evidence here proves fund theft, key compromise, or memory-safety impact. Grounded by direct before/after code in the validator and error enum. Confidence is medium rather than high because end-to-end reachability across all validation paths is not shown in the supplied evidence. No evidence here supports stronger claims such as consensus split, memory corruption, or asset theft. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-protocol-validation`
Final impact type: `protocol-integrity, transaction-validation-bypass`
Final confidence: `medium`
Final tags: `transaction-processing, eip-4844, protocol-validation, cryptographic-binding`

The patch clearly tightens a security-sensitive validation path for EIP-4844 blob transactions by enforcing that each transaction-declared versioned hash matches the canonical hash derived from the supplied KZG commitment. That is a real fail-closed protocol check in a cryptographic transaction-validation path, so it fits security hardening. However, the provided evidence does not prove a concrete exploitable vulnerability, consensus impact, or end-to-end reachability across all acceptance paths, so the stronger phase-3 claim of a confirmed security fix causing state corruption is not supported from the patch alone.

## Security Evidence

1. The main code change adds an explicit equality check between the declared versioned hash and the commitment-derived versioned hash.
2. The new `WrongVersionedHash` error shows mismatches are now rejected instead of merely computing the value.
3. The code comment links the check to EIP-4844 execution-layer validation, indicating a protocol-required invariant.
4. The affected path validates blob transaction sidecars, which is a cryptographic and transaction-acceptance boundary.

## Missing Evidence

1. No proof that this validator guarded every block-import, mempool, or consensus-relevant path.
2. No test or reproducer showing that malformed transactions were actually accepted before the patch.
3. No evidence of real exploitability, chain split, fund loss, or peer-driven impact.
4. The patch does not show whether other validation layers already enforced the same invariant.

## Claim Boundaries

1. Supported claim: a required binding check between KZG commitments and versioned hashes was added.
2. Supported claim: malformed EIP-4844 sidecars with hash/commitment mismatches are now rejected on this path.
3. Not supported: definite state corruption, asset theft, or memory-safety impact.
4. Not supported: a confirmed exploitable security bug across the full client rather than a hardening fix in a sensitive validator.
