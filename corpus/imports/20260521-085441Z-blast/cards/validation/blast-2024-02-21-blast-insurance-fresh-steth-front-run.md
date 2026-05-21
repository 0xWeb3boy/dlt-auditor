# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-insurance-fresh-steth-front-run`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `loss-eligibility-snapshot-gap`

## What Confirmed The Issue

- The competition report identifies this as `M-16` with `medium` severity.
- The affected surface is specific: yield-provider-insurance at `ETH yield manager share minting and insurance repair distribution`.
- The missing property can be stated as `loss-time-eligibility-binding` and the trigger crosses `external provider impairment -> bridge deposit and insurance accounting`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: value-transfer-between-cohorts, insurance-drain
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
