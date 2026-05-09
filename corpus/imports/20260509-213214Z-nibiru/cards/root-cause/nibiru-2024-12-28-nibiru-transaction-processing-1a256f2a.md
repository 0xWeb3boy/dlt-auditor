# Root-Cause Card

## Metadata

- ID: `nibiru-2024-12-28-nibiru-transaction-processing-1a256f2a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursive-gas-forwarding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `recursive gas forwarding bound`

## Violated Invariant

- Invariant: Nested contract calls made by protocol helpers must forward gas from the transaction remaining budget, not grant each recursive call a fresh fixed allowance.

## Trust Boundary

- Boundary: Protocol ERC20 helper crosses into user-controlled token code that can recurse back into precompiles.

## Attack Surface

- Entrypoint type: FunToken/ERC20 mint or burn helper call
- Sensitive sink: recursive CallContract execution and transaction gas meter

## Impact Pattern

- Primary impact: recursive resource exhaustion
- Secondary impact: transaction failure or degraded liveness

## Short Reusable Lesson

- A recursive ERC20/precompile path now computes forwarded call gas from remaining transaction gas with a 63/64-style cap instead of passing a fresh fixed limit.
