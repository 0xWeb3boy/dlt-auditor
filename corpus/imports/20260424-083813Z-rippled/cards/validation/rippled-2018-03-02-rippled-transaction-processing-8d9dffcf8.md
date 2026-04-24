# Validation Card

## Metadata

- ID: `rippled-2018-03-02-rippled-transaction-processing-8d9dffcf8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `escrow-condition-validation-hardening`

## What Confirmed The Issue

- Evidence 1: EscrowCreate validation now requires a FinishAfter value or cryptocondition for cases that otherwise could be immediately finished.
- Evidence 2: The change is gated by fix1571, indicating a consensus-rule amendment rather than ordinary cleanup.

## What Could Have Invalidated It

- Compensating control 1: No evidence of theft, unauthorized signature use, cryptocondition bypass, or ledger corruption is provided.
- Compensating control 2: The commit says the prior immediate-finish behavior was documented, which weakens a concrete vulnerability claim.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: escrow-release-policy-hardening, economic-risk-reduction
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No evidence of theft, unauthorized signature use, cryptocondition bypass, or ledger corruption is provided.
- Caution 2: The commit says the prior immediate-finish behavior was documented, which weakens a concrete vulnerability claim.
