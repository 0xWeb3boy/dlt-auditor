# Validation Card

## Metadata

- ID: `nitro-2024-02-05-nitro-core-logic-6b420cb12`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-state-check`

## What Confirmed The Issue

- Evidence 1: The supported finding is a business-logic guard addition: the patch teaches the assertion confirmation flow to stop when the target assertion is locally known to be challenged.
- Evidence 2: Add explicit state guards around a sensitive action, including re-checking after delay windows before issuing the final side effect.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
