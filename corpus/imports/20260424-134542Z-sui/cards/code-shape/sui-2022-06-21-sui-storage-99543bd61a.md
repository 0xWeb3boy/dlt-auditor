# Code-Shape Card

## Metadata

- ID: `sui-2022-06-21-sui-storage-99543bd61a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `non-finalized-state-retention`

## Code Shape Summary

- The patch fixes a missing rollback in Sui epoch finalization. Before the change, `finish_epoch_change` detected non-empty `checkpoints.extra_transactions` but only had a deferred guard for reverting them.

## Search Motifs

- input-validation enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The storage sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Replace detection-only handling of non-finalized epoch state with explicit rollback of each recorded extra transaction before completing epoch finalization.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
