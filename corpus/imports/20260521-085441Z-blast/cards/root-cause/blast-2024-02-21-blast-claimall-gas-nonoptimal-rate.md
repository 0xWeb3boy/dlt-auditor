# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-claimall-gas-nonoptimal-rate`
- Bug family: `resource_accounting_and_limits`
- Bug class: `claim-helper-nonoptimal-payout`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `claim-curve-optimality`

## Violated Invariant

- Invariant: Convenience claim helpers should not force a lower payout than an equivalent sequence of allowed split claims over the same balance and maturity state.

## Trust Boundary

- Boundary: authorized gas governor -> Gas predeploy claim curve

## Attack Surface

- Entrypoint type: claimAllGas or claimMaxGas helper
- Sensitive sink: claimable gas payout and retained seconds accounting

## Impact Pattern

- Primary impact: fee-bypass
- Secondary impact: value-miscalculation

## Short Reusable Lesson

- Convenience claim helpers should not force a lower payout than an equivalent sequence of allowed split claims over the same balance and maturity state. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
