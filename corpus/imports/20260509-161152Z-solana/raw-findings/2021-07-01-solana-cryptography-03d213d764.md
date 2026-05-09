---
case_id: case_20210701_03d213d764
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2021-07-01
source_refs:
  - git:03d213d764ebc3a7a4439ee8b678a3d1b439b8c3
  - "client/src/rpc_custom_error.rs:155"
  - "rpc/src/rpc.rs:1900"
  - "ledger/src/entry.rs:529"
  - "client/src/rpc_custom_error.rs:53"
bug_class: transaction-signature-length-validation
impact_type:
  - invalid-transaction-admission
tags:
  - blockchain-core
  - transaction-validation
  - signature
  - rpc
  - ledger
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit `verify_signatures_len()` checks in RPC transaction verification and ledger entry verification/hashing paths. The evidence supports a security-relevant transaction validation hardening for rejecting transactions with extra or otherwise invalid signature counts, but it does not establish a concrete exploit such as forgery, replay, double-spend, or consensus divergence.

## Observed Patch Facts

1. In `client/src/rpc_custom_error.rs`, the patch adds `RpcCustomError::TransactionSignatureLenMismatch => Self {`.

2. In `rpc/src/rpc.rs`, the patch adds `if !transaction.verify_signatures_len() {`.

3. In `ledger/src/entry.rs`, the patch adds `if verify_tx_signatures_len && !tx.verify_signatures_len() {`.

4. In `client/src/rpc_custom_error.rs`, the patch adds `#[error("TransactionSignatureLenMismatch")]`.

## Project Context

The changed code sits primarily in `client/src`, `rpc/src`, `ledger/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `rpc/src/transaction_status_service.rs`, `rpc/src/send_transaction_service.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rpc/src/transaction_status_service.rs`, `rpc/src/send_transaction_service.rs`. The strongest project-level identifiers around this patch are `RpcCustomError::TransactionSignatureLenMismatch`, `ErrorCode::ServerError`, `None`, and `TransactionSignatureLenMismatch`.

## Before/After Behavior

Before the patch, the shown RPC verification path returned success after `transaction.verify()` and `transaction.verify_precompiles()` passed. After the patch, it also rejects transactions failing `transaction.verify_signatures_len()`. Before the patch, the shown ledger entry verification path proceeded from size/precompile checks to `tx.verify_and_hash_message()`. After the patch, when `verify_tx_signatures_len` is enabled, it returns `None` if `tx.verify_signatures_len()` fails. RPC custom error support for signature length mismatch was also added.

# Root Cause

The observed transaction verification paths lacked an explicit structural check for signature-vector length before accepting or hashing a transaction as verified.

## Walkthrough

1. A transaction reaches RPC verification in `rpc/src/rpc.rs`.

2. The pre-patch evidence shows RPC verification checking signature validity and precompiles, then returning success.

3. The patch adds a `verify_signatures_len()` rejection before RPC verification succeeds.

4. Ledger entry verification in `ledger/src/entry.rs` verifies transactions before hashing messages for entry handling.

5. The patch adds a gated signature-length check that stops processing by returning `None` when enabled and the check fails.

6. Client RPC error additions support reporting the mismatch condition but are not the root cause fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rpc/src/rpc.rs | 1893 | RPC transaction verification now rejects transactions whose signature vector length is invalid before returning success. |
| ledger/src/entry.rs | 515 | Ledger entry transaction verification and hashing now optionally rejects transactions with invalid signature length. |
| client/src/rpc_custom_error.rs | 53 | Adds an RPC custom error variant for transaction signature length mismatch. |
| client/src/rpc_custom_error.rs | 155 | Maps the signature length mismatch condition into a JSON-RPC server error response. |

## Code Snippets

## Snippet 1

Context: `client/src/rpc_custom_error.rs:155` (changes signature or replay validation logic)

Before
```rust
data: None,
            },
        }
    }
