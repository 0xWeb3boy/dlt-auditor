# Validation Card

## Metadata

- ID: `firedancer-2026-01-09-firedancer-cryptography-1ad8a534f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-root-validation-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly references FEC chaining verification, duplicate confirmation repair, and equivocation protection.
- Evidence 2: Data shred insertion now rejects an incoming shred when its merkle root conflicts with a verified confirmed merkle root.

## What Could Have Invalidated It

- Compensating control 1: No concrete attacker flow or exploit sequence is shown.
- Compensating control 2: No evidence of signature forgery or cryptographic primitive failure is provided.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No concrete attacker flow or exploit sequence is shown.
- Caution 2: No evidence of signature forgery or cryptographic primitive failure is provided.
