# Code-Shape Card

## Metadata

- ID: `sui-2025-11-26-sui-consensus-3b59b5be60`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-accounting-hardening`

## Code Shape Summary

- The patch is a consensus vote-accounting fix for Mysticeti fastpath finalization under garbage collection. It adds a guard that skips counting votes from a block when a same-author origin ancestor above the pending block round is missing from the retained block map and may have been GC'ed.

## Search Motifs

- resource-accounting enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Add a conservative GC-aware vote-accounting guard before aggregating accept votes when retained ancestry is incomplete.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
