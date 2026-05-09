# Root-Cause Card

## Metadata

- ID: `nibiru-2024-10-24-nibiru-rpc-client-api-dd27f4b6`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-gas-resource-control-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `bounded helper-call gas and revert isolation`

## Violated Invariant

- Invariant: System-mediated contract calls must run under a predictable gas cap and must not commit intermediate state when the contract reverts or errors.

## Trust Boundary

- Boundary: Native keeper helper crosses into attacker-supplied ERC20 contract code.

## Attack Surface

- Entrypoint type: keeper-initiated EVM contract helper call
- Sensitive sink: EVM execution with gas consumption and cached-context commit behavior

## Impact Pattern

- Primary impact: resource exhaustion hardening
- Secondary impact: state isolation on failed helper calls

## Short Reusable Lesson

- A native helper that calls arbitrary contract code was changed to use a fixed gas cap and cached execution context so reverts do not leak state.
