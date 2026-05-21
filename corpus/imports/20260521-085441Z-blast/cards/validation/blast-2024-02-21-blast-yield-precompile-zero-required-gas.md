# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-yield-precompile-zero-required-gas`
- Bug family: `resource_accounting_and_limits`
- Bug class: `native-precompile-requiredgas-predicate`

## What Confirmed The Issue

- The competition report identifies this as `H-05` with `high` severity.
- The affected surface is specific: execution-client-native-precompile at `StateDB yield accounting and Shares predeploy storage`.
- The missing property can be stated as `native-work-metering` and the trigger crosses `EVM call -> native precompile execution`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: denial-of-service, fee-bypass
- Expected severity band: high

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
