# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-nonupgradeable-predeploys-proxied`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `constructor-only-contract-behind-proxy`

## What Confirmed The Issue

- The competition report identifies this as `M-10` with `medium` severity.
- The affected surface is specific: l2-genesis-predeploys at `Blast and Gas predeploy implementation and mutable configuration`.
- The missing property can be stated as `proxy-intent-and-initializer-model` and the trigger crosses `genesis/deployment proxy admin -> system predeploy logic`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: upgrade-safety, unauthorized-action
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
