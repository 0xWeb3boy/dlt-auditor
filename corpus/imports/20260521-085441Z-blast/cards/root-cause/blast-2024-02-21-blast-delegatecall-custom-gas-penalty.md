# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-delegatecall-custom-gas-penalty`
- Bug family: `resource_accounting_and_limits`
- Bug class: `delegatecall-surcharge-identity-mismatch`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `execution-context-aware-metering`

## Violated Invariant

- Invariant: Custom first-use gas penalties should use the same identity for surcharge admission and fee allocation under delegatecall/callcode semantics.

## Trust Boundary

- Boundary: CALL-family opcode gas calculation -> GasTracker allocation

## Attack Surface

- Entrypoint type: DELEGATECALL or CALLCODE after frame threshold
- Sensitive sink: caller-context gas allocation and custom surcharge

## Impact Pattern

- Primary impact: fee-miscalculation
- Secondary impact: denial-of-service

## Short Reusable Lesson

- Custom first-use gas penalties should use the same identity for surcharge admission and fee allocation under delegatecall/callcode semantics. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
