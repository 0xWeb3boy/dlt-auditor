# Code-Shape Card

## Metadata

- ID: `solana-2020-08-06-solana-cryptography-5c4b8153c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-off-curve-address-validation`

## Code Shape Summary

The patch hardens Solana web3.js program-address derivation by adding an explicit ed25519 curve-membership rejection in `PublicKey.createProgramAddress`. The evidence supports a missing off-curve validation gate in the client helper, but does not establish a concrete exploit, known private key, replay issue, or runtime consensus vulnerability.

## Search Motifs

- search for missing off curve address validation checks near cryptography entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add invariant validation at the deterministic address-construction boundary and reject derived addresses that do not satisfy the off-curve requirement.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
