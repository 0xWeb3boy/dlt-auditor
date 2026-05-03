# Validation Card

## Metadata

- ID: `firedancer-2024-01-24-firedancer-transaction-processing-d17e587ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-key-isolation-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject uses explicit security framing: remote signing for QUIC/TLS.
- Evidence 2: QUIC/TLS adds a signer callback that delegates signing to fd_keyguard_client_sign.

## What Could Have Invalidated It

- Compensating control 1: No proof that private keys were exposed before the patch.
- Compensating control 2: No proof that arbitrary payload signing or signature forgery was possible before the patch.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No proof that private keys were exposed before the patch.
- Caution 2: No proof that arbitrary payload signing or signature forgery was possible before the patch.
