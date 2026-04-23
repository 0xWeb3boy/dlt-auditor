# Validation Card

## Metadata

- ID: `nitro-2023-11-15-nitro-transaction-processing-4b8676d77`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-index-derivation`

## What Confirmed The Issue

- Evidence 1: The supplied diff supports a correctness fix in the staker state-provider path: proof and machine-hash lookups now derive the message index from batch metadata, equal-batch ranges are rejected, and missing batch-count data is surfaced as a catch-up condition.
- Evidence 2: Replace direct or ambiguous index inputs with indices derived from authoritative batch metadata, add stricter argument validation, and translate sync-lag conditions into an explicit error.

## What Could Have Invalidated It

- Compensating control 1: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
- Compensating control 2: If the edge case only affects unreachable dispute states, downgrade similar patterns.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
- Caution 2: Do not claim profitable challenge manipulation without evidence that the malformed proof or edge can actually be submitted or accepted.
