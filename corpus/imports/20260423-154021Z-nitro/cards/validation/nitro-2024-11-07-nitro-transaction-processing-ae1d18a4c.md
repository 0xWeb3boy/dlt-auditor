# Validation Card

## Metadata

- ID: `nitro-2024-11-07-nitro-transaction-processing-ae1d18a4c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-proof-generation-hardening`

## What Confirmed The Issue

- Evidence 1: The evidence supports a correctness fix in BoLD challenge handling: virtual-range block challenges were previously handled with a boolean shortcut that did not provide the concrete finished state to use, and the commit message says this could lead to looking up a block index for which no real block existed and producing incorrect inclusion proofs.
- Evidence 2: Replace a boolean boundary-case shortcut with an API that returns the concrete fallback state, and use that state at each proof/hash generation entry point.

## What Could Have Invalidated It

- Compensating control 1: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
- Compensating control 2: If the edge case only affects unreachable dispute states, downgrade similar patterns.

## Severity Guidance

- Expected impact band: `proof_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
- Caution 2: Do not claim profitable challenge manipulation without evidence that the malformed proof or edge can actually be submitted or accepted.
