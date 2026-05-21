# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-access-list-intrinsic-gas-attribution`
- Bug family: `resource_accounting_and_limits`
- Bug class: `intrinsic-gas-attribution-mismatch`

## What Confirmed The Issue

- The competition report identifies this as `M-14` with `medium` severity.
- The affected surface is specific: gas-fee-attribution at `GasTracker allocation and claimable gas recipient`.
- The missing property can be stated as `fee-recipient-attribution` and the trigger crosses `transaction intrinsic gas -> developer gas accounting`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: fee-attribution-error, fee-bypass
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
