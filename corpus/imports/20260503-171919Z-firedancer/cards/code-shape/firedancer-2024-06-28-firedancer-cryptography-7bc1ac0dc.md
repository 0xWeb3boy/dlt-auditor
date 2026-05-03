# Code-Shape Card

## Metadata

- ID: `firedancer-2024-06-28-firedancer-cryptography-7bc1ac0dc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-cryptographic-rng-failure`

## Code Shape Summary

- Protocol setup called a random-byte helper for connection identifiers without checking the documented failure path.

## Search Motifs

- Motif 1: random-byte helper return value ignored
- Motif 2: connection ID or nonce generated without fail-closed path
- Motif 3: protocol state initialized even when entropy helper can fail

## Typical Asymmetry

- The protocol assumes identifiers are unpredictable, but the implementation silently continues even when randomness acquisition fails.

## Patch Pattern

- Wrap randomness generation in a checked helper and abort or error-return immediately if entropy generation fails.

## False Match Warnings

- No evidence that an attacker can cause fd_rng_secure or getrandom failure.
- No evidence of observed duplicate, zero, predictable, or reused connection IDs in production.
