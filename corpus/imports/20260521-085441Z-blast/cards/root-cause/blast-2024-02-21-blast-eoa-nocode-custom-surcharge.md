# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-eoa-nocode-custom-surcharge`
- Bug family: `resource_accounting_and_limits`
- Bug class: `nocode-target-repeated-surcharge`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `made-progress-classification`

## Violated Invariant

- Invariant: First-use storage surcharges should be tied to targets that actually create gas-accounting storage work, not no-code/EOA targets that execute no code.

## Trust Boundary

- Boundary: EVM call graph -> Blast high-frame surcharge

## Attack Surface

- Entrypoint type: CALL/STATICCALL/CALLCODE/DELEGATECALL to EOA or empty-code target
- Sensitive sink: transaction gas charge and caller-side allocation

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: fee-miscalculation

## Short Reusable Lesson

- First-use storage surcharges should be tied to targets that actually create gas-accounting storage work, not no-code/EOA targets that execute no code. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
