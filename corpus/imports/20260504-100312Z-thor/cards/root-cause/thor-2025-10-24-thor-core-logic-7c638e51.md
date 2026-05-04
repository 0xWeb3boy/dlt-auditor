# Root-Cause Card

## Metadata

- ID: `thor-2025-10-24-thor-core-logic-7c638e51`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `unchecked-numeric-conversion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic-bounds`

## Violated Invariant

- Invariant: Externally supplied staking amounts and contract balances must be converted into internal accounting units only after checking conversion errors and bounds.

## Trust Boundary

- Boundary: `contract-caller->native-staking-accounting`

## Attack Surface

- Entrypoint type: `native-contract-staking-handler`
- Sensitive sink: stake increase/decrease, delegation creation, and staker contract balance reconciliation
- Attacker capability: Submit native staking calls with large or boundary-value amount fields.
- Preconditions: The conversion routine can fail or overflow for some supplied values.

## Impact Pattern

- Primary impact: staking/accounting state integrity
- Secondary impact: validator accounting consistency
- Blast radius: `chain-wide`

## Short Reusable Lesson

- Consensus state transitions should never inline fallible numeric conversions into state-mutating calls; conversion and bounds errors must be handled before accounting state is touched.
