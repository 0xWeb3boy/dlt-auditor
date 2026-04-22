# Validation Card

## Metadata

- ID: `base-2026-03-06-base-cryptography-32483663d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Evidence 1: Commit body explicitly states `MAX_PROPOSALS (1024)` was added to prevent memory exhaustion on deserialization from untrusted input.
- Evidence 2: Commit body says `ProofClaim::validate()` rejects empty proposal lists and oversized proposal vectors.

## What Could Have Invalidated It

- Compensating control 1: This supports malformed-input and resource-exhaustion hardening at an untrusted input boundary.
- Compensating control 2: This does not prove a concrete signature-forgery, replay, or authentication bypass bug was fixed.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: This supports malformed-input and resource-exhaustion hardening at an untrusted input boundary.
- Caution 2: This does not prove a concrete signature-forgery, replay, or authentication bypass bug was fixed.
