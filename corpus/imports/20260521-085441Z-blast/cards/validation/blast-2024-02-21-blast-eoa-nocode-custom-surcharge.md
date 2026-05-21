# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-eoa-nocode-custom-surcharge`
- Bug family: `resource_accounting_and_limits`
- Bug class: `nocode-target-repeated-surcharge`

## What Confirmed The Issue

- The competition report identifies this as `M-08` with `medium` severity.
- The affected surface is specific: execution-client-gas-accounting at `transaction gas charge and caller-side allocation`.
- The missing property can be stated as `made-progress-classification` and the trigger crosses `EVM call graph -> Blast high-frame surcharge`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: denial-of-service, fee-miscalculation
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
