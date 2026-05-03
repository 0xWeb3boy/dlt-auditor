# Validation Card

## Metadata

- ID: `movement-2024-11-20-movement-cryptography-3f265410b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signed-field-not-bound`

## What Confirmed The Issue

- Before the patch, wrapper verification delegated to inner data verification.
- After the patch, verification hashes blob, timestamp, and id before checking the ECDSA signature.
- The changed code is in signed DA blob verification and signing paths.

## What Could Have Invalidated It

- The wrapper id is derived from the signed blob and cannot be attacker-controlled.
- Every downstream consumer ignores the id for trust, routing, replay, or storage identity.
- Another authenticated envelope binds the id before this verifier is trusted.

## Severity Guidance

- Expected impact band: integrity_hardening
- Expected severity band: medium_or_low
- Rationale: Missing signed-field binding is a classic integrity issue in cryptographic protocols, but Phase 4 kept this as likely because no downstream exploit path was shown.

## False-Positive Cautions

- Do not flag omitted fields that are purely cached or recomputable and never influence trust decisions.
- Do not claim forgery if the omitted field is independently authenticated elsewhere.
