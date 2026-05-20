# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m04-cumulative-gas-refund`
- Bug family: `resource_accounting_and_limits`
- Bug class: `cumulative-gas-refund-miscalculation`

## What Confirmed The Issue

- Public C4 report section M-04 rated this as Medium.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if fee deduction is explicitly based on the same aggregate batch gas unit.
- No issue if only one EVM message can exist per transaction.

## Severity Guidance

- Expected impact band: under-refunded gas fees
- Expected severity band: medium

## False-Positive Cautions

- No issue if fee deduction is explicitly based on the same aggregate batch gas unit.
- No issue if only one EVM message can exist per transaction.
- No issue if cumulative gas is never used in per-message refund math.
