# Validation Card

## Metadata

- ID: `nibiru-2025-01-06-nibiru-transaction-processing-350b9e97`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-undercharge`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: transaction gas meter charge for storage-heavy bank side effects.
- Evidence 2: The validated finding ties the change to this invariant: A wrapper that charges gas for delegated state operations must measure the real operation cost, not a discounted or zero-cost substitute context.

## What Could Have Invalidated It

- Compensating control 1: Do not flag test-only gas meters
- Compensating control 2: InfiniteGasMeter can be correct when used only to avoid double charging while preserving store gas configs

## Severity Guidance

- Expected impact band: `resource_control`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `confirmed` and `security-hardening`.
- Caution 2: The undercharge is confirmed and affects resource fairness, but the record does not prove a chain halt or direct economic theft.
