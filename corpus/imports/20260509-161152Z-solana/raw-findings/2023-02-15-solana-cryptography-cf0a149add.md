---
case_id: case_20230215_cf0a149add
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2023-02-15
source_refs:
  - git:cf0a149add033e644eb1d18b1694192825e84323
  - "ledger/src/shred/merkle.rs:620"
  - "ledger/src/shred/merkle.rs:538"
  - "ledger/src/shred/merkle.rs:747"
  - "ledger/src/shred/merkle.rs:1430"
bug_class: signature-commitment-hardening
impact_type:
  - cryptographic-integrity-hardening
confidence: medium
tags:
  - blockchain-core
  - cryptography
  - signature
  - merkle-proof
  - commitment-binding
  - serialization-layout
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch removes the embedded Merkle root from serialized Merkle shred branch data, changes proof handling from root-plus-proof branches to proof-only data, and updates tests so signed data resolves to `SignedData::MerkleRoot`. This is plausibly security relevant because it changes cryptographic commitment handling, but the evidence does not prove a vulnerability in the previous behavior. Treat as unclear hardening/layout work rather than a validated security fix.

## Observed Patch Facts

1. In `ledger/src/shred/merkle.rs`, the patch replaces `if offset + 1 != tree.len() {` with `(offset + 1 == tree.len()).then_some(proof)`.

2. In `ledger/src/shred/merkle.rs`, the patch replaces `impl<'a> TryFrom<&'a [u8]> for MerkleBranch<'a> {` with `// Obtains parent's hash by joining two sibiling nodes in merkle tree.`.

3. In `ledger/src/shred/merkle.rs`, the patch replaces `// Compute merkle tree and set the merkle branch on the recovered shreds.` with `// Compute merkle tree and set the merkle proof on the recovered shreds.`.

4. In `ledger/src/shred/merkle.rs`, the patch replaces `assert_eq!(shred::layout::get_merkle_root(shred), merkle_root);` with `assert_eq!(shred::layout::get_merkle_root(shred), Some(merkle_root));`.

## Project Context

The changed code sits primarily in `ledger/src/shred`, `ledger/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `ledger/src/shred/shred_data.rs`, `ledger/src/shred/shred_code.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/shred.rs`, `ledger/src/blockstore.rs`. The strongest project-level identifiers around this patch are `shred`, `tree`, `layout`, and `proof`.

## Before/After Behavior

Before the patch, Merkle branch construction returned `MerkleBranch { root, proof }`, with the root derived from a truncated slice of the final Merkle tree node, and serialized branch parsing split bytes into a root prefix and proof chunks. After the patch, the helper returns proof-only data when tree traversal reaches the expected end, and the root-plus-proof parser is removed. Recovery now refers to setting Merkle proofs and compares proof data against recomputed proof data. Tests now expect no signed-data offsets and verify signatures over `SignedData::MerkleRoot(merkle_root)`.

# Root Cause

The prior design embedded Merkle root material in the shred binary and represented Merkle branch bytes as root plus proof. The commit says this caused signatures to be over a truncated root rather than the full 32-byte hash. The provided evidence does not show that this was exploitable or that invalid proofs could be accepted in practice.

## Walkthrough

1. `make_merkle_branch` previously extracted a root slice from the final Merkle tree node and returned it together with proof entries.

2. Serialized Merkle branch parsing previously required root bytes before proof-entry chunks.

3. The patch changes proof construction to return only proof entries when the tree length check succeeds.

4. The root-plus-proof `TryFrom<&[u8]> for MerkleBranch` parser is removed from the shown path.

5. Recovery now computes Merkle nodes with `Shred::merkle_node` and compares stored proof data with recomputed proof data.

6. Tests now assert that signed data is represented as `SignedData::MerkleRoot(merkle_root)` and that separate signed-data offsets are absent.

7. The commit text says signatures are now over the full 32-byte hash and that signature verification effectively verifies the Merkle proof.

8. No provided evidence demonstrates a practical forgery, replay window, or previous sanitize bypass.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| ledger/src/shred/merkle.rs | 604 | builds Merkle proofs for shreds without returning an embedded truncated root |
| ledger/src/shred/merkle.rs | 538 | removes parsing of MerkleBranch as root-plus-proof serialized bytes |
| ledger/src/shred/merkle.rs | 747 | recovers shreds and verifies reconstructed Merkle proof data against recomputed tree state |
| ledger/src/shred/merkle.rs | 1430 | tests signature input now resolves to SignedData::MerkleRoot and no separate signed-data byte offsets |

## Code Snippets

## Snippet 1

Context: `ledger/src/shred/merkle.rs:620` (changes the branch that decides whether execution stops or continues)

Before
```rust
index >>= 1;
    }
    if offset + 1 != tree.len() {
        return None;
    }
    let root = &tree.last()?.as_ref()[..SIZE_OF_MERKLE_ROOT];
    let root = <&MerkleRoot>::try_from(root).unwrap();
    Some(MerkleBranch { root, proof })
```
After
```rust
index >>= 1;
    }
    (offset + 1 == tree.len()).then_some(proof)
}
```

## Snippet 2

Context: `ledger/src/shred/merkle.rs:538` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

impl<'a> TryFrom<&'a [u8]> for MerkleBranch<'a> {
    type Error = Error;
    fn try_from(merkle_branch: &'a [u8]) -> Result<Self, Self::Error> {
        if merkle_branch.len() < SIZE_OF_MERKLE_ROOT {
            return Err(Error::InvalidMerkleProof);
        }
```
After
```rust
}

// Obtains parent's hash by joining two sibiling nodes in merkle tree.
fn join_nodes<S: AsRef<[u8]>, T: AsRef<[u8]>>(node: S, other: T) -> Hash {
```

