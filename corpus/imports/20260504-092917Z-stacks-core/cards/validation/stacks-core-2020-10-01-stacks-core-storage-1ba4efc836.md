# Validation Card

## Metadata

- ID: `stacks-core-2020-10-01-stacks-core-storage-1ba4efc836`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `delegated-stacking-validation`

## What Confirmed The Issue

- Evidence 1: In `src/vm/functions/special.rs`, the patch replaces `// sender is required` with `match parse_pox_stacking_result(value) {`.
- Evidence 2: In `src/chainstate/stacks/boot/contract_tests.rs`, the patch adds `CheckErrors, Error, IncomparableError, InterpreterError, InterpreterResult as Result,`.

## What Could Have Invalidated It

- Compensating control 1: The constructor may be used only with trusted constants.
- Compensating control 2: The changed path may improve diagnostics without changing acceptance behavior.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The constructor may be used only with trusted constants.
- Caution 2: The changed path may improve diagnostics without changing acceptance behavior.
