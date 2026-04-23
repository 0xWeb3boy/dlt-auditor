# Validation Card

## Metadata

- ID: `nitro-2023-12-11-nitro-cryptography-1d3b655ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-state-commitment`

## What Confirmed The Issue

- Evidence 1: The strongest supported finding is a prover state-hash correctness fix: `Machine::hash` now commits the guard-enabled flag even when the guard stack is empty, and `ErrorGuardProof::hash_guards` no longer mixes that flag into the stack-hash helper.
- Evidence 2: Move mode or feature flags into the top-level state commitment and keep collection-hash helpers responsible only for collection contents.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
