# Validation Card

## Metadata

- ID: `firedancer-2024-07-15-firedancer-cryptography-22a0ab7f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `quic-packet-validation-hardening`

## What Confirmed The Issue

- Evidence 1: Adds early rejection when IPv4 total length exceeds the available packet buffer.
- Evidence 2: Adds early rejection when UDP length exceeds the remaining buffer and then bounds payload size by UDP length.

## What Could Have Invalidated It

- Compensating control 1: No advisory, CVE, exploit, or security-labeled commit message is provided.
- Compensating control 2: No supplied hunk proves out-of-bounds read, write, packet forgery, nonce reuse, or plaintext exposure.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No advisory, CVE, exploit, or security-labeled commit message is provided.
- Caution 2: No supplied hunk proves out-of-bounds read, write, packet forgery, nonce reuse, or plaintext exposure.
