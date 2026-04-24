# Code-Shape Card

## Metadata

- ID: `reth-2023-11-29-reth-transaction-processing-2c5a748c5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-malleability`

## Code Shape Summary

- The `Signature` API did not explicitly separate EIP-2-compliant signer recovery from legacy-compatible recovery, leaving the low-s invariant implicit rather than enforced at a clearly named checked boundary.

## Search Motifs

- signature recovery accepts non-canonical v/s values or exposes unchecked recovery in validation paths
- search for `recover_signer` call sites that derive, cache, or validate security-sensitive state
- search for `recover_signer_unchecked` call sites that derive, cache, or validate security-sensitive state
- search for `Signature` call sites that derive, cache, or validate security-sensitive state
- signature-malleability fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses externally supplied transaction bytes -> signer recovery, but canonical-signature-enforcement is incomplete before the code updates or relies on authenticated transaction sender identity.

## Patch Pattern

- Split a compatibility-oriented helper from the validation-oriented API, and make the validation path enforce the protocol invariant explicitly with a local guard and regression test.

## False Match Warnings

- No caller-side diff is shown proving validation paths were switched to the checked API
- No evidence shows previously accepted high-s signatures could reach canonical processing after EIP-2 rules should apply
- No proof of a concrete exploit, replay, consensus failure, or externally reachable vulnerability is provided
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
