# Validation Card

## Metadata

- ID: `nitro-2022-03-17-nitro-storage-368fbe57c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-validation`

## What Confirmed The Issue

- Evidence 1: The visible patch adds fail-fast validation in the validator startup path, including configuration sanity checks and a runtime WASM module-root comparison.
- Evidence 2: Add fail-fast startup validation for critical configuration dependencies and verify that the runtime-loaded validator artifact matches the expected configured identity.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
