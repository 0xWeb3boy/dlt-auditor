# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-discounted-messenger-reserved-gas`
- Bug family: `resource_accounting_and_limits`
- Bug class: `bridge-failure-record-gas-underreserve`

## What Confirmed The Issue

- The competition report identifies this as `H-07` with `high` severity.
- The affected surface is specific: cross-domain-messenger at `failedMessages and discountedValues storage writes`.
- The missing property can be stated as `failure-state-gas-reservation` and the trigger crosses `L2-to-L1 message finalization -> L1 messenger failure state`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: asset-stranding, cross-domain-lifecycle-failure
- Expected severity band: high

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
