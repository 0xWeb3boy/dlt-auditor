# Validation Card

## Metadata

- ID: `stellar-core-2015-03-22-stellar-core-storage-838f99c3c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `trustline-invariant-enforcement`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- TrustFrame::addBalance was added with bounds checks.
- Payment and offer paths replaced direct balance updates with addBalance calls.
- The payment path gained a destination-trustline authorization check.

## What Could Have Invalidated It

- If all direct arithmetic occurs only on freshly validated temporary deltas, the bug may be lower risk.
- If unauthorized trustlines cannot be reached by external payment operations, authorization impact is limited.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: Bypassing trustline bounds or authorization can break core issued-asset semantics, though the validation kept this as likely hardening rather than a proven exploit.

## False-Positive Cautions

- Do not flag centralized accounting helpers for performing the final assignment.
- Do not assume every trustline authorization field has revocation semantics.
