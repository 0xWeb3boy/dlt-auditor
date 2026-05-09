# Validation Card

## Metadata

- ID: `nibiru-2022-08-03-nibiru-storage-8c6e9717`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-margin-validation`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: position update and vault accounting that can admit undercollateralized exposure.
- Evidence 2: The validated finding ties the change to this invariant: Leveraged position updates must be rejected if the resulting position would be below maintenance margin or create bad debt after all price, funding, and margin effects are applied.

## What Could Have Invalidated It

- Compensating control 1: Margin tests alone are not security evidence unless runtime acceptance changed
- Compensating control 2: Do not claim exploitability if only test setup or TWAP timing changed

## Severity Guidance

- Expected impact band: `economic_integrity`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: A successful bypass can create undercollateralized exposure and bad debt, though the validated evidence did not prove a full exploit trace.
