# Validation Card

## Metadata

- ID: `nitro-2023-11-21-nitro-core-logic-995df9e00`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `error-handling-policy`

## What Confirmed The Issue

- Evidence 1: The patch changes the prover VM's error-guard behavior from implicitly recovering whenever a guard frame exists to recovering only when an explicit `enabled` policy bit is set.
- Evidence 2: Add explicit policy state for recovery behavior and enforce it at the decision point instead of inferring permission from leftover internal state.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
