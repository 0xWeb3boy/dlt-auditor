# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-direct-eth-yield-deposit-min-gas-bricking`
- Bug family: `resource_accounting_and_limits`
- Bug class: `bridge-direct-deposit-gas-budget`

## What Confirmed The Issue

- The competition report identifies this as `H-03` with `high` severity.
- The affected surface is specific: bridge at `L2 direct ETH finalizer and recipient transfer`.
- The missing property can be stated as `cross-domain-replay-and-gas-budgeting` and the trigger crosses `L1 bridge deposit -> L2 value finalization`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: asset-stranding, denial-of-service
- Expected severity band: high

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
