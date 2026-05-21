# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-eth-yield-token-decimal-conversion`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-domain-unit-conversion-mismatch`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `unit-consistency`

## Violated Invariant

- Invariant: The value sent through a portal and the amount encoded for the L2 finalizer must use the same decimal unit and equality expectation.

## Trust Boundary

- Boundary: L1 ERC20 deposit amount -> L2 native ETH finalizer

## Attack Surface

- Entrypoint type: bridgeERC20To with approved non-18-decimal ETH-yield token
- Sensitive sink: portal msg.value and L2 finalizeBridgeETHDirect equality check

## Impact Pattern

- Primary impact: asset-stranding
- Secondary impact: cross-domain-accounting-error

## Short Reusable Lesson

- The value sent through a portal and the amount encoded for the L2 finalizer must use the same decimal unit and equality expectation. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
