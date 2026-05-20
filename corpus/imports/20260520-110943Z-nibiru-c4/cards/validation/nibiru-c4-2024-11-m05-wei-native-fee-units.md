# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m05-wei-native-fee-units`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fee-unit-conversion-mismatch`

## What Confirmed The Issue

- Public C4 report section M-05 rated this as Medium.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if the denomination is actually wei-denominated.
- No issue if a helper already converts txData.Fee before coin creation.

## Severity Guidance

- Expected impact band: fee denomination mismatch
- Expected severity band: medium

## False-Positive Cautions

- No issue if the denomination is actually wei-denominated.
- No issue if a helper already converts txData.Fee before coin creation.
- Beware examples with 1 wei gas price if minimum transferable unit rules forbid them.
