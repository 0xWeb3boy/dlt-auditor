# Root-Cause Card

## Metadata

- ID: `solana-2023-02-15-solana-cryptography-cf0a149add`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-commitment-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The prior design embedded Merkle root material in the shred binary and represented Merkle branch bytes as root plus proof. The commit says this caused signatures to be over a truncated root rather than the full 32-byte hash. The provided evidence does not show that this was exploitable or that invalid proofs could be accepted in practice.

## Impact Pattern

- Primary impact: cryptographic-integrity-hardening
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch removes the embedded Merkle root from serialized Merkle shred branch data, changes proof handling from root-plus-proof branches to proof-only data, and updates tests so signed data resolves to `SignedData::MerkleRoot`. This is plausibly security relevant because it changes cryptographic commitment handling, but the evidence does not prove a vulnerability in the previous behavior. Treat as unclear hardening/layout work rather than a validated s...
