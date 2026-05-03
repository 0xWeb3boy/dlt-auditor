# Validation Card

## Metadata

- ID: `firedancer-2024-06-28-firedancer-cryptography-7bc1ac0dc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-cryptographic-rng-failure`

## What Confirmed The Issue

- Evidence 1: fd_quic_crypto_rand was documented as returning success or failure for cryptographic-quality random bytes.
- Evidence 2: Server Initial handling previously called fd_quic_crypto_rand for a new connection ID without checking the return value.

## What Could Have Invalidated It

- Compensating control 1: No evidence that an attacker can cause fd_rng_secure or getrandom failure.
- Compensating control 2: No evidence of observed duplicate, zero, predictable, or reused connection IDs in production.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No evidence that an attacker can cause fd_rng_secure or getrandom failure.
- Caution 2: No evidence of observed duplicate, zero, predictable, or reused connection IDs in production.
