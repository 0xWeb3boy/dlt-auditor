# Validation Card

## Metadata

- ID: `rippled-2012-05-15-rippled-transaction-processing-9bbbf24f4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-claim-authority-proof`

## What Confirmed The Issue

- Evidence 1: Commit subject says Claim transactions are fixed to prove authority.
- Evidence 2: Claim transaction schema removes required GeneratorID and adds required PubKey and Signature fields.

## What Could Have Invalidated It

- Compensating control 1: No validation path showing the signature is verified.
- Compensating control 2: No rejection behavior for invalid or missing authority proof is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: authorization-hardening, transaction-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No validation path showing the signature is verified.
- Caution 2: No rejection behavior for invalid or missing authority proof is shown.
