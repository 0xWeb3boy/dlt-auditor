# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-h04-failed-precompile-gas-bypass`
- Bug family: `resource_accounting_and_limits`
- Bug class: `failed-precompile-gas-undercharge`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `failure-path resource accounting`

## Violated Invariant

- Invariant: Precompile gas charged to the EVM caller must include work consumed by the local/cache context even when the precompile returns an error.

## Trust Boundary

- Boundary: EVM caller->native precompile execution

## Attack Surface

- Entrypoint type: precompile method call
- Sensitive sink: contract gas meter and cached Cosmos gas consumed by FunToken, Wasm, and Oracle precompiles

## Impact Pattern

- Primary impact: undercharged failed precompile work
- Secondary impact: resource-exhaustion DoS

## Short Reusable Lesson

- Precompile handlers returned immediately on err and only called contract.UseGas after the success path.
