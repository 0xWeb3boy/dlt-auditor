# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-zero-rounded-discounted-withdrawal`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `zero-rounded-positive-value-lifecycle`

## What Confirmed The Issue

- The competition report identifies this as `M-03` with `medium` severity.
- The affected surface is specific: bridge-withdrawal-discounting at `portal finalizedWithdrawals and messenger failedMessages/discountedValues`.
- The missing property can be stated as `zero-progress-handling` and the trigger crosses `discounted yield withdrawal -> cross-domain messenger replay state`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: asset-stranding, cross-domain-lifecycle-failure
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
