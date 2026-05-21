# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-direct-eth-yield-deposit-min-gas-bricking`
- Bug family: `resource_accounting_and_limits`
- Bug class: `bridge-direct-deposit-gas-budget`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `cross-domain-replay-and-gas-budgeting`

## Violated Invariant

- Invariant: Direct bridge deposits that bypass the messenger must still budget enough gas for finalization or provide an equivalent replay/refund path.

## Trust Boundary

- Boundary: L1 bridge deposit -> L2 value finalization

## Attack Surface

- Entrypoint type: L1 ETH-yield-token bridgeERC20/bridgeERC20To
- Sensitive sink: L2 direct ETH finalizer and recipient transfer

## Impact Pattern

- Primary impact: asset-stranding
- Secondary impact: denial-of-service

## Short Reusable Lesson

- Direct bridge deposits that bypass the messenger must still budget enough gas for finalization or provide an equivalent replay/refund path. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
