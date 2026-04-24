# Code-Shape Card

## Metadata

- ID: `sui-2022-12-21-sui-consensus-bd9fbd18d3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-boundary-reconfiguration-race`

## Code Shape Summary

- The patch makes Sui validator certificate handling acquire and check the per-epoch reconfiguration read lock earlier, before certificate verification and later pending-consensus storage.

## Search Motifs

- state-transition-invariant enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Acquire the reconfiguration read lock at the certificate submission boundary, check the epoch acceptance state while holding it, and pass the lock requirement into the lower-level pending-consensus storage API.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
