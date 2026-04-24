# Code-Shape Card

## Metadata

- ID: `reth-2023-04-11-reth-transaction-processing-e0e449d5f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-input-validation`

## Code Shape Summary

- The legacy signature decode path derived `odd_y_parity` from the raw `v` value without first enforcing the Ethereum legacy constraint that `v` must be exactly `27` or `28`. That allowed non-canonical legacy-branch inputs to be normalized instead of rejected at parse time.

## Search Motifs

- signature recovery accepts non-canonical v/s values or exposes unchecked recovery in validation paths
- search for `27` call sites that derive, cache, or validate security-sensitive state
- search for `28` call sites that derive, cache, or validate security-sensitive state
- search for `odd_y_parity` call sites that derive, cache, or validate security-sensitive state
- signature-input-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses externally supplied transaction bytes -> signer recovery, but signature-field-validation is incomplete before the code updates or relies on authenticated transaction sender identity.

## Patch Pattern

- Add explicit canonical-value validation at the decode boundary for signature metadata and fail closed on malformed encodings instead of normalizing them.

## False Match Warnings

- No proof that malformed legacy v values were accepted into execution or consensus-critical flows
- No test or report showing signature forgery, replay, chain split, or sender-recovery abuse
- No downstream evidence that noncanonical values changed authorization or transaction acceptance semantics
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
