# Code-Shape Card

## Metadata

- ID: `sui-2023-01-09-sui-consensus-4c780d87db`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finality-rollback`

## Code Shape Summary

- The patch fixes an epoch-transition ordering bug where local rollback could revert a transaction that had already been executed through checkpoint processing. The evidence supports a consensus/finality integrity issue, but does not prove a remote exploit path, asset theft, signature bypass, or permanent chain-wide fork.

## Search Motifs

- state-transition-invariant enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Persist finalization evidence at checkpoint execution time, then consult that evidence before performing end-of-epoch rollback.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
