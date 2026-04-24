# Code-Shape Card

## Metadata

- ID: `sui-2022-07-20-sui-storage-ede61fb385`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `authenticated-epoch-storage-hardening`

## Code Shape Summary

- The patch appears to add an authenticated/signed epoch storage path and adjust epoch reconfiguration bookkeeping, but the evidence does not establish a vulnerability.

## Search Motifs

- authorization enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Replace plain local epoch metadata insertion with a signed/authenticated epoch persistence API, while threading checkpoint context through the transition path.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A later mandatory ownership or capability check rejects the request before any state change.
