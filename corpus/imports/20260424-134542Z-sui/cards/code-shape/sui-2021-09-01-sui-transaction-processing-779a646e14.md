# Code-Shape Card

## Metadata

- ID: `sui-2021-09-01-sui-transaction-processing-779a646e14`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-hardening`

## Code Shape Summary

- Commit 779a646e14 changes FastPay signature material from a hand-written Digestible/Sha512 path for Transfer to a Signable/BcsSignable path described as serde plus BCS canonical bytes. It also updates observed signature creation paths to sign value.transfer or certificate.value.transfer.

## Search Motifs

- signature-canonicalization enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- alternate signed encodings accepted as equivalent
- missing epoch/domain/payload binding in verifier

## Typical Asymmetry

- The producer can vary signed bytes or context while the verifier accidentally treats distinct security domains as equivalent.

## Patch Pattern

- Replace ad hoc signature digest construction with a canonical serialization-backed signing interface and align signature creation call sites on the intended Transfer payload.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The alternative encoding cannot be produced by an untrusted party or is normalized before verification.
