# Code-Shape Card

## Metadata

- ID: `sui-2022-07-29-sui-cryptography-5e06c90b39`
- Bug family: `authz_and_role_gates`
- Bug class: `epoch-authentication-invariant`

## Code Shape Summary

- The patch strengthens Sui epoch authentication checks by making signed and certified epoch verification reject records whose authentication epoch is not exactly the immediately previous epoch.

## Search Motifs

- authorization enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Make the cross-epoch authentication invariant explicit in verification and data modeling: store epoch-local committee data directly and reject signed or certified epoch records whose authentication epoch does not match the immediately previous epoch.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A later mandatory ownership or capability check rejects the request before any state change.
