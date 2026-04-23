# Validation Card

## Metadata

- ID: `go-ethereum-2018-09-25-go-ethereum-cryptography-d3441ebb5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-policy-hardening`

## What Confirmed The Issue

- Evidence 1: NewSignerAPI stores rejectMode as the inverse of advancedMode, making rejection the default behavior.
- Evidence 2: SignTransaction now returns validator warnings as errors when rejectMode is enabled, blocking the signing flow before approval/signing continues.

## What Could Have Invalidated It

- Compensating control 1: Validate as signer/Clef hardening, not a proven cryptographic vulnerability fix.
- Compensating control 2: Do not claim private-key extraction, signature forgery, consensus impact, or remote compromise from this evidence.

## Severity Guidance

- Expected impact band: low
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Validate as signer/Clef hardening, not a proven cryptographic vulnerability fix.
- Caution 2: Do not claim private-key extraction, signature forgery, consensus impact, or remote compromise from this evidence.
