# Validation Card

## Metadata

- ID: `nitro-2022-03-17-nitro-transaction-processing-c4a31f084`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reorg-state-mismatch`

## What Confirmed The Issue

- Evidence 1: This patch is best supported as security hardening in validator reorg handling.
- Evidence 2: Persist the chain identity hash alongside the progress index, then fail closed whenever resumed or derived validator state does not match the live canonical chain.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
