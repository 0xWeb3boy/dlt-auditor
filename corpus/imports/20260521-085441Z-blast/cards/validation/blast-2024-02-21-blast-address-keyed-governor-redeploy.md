# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-address-keyed-governor-redeploy`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `durable-address-keyed-configuration`

## What Confirmed The Issue

- The competition report identifies this as `M-02` with `medium` severity.
- The affected surface is specific: l2-predeploy-configuration at `Blast.governorMap and Gas per-address configuration`.
- The missing property can be stated as `code-identity-binding` and the trigger crosses `contract address lifecycle -> Blast gas/yield governance`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: unauthorized-action, fee-claim-theft
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
