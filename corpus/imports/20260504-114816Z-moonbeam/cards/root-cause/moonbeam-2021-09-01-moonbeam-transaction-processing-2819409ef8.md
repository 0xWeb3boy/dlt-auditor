# Root-Cause Card

## Metadata

- ID: `moonbeam-2021-09-01-moonbeam-transaction-processing-2819409ef8`
- Bug family: `resource_accounting_and_limits`
- Bug class: `fee-accounting-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fee-accounting-consistency`

## Violated Invariant

- Invariant: All transaction execution paths that consume block resources must route their fees through the same canonical accounting and distribution policy.

## Trust Boundary

- Boundary: EVM transaction execution crosses into runtime currency imbalance handling and treasury/burn accounting.

## Attack Surface

- Entrypoint type: evm-transaction-fee-hook
- Sensitive sink: transaction fee imbalance burn/treasury distribution

## Impact Pattern

- Primary impact: fee-bypass
- Secondary impact: economic-accounting, treasury-accounting

## Short Reusable Lesson

- The EVM runtime configuration used a no-op fee hook while Substrate transactions used DealWithFees. The fix wires EVMCurrencyAdapter and adds the EVM callback for nonzero imbalances. Attach the EVM execution path to the same currency adapter and burn/treasury imbalance policy used by native transactions.
