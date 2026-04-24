# Code-Shape Card

## Metadata

- ID: `sui-2022-06-24-sui-transaction-processing-8a3d0789ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-execution-invariant`

## Code Shape Summary

- The patch adds explicit checkpoint/execution consistency checks in Sui checkpointing code, rejecting checkpoint contents that include unexecuted transactions.

## Search Motifs

- state-transition-invariant enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Add precondition guards at checkpoint state-transition boundaries to reject checkpoint contents that are not fully reflected in local execution state.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