## Snippet 3

Context: `ledger/src/shred/merkle.rs:747` (changes the branch that decides whether execution stops or continues)

Before
```rust
})
        .collect::<Result<_, Error>>()?;
    // Compute merkle tree and set the merkle branch on the recovered shreds.
    let nodes: Vec<_> = shreds
        .iter()
        .map(Shred::merkle_tree_node)
        .collect::<Result<_, _>>()?;
    let tree = make_merkle_tree(nodes);
```
After
```rust
})
        .collect::<Result<_, Error>>()?;
    // Compute merkle tree and set the merkle proof on the recovered shreds.
    let nodes: Vec<_> = shreds
        .iter()
        .map(Shred::merkle_node)
        .collect::<Result<_, _>>()?;
    let tree = make_merkle_tree(nodes);
```

## Snippet 4

Context: `ledger/src/shred/merkle.rs:1430` (changes signature or replay validation logic)

Before
```rust
assert_eq!(shred::layout::get_version(shred), Some(version));
            assert_eq!(shred::layout::get_shred_id(shred), Some(key));
            assert_eq!(shred::layout::get_merkle_root(shred), merkle_root);
            let offsets = shred::layout::get_signed_data_offsets(shred).unwrap();
            let data = shred.get(offsets).unwrap();
            assert!(signature.verify(pubkey.as_ref(), data));
            let data = shred::layout::get_signed_data(shred).unwrap();
            assert!(signature.verify(pubkey.as_ref(), data.as_ref()));
```
After
```rust
assert_eq!(shred::layout::get_version(shred), Some(version));
            assert_eq!(shred::layout::get_shred_id(shred), Some(key));
            assert_eq!(shred::layout::get_merkle_root(shred), Some(merkle_root));
            assert_eq!(shred::layout::get_signed_data_offsets(shred), None);
            let data = shred::layout::get_signed_data(shred).unwrap();
            assert_eq!(data, SignedData::MerkleRoot(merkle_root));
            assert!(signature.verify(pubkey.as_ref(), data.as_ref()));
        }
```

# Fix Pattern

Change the serialized Merkle shred format so proof data no longer carries an embedded root, and use the Merkle root commitment as the canonical signed data.

## How It Was Fixed

The patch removes Merkle-root embedding from Merkle branch serialization, removes parsing of branch bytes as root plus proof, updates recovery to operate on recomputed Merkle nodes and proof-only data, and updates tests to verify signatures over `SignedData::MerkleRoot`.

# Why It Matters

1. Changes cryptographic commitment handling in a ledger shred path.

2. Full-root signing is stronger than signing a truncated root, according to the commit text.

3. The serialized format becomes simpler and carries more shred payload capacity.

4. Security impact is not established by the provided evidence.

# Evidence Notes

Grounded evidence is limited to `ledger/src/shred/merkle.rs` changes in proof construction, branch parser removal, recovery behavior, and tests. The commit message supports a signing-input change from truncated root to full 32-byte hash. Unsupported claims removed: confirmed vulnerability, practical forgery, replay, attacker-controlled commitment material, or proven sanitize-bypass behavior. Protocol security invariant: Merkle shred verification should bind the leader signature to the Merkle commitment used for the shred/proof relationship. The provided evidence shows a layout and signing-input change toward proof-only serialized data and full Merkle-root signing, but it does not establish that the prior design allowed forged, replayed, or incorrectly accepted shreds. Verification notes: The patch does not prove a practical forgery against the previous truncated-root design. The patch does not show a replay window or state-changing path reached before signature verification. The patch does not establish that removed sanitize Merkle-proof verification was previously bypassable. The commit also has a storage-capacity and serialization-layout motivation, so it should not be classified as a confirmed vulnerability fix. Evidence supports a Merkle shred layout and signing-input change. Evidence does not prove exploitability of the old truncated-root design. Evidence does not show invalid shreds reaching state-changing behavior. Evidence does not justify keeping this as a confirmed security corpus item. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-commitment-hardening`
Final impact type: `cryptographic-integrity-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, cryptography, signature, merkle-proof, commitment-binding, serialization-layout`

The supplied evidence does not prove a concrete exploitable vulnerability, forgery, replay, or bypass, so this should not be treated as a confirmed security fix. However, the commit and patch clearly change security-sensitive cryptographic commitment handling: signatures move from data involving a truncated Merkle root to `SignedData::MerkleRoot` over the full root, and proof/root handling is simplified so signature verification is described as covering the Merkle proof relationship. That supports retaining it as security hardening with conservative metadata.

## Security Evidence

1. Commit message says signatures are now over the full 32-byte hash instead of a truncated Merkle root.
2. Tests now expect signed data to be `SignedData::MerkleRoot(merkle_root)` and verify the signature over that value.
3. Patch removes serialized root-plus-proof branch parsing and changes Merkle handling to proof-only data.
4. Commit message states signature verification now effectively verifies the Merkle proof, removing separate sanitize proof verification.

## Missing Evidence

1. No evidence shows a practical forgery against the prior truncated-root design.
2. No evidence shows replay, request forgery, or accepted invalid shreds in production behavior.
3. No exploit path or attacker-controlled state transition is demonstrated.
4. The commit also has capacity and serialization-layout motivations, so security intent is not exclusive.

## Claim Boundaries

1. Classify as hardening of cryptographic commitment/signature binding, not as a proven vulnerability fix.
2. Do not claim confirmed replay prevention or request-forgery impact.
3. Do not claim the old sanitize implementation was bypassable from the supplied patch alone.
4. Do not retain misleading database-oriented tagging.
