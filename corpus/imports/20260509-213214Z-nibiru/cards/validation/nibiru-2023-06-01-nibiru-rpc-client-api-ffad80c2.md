# Validation Card

## Metadata

- ID: `nibiru-2023-06-01-nibiru-rpc-client-api-ffad80c2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-margin-ratio-check`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: vault withdrawal and persisted position margin state.
- Evidence 2: The validated finding ties the change to this invariant: Any margin withdrawal or position mutation must validate the resulting position against liquidation thresholds before releasing collateral or committing state.

## What Could Have Invalidated It

- Compensating control 1: Do not flag read-only margin queries
- Compensating control 2: Do not overstate if the path only refactors existing equivalent checks

## Severity Guidance

- Expected impact band: `economic_integrity`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Collateral withdrawal below maintenance margin can directly affect protocol solvency, even though the finding is validated as likely hardening rather than proven loss.
