# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-high-frame-precompile-surcharge-repeat`
- Bug family: `resource_accounting_and_limits`
- Bug class: `custom-surcharge-wrong-participant-key`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `one-time-surcharge-binding`

## Violated Invariant

- Invariant: A storage-style first-use surcharge should be charged once for a participant that creates gas-accounting state, not repeatedly for targets that never receive allocations.

## Trust Boundary

- Boundary: EVM call graph -> Blast high-frame surcharge

## Attack Surface

- Entrypoint type: CALL-family opcode after frame threshold targeting precompiles
- Sensitive sink: transaction gas charge and GasTracker allocation

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: fee-miscalculation

## Short Reusable Lesson

- A storage-style first-use surcharge should be charged once for a participant that creates gas-accounting state, not repeatedly for targets that never receive allocations. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
