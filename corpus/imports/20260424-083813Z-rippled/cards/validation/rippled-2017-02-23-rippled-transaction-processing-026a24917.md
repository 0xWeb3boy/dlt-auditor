# Validation Card

## Metadata

- ID: `rippled-2017-02-23-rippled-transaction-processing-026a24917`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-invariant-enforcement`

## What Confirmed The Issue

- Evidence 1: Adds ApplyContext::checkInvariants and checkInvariantsHelper in the transaction apply context.
- Evidence 2: Invariant execution is gated by the EnforceInvariants protocol amendment.

## What Could Have Invalidated It

- Compensating control 1: No concrete invariant predicates are shown in the supplied hunks.
- Compensating control 2: No specific pre-patch invalid ledger state or exploit path is demonstrated.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-integrity, consensus-safety
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No concrete invariant predicates are shown in the supplied hunks.
- Caution 2: No specific pre-patch invalid ledger state or exploit path is demonstrated.
