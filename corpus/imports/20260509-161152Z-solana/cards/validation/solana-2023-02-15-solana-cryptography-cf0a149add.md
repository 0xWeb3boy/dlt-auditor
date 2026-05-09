# Validation Card

## Metadata

- ID: `solana-2023-02-15-solana-cryptography-cf0a149add`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-commitment-hardening`

## What Confirmed The Issue

- Commit message says signatures are now over the full 32-byte hash instead of a truncated Merkle root.
- Tests now expect signed data to be `SignedData::MerkleRoot(merkle_root)` and verify the signature over that value.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