```
After
```rust
data: None,
            },
            RpcCustomError::TransactionSignatureLenMismatch => Self {
                code: ErrorCode::ServerError(
                    JSON_RPC_SERVER_ERROR_TRANSACTION_SIGNATURE_LEN_MISMATCH,
                ),
                message: "Transaction signature length mismatch".to_string(),
                data: None,
```

## Snippet 2

Context: `rpc/src/rpc.rs:1900` (changes a sensitive control or state-update path)

Before
```rust
}

    Ok(())
}
```
After
```rust
}

    if !transaction.verify_signatures_len() {
        return Err(RpcCustomError::TransactionSignatureVerificationFailure.into());
    }

    Ok(())
}
```

## Snippet 3

Context: `ledger/src/entry.rs:529` (changes a sensitive control or state-update path)

Before
```rust
tx.verify_precompiles().ok()?;
                }
                tx.verify_and_hash_message().ok()?
            } else {
```
After
```rust
tx.verify_precompiles().ok()?;
                }
                if verify_tx_signatures_len && !tx.verify_signatures_len() {
                    return None;
                }
                tx.verify_and_hash_message().ok()?
            } else {
```

## Snippet 4

Context: `client/src/rpc_custom_error.rs:53` (changes a sensitive control or state-update path)

Before
```rust
#[error("ScanError")]
    ScanError { message: String },
}
```
After
```rust
#[error("ScanError")]
    ScanError { message: String },
    #[error("TransactionSignatureLenMismatch")]
    TransactionSignatureLenMismatch,
}
```

# Fix Pattern

Add explicit structural validation for transaction signature-vector length at transaction admission and ledger verification boundaries.

## How It Was Fixed

The RPC path now calls `transaction.verify_signatures_len()` and rejects failure with `TransactionSignatureVerificationFailure`. The ledger entry path now checks `verify_tx_signatures_len && !tx.verify_signatures_len()` and rejects by returning `None`. RPC custom error code was extended for signature length mismatch reporting.

# Why It Matters

1. Signature validity and signature-vector structure are distinct validation properties.

2. Transactions with invalid signature counts are rejected earlier in the observed paths.

3. The evidence supports hardening of transaction admission and ledger verification.

4. The evidence does not prove a concrete exploit impact.

# Evidence Notes

Grounded evidence is limited to the supplied snippets in `rpc/src/rpc.rs`, `ledger/src/entry.rs`, and `client/src/rpc_custom_error.rs`. The commit title supports the narrower claim that transactions with extra signatures are being rejected. The evidence does not show the implementation of `verify_signatures_len()`, the feature-gate activation behavior, bank execution reachability before the patch, or any demonstrated exploit outcome. Protocol security invariant: Transaction verification should reject transactions whose signature vector length is invalid for the transaction, rather than treating successful signature/precompile checks as sufficient. Verification notes: The evidence does not prove that extra signatures allowed signature forgery. The evidence does not prove replay, double-spend, or consensus divergence by itself. The evidence does not show whether invalid transactions could reach bank execution before this patch in all paths. The client error mapping is not itself the security fix. The precise activation behavior for the feature-gated ledger check is not established from the supplied snippets. Downgraded confidence from high to medium because the exact vulnerable behavior and exploitability are not shown. Kept subsystem as transaction-validation rather than generic cryptography. Kept bug class narrowly scoped to signature-length validation. Classified as security hardening rather than confirmed security fix because impact is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-signature-length-validation`
Final impact type: `invalid-transaction-admission`
Final tags: `blockchain-core, transaction-validation, signature, rpc, ledger, security-hardening`

The supplied patch evidence supports retaining this as security hardening: it adds explicit signature-vector length checks in RPC transaction verification and ledger entry verification before accepting or hashing transactions, matching the commit subject about rejecting transactions with extra signatures. The evidence does not prove a concrete exploit such as forgery, replay, double-spend, or consensus divergence, so the original replay/request-forgery framing is too strong for the final corpus metadata.

## Security Evidence

1. RPC transaction verification now rejects transactions when `!transaction.verify_signatures_len()` before returning success.
2. Ledger entry verification now conditionally rejects transactions when `verify_tx_signatures_len && !tx.verify_signatures_len()` before `verify_and_hash_message()`.
3. The commit subject explicitly states `Reject transactions with extra signatures`, aligning with a transaction validation hardening change.
4. RPC error handling adds a transaction signature length mismatch condition, supporting the new rejection path.

## Missing Evidence

1. No implementation of `verify_signatures_len()` is shown.
2. No proof is supplied that extra signatures enabled replay, request forgery, double-spend, or consensus divergence.
3. No exploit demonstration, advisory, or vulnerable execution trace is included.
4. Feature-gate activation and full pre-patch reachability into bank execution are not established from the snippets.

## Claim Boundaries

1. Classify as security hardening, not a proven security fix.
2. Limit the bug class to transaction signature length validation.
3. Do not claim replay, forgery, double-spend, or consensus divergence from this evidence alone.
4. The client RPC error additions are supporting behavior, not independently security-sensitive.
