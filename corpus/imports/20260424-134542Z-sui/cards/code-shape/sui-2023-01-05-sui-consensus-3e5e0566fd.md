# Code-Shape Card

## Metadata

- ID: `sui-2023-01-05-sui-consensus-3e5e0566fd`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-user-signature-verification`

## Code Shape Summary

- The patch is likely a security fix for Sui consensus certificate validation. The commit message explicitly says an unresolved deferred guard after unpinning user signatures allowed validators to submit certificates with incorrect user signatures. The supplied code evidence shows new regression support that corrupts `cert.

## Search Motifs

- signature-verification enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- alternate signed encodings accepted as equivalent
- missing epoch/domain/payload binding in verifier

## Typical Asymmetry

- The producer can vary signed bytes or context while the verifier accidentally treats distinct security domains as equivalent.

## Patch Pattern

- Verify embedded user transaction signatures during consensus certificate-message validation, and add regression coverage that submits otherwise well-formed certificates with deliberately corrupted user signatures.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The alternative encoding cannot be produced by an untrusted party or is normalized before verification.
- The value is only advisory and is recomputed from canonical local consensus state before use.
