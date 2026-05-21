# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-protocol-fee-vault-discounted-withdrawal`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `fee-vault-discount-domain-mismatch`

## What Confirmed The Issue

- The competition report identifies this as `M-05` with `medium` severity.
- The affected surface is specific: fee-vault-withdrawals at `OptimismPortal discounted ETH withdrawal claim`.
- The missing property can be stated as `fee-bucket-discount-exemption` and the trigger crosses `permissionless L2 fee-vault withdrawal -> L1 discounted ETH settlement`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: fee-bypass, protocol-revenue-loss
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
