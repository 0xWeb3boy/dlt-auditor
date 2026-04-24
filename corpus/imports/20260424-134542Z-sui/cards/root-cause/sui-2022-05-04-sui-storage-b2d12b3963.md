# Root-Cause Card

## Metadata

- ID: `sui-2022-05-04-sui-storage-b2d12b3963`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-metering-inconsistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Every state transition that consumes resources or changes balances must update the corresponding accounting state exactly once and within protocol bounds.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: committing fees, balances, or resource accounting state

## Impact Pattern

- Primary impact: resource-accounting
- Secondary impact: economic-integrity

## Short Reusable Lesson

- Shared validator resources need bounded accounting and attribution before untrusted work can be amplified. The supported finding is a likely gas-metering consistency fix. The clearest evidence is that `transaction_input_checker.rs::check_locks` now sums the gas-metered sizes of all checked input objects and calls `gas_status.charge_storage_read(total_size)?` before returning them.
