# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-claimall-gas-nonoptimal-rate`
- Bug family: `resource_accounting_and_limits`
- Bug class: `claim-helper-nonoptimal-payout`

## What Confirmed The Issue

- The competition report identifies this as `M-04` with `medium` severity.
- The affected surface is specific: gas-claim-predeploy at `claimable gas payout and retained seconds accounting`.
- The missing property can be stated as `claim-curve-optimality` and the trigger crosses `authorized gas governor -> Gas predeploy claim curve`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: fee-bypass, value-miscalculation
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
