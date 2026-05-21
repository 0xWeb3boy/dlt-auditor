# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-eth-yield-token-decimal-conversion`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-domain-unit-conversion-mismatch`

## What Confirmed The Issue

- The competition report identifies this as `M-12` with `medium` severity.
- The affected surface is specific: bridge at `portal msg.value and L2 finalizeBridgeETHDirect equality check`.
- The missing property can be stated as `unit-consistency` and the trigger crosses `L1 ERC20 deposit amount -> L2 native ETH finalizer`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: asset-stranding, cross-domain-accounting-error
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
