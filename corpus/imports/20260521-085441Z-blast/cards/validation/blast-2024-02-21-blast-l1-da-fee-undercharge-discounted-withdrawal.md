# Validation Card

## Metadata

- ID: `blast-2024-02-21-blast-l1-da-fee-undercharge-discounted-withdrawal`
- Bug family: `resource_accounting_and_limits`
- Bug class: `fee-recovery-discount-mismatch`

## What Confirmed The Issue

- The competition report identifies this as `M-13` with `medium` severity.
- The affected surface is specific: fee-vault-accounting at `remote fee-vault payout through discounted withdrawal path`.
- The missing property can be stated as `request-response-cost-symmetry` and the trigger crosses `L2 L1/DA fee accounting -> L1 fee recipient withdrawal`.

## What Could Have Invalidated It

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.

## Severity Guidance

- Expected impact band: fee-bypass, protocol-cost-underrecovery
- Expected severity band: medium

## False-Positive Cautions

- Do not report a broad family match unless the target code reaches the same sensitive sink.
- Preserve attacker capability and lifecycle preconditions; many Blast patterns are real only in value-bearing, claimable, bridge, or upgrade contexts.
