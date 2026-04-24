# Code-Shape Card

## Metadata

- ID: `sui-2022-10-13-sui-storage-f4ea3fc5f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-state-confusion`

## Code Shape Summary

- The patch addresses a stale-epoch certificate handling bug in Sui authority/node-sync storage. The supplied evidence supports a correctness and state-integrity fix around epoch transitions, but does not establish an exploitable vulnerability or a concrete protocol security failure.

## Search Motifs

- state-transition-invariant enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Separate epoch-scoped state from perpetual state, use epoch-aware certificate lookup, and place consensus certificates into the pending-execution path instead of relying on certificate persistence alone.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
