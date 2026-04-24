# Validation Card

## Metadata

- ID: `rippled-2025-09-30-rippled-transaction-processing-e1b234cc5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-object-confusion-hardening`

## What Confirmed The Issue

- Evidence 1: Signature-checking helper previously accepted both PreclaimContext and sigObject, allowing access to ctx.tx while validating sigObject.
- Evidence 2: Multisign detection changed from ctx.tx.isFieldPresent(sfSigners) to sigObject.isFieldPresent(sfSigners).

## What Could Have Invalidated It

- Compensating control 1: No current caller is shown passing a sigObject different from ctx.tx.
- Compensating control 2: The commit states the bug is harmless for now.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: authorization-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No current caller is shown passing a sigObject different from ctx.tx.
- Caution 2: The commit states the bug is harmless for now.
