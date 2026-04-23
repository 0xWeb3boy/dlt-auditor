# Validation Card

## Metadata

- ID: `nitro-2022-02-17-nitro-transaction-processing-8ad394df3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-boundary-validation`

## What Confirmed The Issue

- Evidence 1: The patch fixes correctness bugs in validator challenge setup and machine initialization around genesis-relative indexing and boundary handling.
- Evidence 2: Thread canonical genesis context through challenge construction, handle valid boundary special cases explicitly, and add fail-closed checks before deriving machine state from challenge metadata.

## What Could Have Invalidated It

- Compensating control 1: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
- Compensating control 2: If the edge case only affects unreachable dispute states, downgrade similar patterns.

## Severity Guidance

- Expected impact band: `proof_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
- Caution 2: Do not claim profitable challenge manipulation without evidence that the malformed proof or edge can actually be submitted or accepted.
