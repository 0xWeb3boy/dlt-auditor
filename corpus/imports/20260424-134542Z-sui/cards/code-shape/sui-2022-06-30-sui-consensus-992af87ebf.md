# Code-Shape Card

## Metadata

- ID: `sui-2022-06-30-sui-consensus-992af87ebf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `byzantine-availability-hardening`

## Code Shape Summary

- The patch is best characterized as Byzantine-availability hardening for Sui gossip node sync. It changes transaction/effects download from a direct request to the gossip peer into an AuthorityAggregator-mediated request that can accept one successful authenticated response with timeout handling.

## Search Motifs

- input-validation enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The consensus sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Replace a single-authority request for authenticated data with an aggregator-mediated multi-authority query that accepts one valid successful response and applies timeout handling.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
