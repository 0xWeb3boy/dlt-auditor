# Validation Card

## Metadata

- ID: `moonbeam-2025-05-13-moonbeam-transaction-processing-ac666695ee`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-resource-accounting-and-reentrancy-hardening`

## What Confirmed The Issue

- runtime/common/src/apis.rs now builds pallet_ethereum::TransactionData.
- pallet_ethereum dependency enables forbid-evm-reentrancy.

## What Could Have Invalidated It

- The manual estimate was proven equivalent to the canonical transaction representation
- The paths are read-only and cannot influence admitted transaction accounting

## Severity Guidance

- Expected impact band: resource_accounting_or_reentrancy_hardening
- Expected severity band: medium

## False-Positive Cautions

- Manual estimation may be safe if covered by exact tests against canonical encoding
- RPC simulation-only undercharging may not affect block production
