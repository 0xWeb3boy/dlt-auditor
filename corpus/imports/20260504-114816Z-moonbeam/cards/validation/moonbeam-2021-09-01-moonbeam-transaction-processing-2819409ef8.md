# Validation Card

## Metadata

- ID: `moonbeam-2021-09-01-moonbeam-transaction-processing-2819409ef8`
- Bug family: `resource_accounting_and_limits`
- Bug class: `fee-accounting-mismatch`

## What Confirmed The Issue

- Moonriver EVM OnChargeTransaction changed from unit to EVMCurrencyAdapter.
- DealWithFees gained an EVM-facing nonzero imbalance handler mirroring the existing fee split.

## What Could Have Invalidated It

- Evidence that pallet_evm already charged and distributed fees through another mandatory path
- A chain policy intentionally allowing fee-free Ethereum transactions

## Severity Guidance

- Expected impact band: resource_accounting_or_fee_integrity
- Expected severity band: medium

## False-Positive Cautions

- A no-op hook may be safe in tests or fee-free dev networks
- Fees may be charged earlier by a separate mandatory adapter
