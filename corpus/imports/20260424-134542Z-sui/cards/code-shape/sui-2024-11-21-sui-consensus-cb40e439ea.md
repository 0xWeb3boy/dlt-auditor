# Code-Shape Card

## Metadata

- ID: `sui-2024-11-21-sui-consensus-cb40e439ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-limit-accounting`

## Code Shape Summary

- The patch fixes a consensus block-construction accounting bug. The transaction consumer now checks aggregate block bytes and selected-plus-incoming transaction count before accepting a transaction batch, aligning proposal behavior with verifier-side protocol limits.

## Search Motifs

- resource-accounting enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Align producer-side limit accounting with verifier-side protocol validation by checking the post-addition block state before accepting a transaction batch.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
