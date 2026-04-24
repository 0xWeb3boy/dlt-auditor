# Code-Shape Card

## Metadata

- ID: `sui-2022-08-16-sui-cryptography-e65338451c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `empty-batch-signature-validation`

## Code Shape Summary

- The patch hardens Narwhal's batch signature verification paths by adding explicit rejection of empty signature batches in the generic `VerifyingKey` default and in Ed25519, BLS12-381, and BLS12-377 implementations.

## Search Motifs

- signature-verification enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- alternate signed encodings accepted as equivalent
- missing epoch/domain/payload binding in verifier

## Typical Asymmetry

- The producer can vary signed bytes or context while the verifier accidentally treats distinct security domains as equivalent.

## Patch Pattern

- Add an explicit non-empty-batch precondition at batch signature verification entry points, before curve-specific verification logic, while preserving key/signature count mismatch checks.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The alternative encoding cannot be produced by an untrusted party or is normalized before verification.
