# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-native-yield-gas-refund-undermetering`
- Bug family: `resource_accounting_and_limits`
- Bug class: `native-bookkeeping-undermetering`

## What Confirmed The Issue

- The competition report identifies this as `M-18` with `medium` severity.
- The affected surface is specific: execution-client-native-accounting at `Shares and Gas predeploy storage plus StateDB journals`.
- The missing property can be stated as `native-work-gas-budget` and the trigger crosses `EVM transaction/opcode gas schedule -> Blast native StateDB side effects`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: denial-of-service, resource-accounting
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
