# Validation Card

## Metadata

- ID: `stellar-core-2015-03-20-stellar-core-storage-cc9a3c0bd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-validation`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- ChangeTrustOpFrame::doApply gained a requested-limit check before assigning the trustline limit.
- The transaction result schema gained an INVALID_LIMIT code.

## What Could Have Invalidated It

- If the operation could only lower unused credit and never affect existing balances, impact would be lower.
- A database constraint enforcing the same condition would make the application guard defense in depth.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: A broken trustline limit invariant can corrupt asset accounting semantics, but the evidence does not show a concrete theft path or consensus split.

## False-Positive Cautions

- Do not flag limit changes that are allowed only after balance is reduced first.
- Do not generalize to all account flags unless the changed field is an accounting bound.
