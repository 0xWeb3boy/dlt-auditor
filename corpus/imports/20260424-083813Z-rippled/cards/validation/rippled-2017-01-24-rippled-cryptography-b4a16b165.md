# Validation Card

## Metadata

- ID: `rippled-2017-01-24-rippled-cryptography-b4a16b165`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-key-revocation-handling`

## What Confirmed The Issue

- Evidence 1: Commit and documentation describe revoking validator keys and handling compromised master keys.
- Evidence 2: Manifest parsing is changed so terminal revocation manifests can be accepted without ordinary signing-key fields.

## What Could Have Invalidated It

- Compensating control 1: No evidence shows an attacker could forge a revocation manifest or ordinary manifest.
- Compensating control 2: No evidence shows prior code accepted unauthorized validations.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: compromised-key-containment, validator-trust-management
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No evidence shows an attacker could forge a revocation manifest or ordinary manifest.
- Caution 2: No evidence shows prior code accepted unauthorized validations.
