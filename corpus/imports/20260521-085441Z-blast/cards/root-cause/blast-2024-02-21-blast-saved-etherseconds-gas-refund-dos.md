# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-saved-etherseconds-gas-refund-dos`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-refund-maturity-reuse`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Gas refund maturity should be consumed when the corresponding gas balance is claimed so old seconds cannot subsidize future block-stuffing work.

## Trust Boundary

- Boundary: user transaction -> Blast gas-refund accounting

## Attack Surface

- Entrypoint type: gas-claim path and post-transaction gas allocation
- Sensitive sink: Gas predeploy etherBalance and etherSeconds state

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: fee-bypass

## Short Reusable Lesson

- Gas refund maturity should be consumed when the corresponding gas balance is claimed so old seconds cannot subsidize future block-stuffing work. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
