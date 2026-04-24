# Code-Shape Card

## Metadata

- ID: `sui-2023-02-27-sui-cryptography-d009e82fa3`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-domain-separation`

## Code Shape Summary

- The patch changes authority signature construction, verification, and batch verification to include an explicit intent scope by signing/verifying serialized `IntentMessage<T>` values.

## Search Motifs

- signature-canonicalization enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- alternate signed encodings accepted as equivalent
- missing epoch/domain/payload binding in verifier

## Typical Asymmetry

- The producer can vary signed bytes or context while the verifier accidentally treats distinct security domains as equivalent.

## Patch Pattern

- Add cryptographic domain separation by signing a structured intent-scoped envelope instead of only the raw protocol payload bytes.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The alternative encoding cannot be produced by an untrusted party or is normalized before verification.
