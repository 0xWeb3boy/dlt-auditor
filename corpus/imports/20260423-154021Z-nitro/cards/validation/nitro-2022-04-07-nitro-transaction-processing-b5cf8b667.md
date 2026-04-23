# Validation Card

## Metadata

- ID: `nitro-2022-04-07-nitro-transaction-processing-b5cf8b667`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `module-root-mismatch`

## What Confirmed The Issue

- Evidence 1: The patch changes challenge-related machine loading so the validator can select a machine by module root instead of implicitly using the latest machine directory, and it adds an explicit module-root equality check before using the loaded machine.
- Evidence 2: Replace implicit default artifact selection with identifier-based selection, then add a fail-closed validation check at use time.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
