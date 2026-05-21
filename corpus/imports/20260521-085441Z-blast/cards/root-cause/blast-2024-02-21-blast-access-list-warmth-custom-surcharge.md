# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-access-list-warmth-custom-surcharge`
- Bug family: `resource_accounting_and_limits`
- Bug class: `access-list-custom-gas-incompatibility`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `access-list-warmth-parity`

## Violated Invariant

- Invariant: If an access list prewarms a target for EVM gas semantics, Blast-specific custom gas should not reintroduce an unpriced cold-style failure mode for the same target class.

## Trust Boundary

- Boundary: transaction access list -> CALL-family gas calculation

## Attack Surface

- Entrypoint type: EIP-2930 or EIP-1559 transaction with access list
- Sensitive sink: CALL dynamic gas and OOG behavior

## Impact Pattern

- Primary impact: compatibility-break
- Secondary impact: denial-of-service

## Short Reusable Lesson

- If an access list prewarms a target for EVM gas semantics, Blast-specific custom gas should not reintroduce an unpriced cold-style failure mode for the same target class. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
