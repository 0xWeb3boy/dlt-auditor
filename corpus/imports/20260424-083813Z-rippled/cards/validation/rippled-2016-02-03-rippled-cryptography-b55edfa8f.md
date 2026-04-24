# Validation Card

## Metadata

- ID: `rippled-2016-02-03-rippled-cryptography-b55edfa8f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `validator-manifest-signature-hardening`

## What Confirmed The Issue

- Evidence 1: Manifest::verify now rejects the manifest if ripple::verify with signingKey fails.
- Evidence 2: Manifest::verify now verifies the master key using the explicit sfMasterSignature field after the signing-key check.

## What Could Have Invalidated It

- Compensating control 1: No advisory, CVE, or explicit vulnerability statement is provided.
- Compensating control 2: No attack path or forged-manifest scenario is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: cryptographic-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No advisory, CVE, or explicit vulnerability statement is provided.
- Caution 2: No attack path or forged-manifest scenario is shown.
