# Validation Card

## Metadata

- ID: `stacks-core-2024-04-20-stacks-core-storage-809c5fecc0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vm-error-propagation-transaction-validity`

## What Confirmed The Issue

- Evidence 1: In `clarity/src/vm/contexts.rs`, the patch replaces `Ok(value) => match value.clone().expect_result() {` with `Ok(value) => match value.clone().expect_result()? {`.
- Evidence 2: In `clarity/src/vm/contexts.rs`, the patch replaces `#[test]` with `/// Test the stx-transfer consolidation tx invalidation`.

## What Could Have Invalidated It

- Compensating control 1: The constructor may be used only with trusted constants.
- Compensating control 2: The changed path may improve diagnostics without changing acceptance behavior.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The constructor may be used only with trusted constants.
- Caution 2: The changed path may improve diagnostics without changing acceptance behavior.
