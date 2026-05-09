# Validation Card

## Metadata

- ID: `nibiru-2025-01-26-nibiru-staking-3f5be387`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-runtime-state-sync`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: EVM StateDB account cache for sender and module account balances.
- Evidence 2: The validated finding ties the change to this invariant: When native module operations move balances visible to another runtime, both runtimes must observe the same balances before execution continues.

## What Could Have Invalidated It

- Compensating control 1: Do not flag transfers of denoms not mirrored into the foreign runtime
- Compensating control 2: Need subsequent runtime visibility or cache dependence

## Severity Guidance

- Expected impact band: `state_integrity`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Stale mirrored balances can enable dirty-state behavior across runtimes, though concrete theft or permanent loss was not proven.
