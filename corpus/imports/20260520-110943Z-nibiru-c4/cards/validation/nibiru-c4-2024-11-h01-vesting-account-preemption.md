# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-h01-vesting-account-preemption`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `account-type-preemption`

## What Confirmed The Issue

- Public C4 report section H-01 rated this as High.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if vesting creation is governance-only or disabled.
- No issue if EVM contract accounts live in a disjoint address namespace.

## Severity Guidance

- Expected impact band: deterministic contract address preemption
- Expected severity band: high

## False-Positive Cautions

- No issue if vesting creation is governance-only or disabled.
- No issue if EVM contract accounts live in a disjoint address namespace.
- No issue if deployment converts or rejects pre-existing non-EVM accounts before storing code.
