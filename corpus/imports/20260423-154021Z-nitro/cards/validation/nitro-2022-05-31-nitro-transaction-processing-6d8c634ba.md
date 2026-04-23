# Validation Card

## Metadata

- ID: `nitro-2022-05-31-nitro-transaction-processing-6d8c634ba`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-initialization-validation`

## What Confirmed The Issue

- Evidence 1: The provided evidence shows a configuration-binding fix: the code now carries `genesisBlockNum` through chain-config selection and checks it against the init message during startup.
- Evidence 2: Add the missing identity field to configuration handling, thread it through config lookup paths, and reject mismatches during initialization.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
