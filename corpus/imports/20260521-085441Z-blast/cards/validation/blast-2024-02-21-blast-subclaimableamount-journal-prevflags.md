# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-subclaimableamount-journal-prevflags`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `incomplete-journal-rollback`

## What Confirmed The Issue

- The competition report identifies this as `H-08` with `high` severity.
- The affected surface is specific: execution-client-state-journal at `StateDB balanceValuesChange rollback`.
- The missing property can be stated as `rollback-atomicity` and the trigger crosses `authorized yield claim -> EVM revert journal`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: state-integrity, unauthorized-value-shift
- Expected severity band: high

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
