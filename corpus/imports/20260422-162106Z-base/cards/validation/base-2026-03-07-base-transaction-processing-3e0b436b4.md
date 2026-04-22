# Validation Card

## Metadata

- ID: `base-2026-03-07-base-transaction-processing-3e0b436b4`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation`

## What Confirmed The Issue

- Evidence 1: `build_proof_data()` now delegates to shared `ProofEncoder::encode_proof_bytes(...)` instead of manual local assembly.
- Evidence 2: `CryptoError::InvalidVValue(u8)` was added, showing explicit rejection of unsupported ECDSA recovery-byte values.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: the commit hardens signature/proof encoding validation by rejecting invalid ECDSA `v` values in shared code.
- Compensating control 2: Supported claim: the change reduces risk of malformed proof data being constructed or forwarded.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: the commit hardens signature/proof encoding validation by rejecting invalid ECDSA `v` values in shared code.
- Caution 2: Supported claim: the change reduces risk of malformed proof data being constructed or forwarded.
