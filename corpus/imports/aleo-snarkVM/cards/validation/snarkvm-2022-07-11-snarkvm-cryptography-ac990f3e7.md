# Validation Card

## Metadata

- ID: `snarkvm-2022-07-11-snarkvm-cryptography-ac990f3e7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-balance-nonnegativity-constraint`

## What Confirmed The Issue

- The patch imports `MSB` and asserts that the signed net balance most-significant bit is not set.
- The existing field consistency assertion remains in place.

## What Could Have Invalidated It

- The same non-negativity property is already constrained by another gadget on every path.
- The signed value cannot be attacker-controlled or cannot become negative by construction.

## Severity Guidance

- Expected impact band: economic_integrity
- Expected severity band: high_or_medium

## False-Positive Cautions

- A separate range proof already constrains the signed balance before conversion.
- The code path is only for test parsing and not used in proof generation.
