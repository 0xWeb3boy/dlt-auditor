# Validation Card

## Metadata

- ID: `moonbeam-2023-01-19-moonbeam-transaction-processing-b133edf7fd`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-hardening`

## What Confirmed The Issue

- request_gas_limit_with_overhead uses checked_add.
- Fulfillment path adds max_prepare_and_finish_fulfillment_cost remaining-gas rejection.

## What Could Have Invalidated It

- EVM host metering already charges the same overhead before this code runs
- Downstream subcalls cannot be reached when gas is insufficient

## Severity Guidance

- Expected impact band: resource_accounting_or_dos
- Expected severity band: medium

## False-Positive Cautions

- Gas checks are less security-critical if all downstream work is separately metered and atomic
- Overflow-safe types alone do not prove exploitable undercharging
