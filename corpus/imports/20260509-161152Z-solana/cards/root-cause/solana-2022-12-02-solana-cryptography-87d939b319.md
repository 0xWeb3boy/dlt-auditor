# Root-Cause Card

## Metadata

- ID: `solana-2022-12-02-solana-cryptography-87d939b319`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-cryptographic-key-derivation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach consensus, accounting, or authorization-sensitive state.

## Trust Boundary

- Boundary: untrusted external input to protocol enforcement layer

## Attack Surface

- Entrypoint type: protocol input or state-transition entrypoint
- Sensitive sink: consensus, accounting, or authorization-sensitive state

## Root Cause

The root cause was inconsistent public-key derivation across ElGamal key construction paths. The canonical helper and scalar-based key generation used different formulas, which could produce keypairs that did not satisfy the expected private/public relation for proof generation and verification.

## Impact Pattern

- Primary impact: cryptographic-integrity
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch fixes inconsistent ElGamal public-key derivation in the zk-token SDK. Before the change, `ElGamalPubkey::new` derived the public key as `secret * H`, while `keygen_with_scalar` used `secret.invert() * H`. After the change, `ElGamalPubkey::new` asserts the scalar is nonzero and uses `s.invert() * H`, and `keygen_with_scalar` delegates to that helper. The accompanying `pubkey_proof.rs` changes add test coverage for derived keypairs; they do not...
