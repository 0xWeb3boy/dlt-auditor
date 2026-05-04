# Validation Card

## Metadata

- ID: `snarkvm-2022-08-05-snarkvm-cryptography-18c2a7bdd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fail-open-ledger-lookup`

## What Confirmed The Issue

- The unspent filter now returns a commitment only for `Ok(false)` from `contains_serial_number`.
- Lookup errors are logged and excluded instead of being reported as unspent.

## What Could Have Invalidated It

- The scanner output is explicitly documented as best-effort telemetry.
- All consumers re-check spend status against consensus state before action.

## Severity Guidance

- Expected impact band: client_or_node_state_classification
- Expected severity band: medium_or_low

## False-Positive Cautions

- The result is informational only and never used for signing or spending decisions.
- A later mandatory consensus check rejects spent records regardless of scanner output.
