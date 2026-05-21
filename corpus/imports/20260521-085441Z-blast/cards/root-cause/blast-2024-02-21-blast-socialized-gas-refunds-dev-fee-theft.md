# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-socialized-gas-refunds-dev-fee-theft`
- Bug family: `resource_accounting_and_limits`
- Bug class: `global-refund-socialization`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `refund-source-attribution`

## Violated Invariant

- Invariant: Gas refunds should reduce the claimable allocation of the contract that generated the refund, not proportionally reduce unrelated contracts touched in the same transaction.

## Trust Boundary

- Boundary: user-controlled EVM execution -> developer gas-fee distribution

## Attack Surface

- Entrypoint type: post-transaction GasTracker allocation
- Sensitive sink: per-contract claimable gas accounting

## Impact Pattern

- Primary impact: fee-bypass
- Secondary impact: unauthorized-value-shift

## Short Reusable Lesson

- Gas refunds should reduce the claimable allocation of the contract that generated the refund, not proportionally reduce unrelated contracts touched in the same transaction. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
