# Validation Card

## Metadata

- ID: `snarkvm-2022-10-15-snarkvm-cryptography-8b2735410`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-consensus-target-validation`

## What Confirmed The Issue

- `CoinbaseSolution::verify` and `ProverSolution::verify` now receive target values.
- Ledger admission paths were updated to pass the latest proof target.

## What Could Have Invalidated It

- Every previous call site already performed an equivalent target comparison before accepting the result.
- Only benchmark or test APIs changed.

## Severity Guidance

- Expected impact band: consensus_and_economic_integrity
- Expected severity band: high_or_medium

## False-Positive Cautions

- The verifier obtains the active target internally from a trusted snapshot.
- The changed API is only a refactor with identical target checks in all old paths.
