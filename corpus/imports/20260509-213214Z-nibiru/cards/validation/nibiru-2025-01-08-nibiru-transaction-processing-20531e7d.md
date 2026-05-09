# Validation Card

## Metadata

- ID: `nibiru-2025-01-08-nibiru-transaction-processing-20531e7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-or-state-drift`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: bank coin burn amount and supply accounting.
- Evidence 2: The validated finding ties the change to this invariant: When converting a bridge representation, the native-side burn or debit must match the user-supplied amount accepted by the protocol, not a post-transfer amount that a malicious token can reduce.

## What Could Have Invalidated It

- Compensating control 1: Do not flag ordinary ERC20 transfers where output amount is intentionally the asset delivered
- Compensating control 2: Need a native supply burn/debit tied to token callback result

## Severity Guidance

- Expected impact band: `economic_integrity`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Burning less than the accepted amount can break supply accounting for a bridge asset; exploit profit was not fully demonstrated.
