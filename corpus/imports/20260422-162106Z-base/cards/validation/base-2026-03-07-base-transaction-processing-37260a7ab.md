# Validation Card

## Metadata

- ID: `base-2026-03-07-base-transaction-processing-37260a7ab`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation-hardening`

## What Confirmed The Issue

- Evidence 1: `build_proof_data()` now delegates to shared `ProofEncoder::encode_proof_bytes(...)` instead of local manual assembly.
- Evidence 2: `CryptoError` gains `InvalidVValue(u8)` with an explicit allowed set `0, 1, 27, 28`.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: the patch adds stricter signature-shape validation and centralizes proof encoding.
- Compensating control 2: Supported claim: invalid ECDSA `v` values are now explicitly rejected during proof construction.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: the patch adds stricter signature-shape validation and centralizes proof encoding.
- Caution 2: Supported claim: invalid ECDSA `v` values are now explicitly rejected during proof construction.
