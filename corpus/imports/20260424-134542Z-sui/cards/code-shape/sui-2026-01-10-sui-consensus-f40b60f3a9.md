# Code-Shape Card

## Metadata

- ID: `sui-2026-01-10-sui-consensus-f40b60f3a9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-finalization-hardening`

## Code Shape Summary

- The patch changes consensus finalization logic so transactions in blocks below the leader-derived GC bound are not directly finalized based only on commit evidence.

## Search Motifs

- state-transition-invariant enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Make finalization conservative when quorum-vote inference depends on transaction votes that may have been omitted due to garbage collection.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
