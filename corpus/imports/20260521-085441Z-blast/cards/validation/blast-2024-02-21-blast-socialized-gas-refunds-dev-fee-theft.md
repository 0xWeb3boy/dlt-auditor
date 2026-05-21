# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-socialized-gas-refunds-dev-fee-theft`
- Bug family: `resource_accounting_and_limits`
- Bug class: `global-refund-socialization`

## What Confirmed The Issue

- The competition report identifies this as `H-02` with `high` severity.
- The affected surface is specific: gas-fee-attribution at `per-contract claimable gas accounting`.
- The missing property can be stated as `refund-source-attribution` and the trigger crosses `user-controlled EVM execution -> developer gas-fee distribution`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: fee-bypass, unauthorized-value-shift
- Expected severity band: high

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
