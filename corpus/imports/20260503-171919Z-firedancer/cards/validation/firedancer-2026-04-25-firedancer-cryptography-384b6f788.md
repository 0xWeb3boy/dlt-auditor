# Validation Card

## Metadata

- ID: `firedancer-2026-04-25-firedancer-cryptography-384b6f788`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-transcript-validation`

## What Confirmed The Issue

- Evidence 1: BLS proof-of-possession verification is a security-sensitive cryptographic validation path.
- Evidence 2: The verifier now binds public_key into the hash input as H(msg || public_key, POP_DST).

## What Could Have Invalidated It

- Compensating control 1: No exploit path through the vote program is shown.
- Compensating control 2: No evidence demonstrates prior acceptance of an attacker-controlled invalid proof.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No exploit path through the vote program is shown.
- Caution 2: No evidence demonstrates prior acceptance of an attacker-controlled invalid proof.
