# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-maker-dsr-shutdown-strands-dai`
- Bug family: `staking_registry_and_accountability`
- Bug class: `external-provider-shutdown-recovery-gap`

## What Confirmed The Issue

- The competition report identifies this as `M-17` with `medium` severity.
- The affected surface is specific: usd-yield-provider at `DSR_MANAGER.exit and DAI recovery ownership`.
- The missing property can be stated as `emergency-recovery-path` and the trigger crosses `Maker emergency shutdown -> Blast USD yield accounting`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: asset-stranding, liveness-failure
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
