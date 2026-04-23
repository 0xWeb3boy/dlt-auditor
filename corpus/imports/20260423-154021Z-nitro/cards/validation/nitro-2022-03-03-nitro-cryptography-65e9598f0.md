# Validation Card

## Metadata

- ID: `nitro-2022-03-03-nitro-cryptography-65e9598f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`

## What Confirmed The Issue

- Evidence 1: The patch changes DAS-backed message handling from using raw bytes after the DAS header as a lookup key to first deserializing a `DataAvailabilityCertificate` and then using `cert.DataHash`.
- Evidence 2: Replace ad hoc byte-slice interpretation with structured decoding at the protocol boundary, then derive lookup inputs from parsed fields.

## What Could Have Invalidated It

- Compensating control 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Compensating control 2: If a downstream verifier canonicalizes and rechecks the same bytes before use, earlier shaping bugs may be benign.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Caution 2: Do not claim key compromise or replay without evidence that invalid or tampered data is actually accepted.
