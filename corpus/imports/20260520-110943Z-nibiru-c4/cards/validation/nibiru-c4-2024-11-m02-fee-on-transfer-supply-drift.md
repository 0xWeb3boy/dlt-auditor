# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m02-fee-on-transfer-supply-drift`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `fee-on-transfer-supply-drift`

## What Confirmed The Issue

- Public C4 report section M-02 rated this as Medium.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if fee-on-transfer tokens are excluded.
- No issue if the full input bank coin is burned regardless of ERC20 transfer fee.

## Severity Guidance

- Expected impact band: unbacked bank coin supply drift
- Expected severity band: medium

## False-Positive Cautions

- No issue if fee-on-transfer tokens are excluded.
- No issue if the full input bank coin is burned regardless of ERC20 transfer fee.
- No issue if conversion accounting explicitly mints/burns fee-adjusted shares rather than fixed-denom bank coins.
