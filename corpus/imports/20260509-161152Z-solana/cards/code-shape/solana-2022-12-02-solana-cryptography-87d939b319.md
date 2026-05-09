# Code-Shape Card

## Metadata

- ID: `solana-2022-12-02-solana-cryptography-87d939b319`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-cryptographic-key-derivation`

## Code Shape Summary

The patch fixes inconsistent ElGamal public-key derivation in the zk-token SDK. Before the change, `ElGamalPubkey::new` derived the public key as `secret * H`, while `keygen_with_scalar` used `secret.invert() * H`. After the change, `ElGamalPubkey::new` asserts the scalar is nonzero and uses `s.invert() * H`, and `keygen_with_scalar` delegates to that helper. The accompanying `pubkey_proof.rs` changes add test coverage for derived keypairs; they do not...

## Search Motifs

- search for incorrect cryptographic key derivation checks near cryptography entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where consensus, accounting, or authorization-sensitive state is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Centralize cryptographic key derivation in one helper, enforce the scalar precondition there, and route all keypair construction paths through that helper. Add focused proof tests for the affected key construction path.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
