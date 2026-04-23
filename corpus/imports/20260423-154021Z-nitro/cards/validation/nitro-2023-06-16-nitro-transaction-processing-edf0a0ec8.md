# Validation Card

## Metadata

- ID: `nitro-2023-06-16-nitro-transaction-processing-edf0a0ec8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-challenge-metadata`

## What Confirmed The Issue

- Evidence 1: The evidence supports a challenge-initiation correctness bug, not a clearly established vulnerability.
- Evidence 2: Replace indirectly inferred or parent-derived state with authoritative creation metadata from the challenged assertion when building challenge-sensitive inputs.

## What Could Have Invalidated It

- Compensating control 1: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
- Compensating control 2: If the edge case only affects unreachable dispute states, downgrade similar patterns.

## Severity Guidance

- Expected impact band: `proof_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
- Caution 2: Do not claim profitable challenge manipulation without evidence that the malformed proof or edge can actually be submitted or accepted.
