# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-subclaimableamount-journal-prevflags`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `incomplete-journal-rollback`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `rollback-atomicity`

## Violated Invariant

- Invariant: Every journal entry that mutates an account yield representation must restore flags, fixed balance, shares, and remainder together on revert.

## Trust Boundary

- Boundary: authorized yield claim -> EVM revert journal

## Attack Surface

- Entrypoint type: Blast claimYield/claimAllYield through native precompile
- Sensitive sink: StateDB balanceValuesChange rollback

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: unauthorized-value-shift

## Short Reusable Lesson

- Every journal entry that mutates an account yield representation must restore flags, fixed balance, shares, and remainder together on revert. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
