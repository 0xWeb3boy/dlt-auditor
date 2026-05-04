# Validation Card

## Metadata

- ID: `stellar-core-2015-02-28-stellar-core-transaction-processing-117a83b23`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-transaction-sequence-validation`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- TransactionFrame::apply gained a bad-sequence check before continuing application.
- AccountFrame::getSeq changed to query sequence state by both account and sequence slot.

## What Could Have Invalidated It

- A mandatory earlier validation step with identical account and slot scoping would reduce the security impact.
- If failed apply paths could not mutate state or affect fees, this would be lower-severity correctness hardening.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: Incorrect sequence enforcement can admit transactions that should be rejected and can disturb ordering or replay invariants, but the finding does not prove theft or consensus divergence.

## False-Positive Cautions

- Do not flag sequence-cache refactors unless they can affect authoritative transaction acceptance.
- Do not treat legacy single-sequence account models as missing slot-specific validation.
