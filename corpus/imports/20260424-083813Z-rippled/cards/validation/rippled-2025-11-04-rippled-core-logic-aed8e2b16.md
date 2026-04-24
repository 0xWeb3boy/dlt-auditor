# Validation Card

## Metadata

- ID: `rippled-2025-11-04-rippled-core-logic-aed8e2b16`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-invariant-enforcement`

## What Confirmed The Issue

- Evidence 1: LoanPay::doApply adds an explicit check for *assetsAvailableProxy > *assetsTotalProxy after payment-derived vault accounting updates.
- Evidence 2: The commit message specifically says LoanPay now fails the transaction if it violates the Vault assetsAvailable <= assetsTotal invariant.

## What Could Have Invalidated It

- Compensating control 1: No proof that an external user can trigger the invalid accounting state.
- Compensating control 2: No demonstrated fund theft, minting, loss, freezing, or user-visible balance corruption.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: state-consistency, asset-accounting-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No proof that an external user can trigger the invalid accounting state.
- Caution 2: No demonstrated fund theft, minting, loss, freezing, or user-visible balance corruption.
