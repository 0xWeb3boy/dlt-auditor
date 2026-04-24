# Validation Card

## Metadata

- ID: `rippled-2016-04-21-rippled-rpc-client-api-b5dbd7942`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `failed-handshake-resource-accounting`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says connections that fail security checks are being handled correctly.
- Evidence 2: Commit body states the fix releases the slot and decrements IP connection counters.

## What Could Have Invalidated It

- Compensating control 1: No proof that an attacker could exhaust slots or IP counters in practice.
- Compensating control 2: No evidence of a successful authentication, cryptographic, or replay bypass.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: resource-exhaustion, denial-of-service
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No proof that an attacker could exhaust slots or IP counters in practice.
- Caution 2: No evidence of a successful authentication, cryptographic, or replay bypass.
