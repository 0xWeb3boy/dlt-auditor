# Validation Card

## Metadata

- ID: `sei-chain-2026-04-21-sei-chain-cryptography-9b9e33970`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `secret-key-lifecycle-hardening`

## What Confirmed The Issue

- Evidence 1: SecretKeyFromSecretBytes changes runtime.AddCleanup usage so the cleanup callback receives the secret pointer rather than capturing raw.
- Evidence 2: The cleanup comment explicitly says the secret is zeroed to avoid leaking it.

## What Could Have Invalidated It

- Compensating control 1: Secret keys are immutable byte slices with no cleanup finalizers or unsafe pointers.
- Compensating control 2: The path handles only public keys or test keys.

## Severity Guidance

- Expected impact band: confidentiality-or-key-lifecycle-hardening
- Expected severity band: low_or_informational

## False-Positive Cautions

- Caution 1: Secret keys are immutable byte slices with no cleanup finalizers or unsafe pointers.
- Caution 2: The path handles only public keys or test keys.
