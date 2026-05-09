# Validation Card

## Metadata

- ID: `nibiru-2024-05-17-nibiru-transaction-processing-dbbcfd60`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-validation`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: transaction conversion and ApplyEvmTx execution.
- Evidence 2: The validated finding ties the change to this invariant: A transaction message must satisfy its basic syntactic and semantic validation before it is converted into an execution object or passed to the state transition engine.

## What Could Have Invalidated It

- Compensating control 1: Do not flag if an earlier mandatory ante path always validates the same message
- Compensating control 2: Formatting-only gas changes are not evidence

## Severity Guidance

- Expected impact band: `transaction_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Missing entrypoint validation can expose parsing or execution assumptions, but the validated evidence did not show crash, replay, or consensus corruption.
