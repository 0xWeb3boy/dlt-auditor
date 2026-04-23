# Validation Card

## Metadata

- ID: `nitro-2022-08-28-nitro-cryptography-d70317ed8`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `message-signature-validation-hardening`

## What Confirmed The Issue

- Evidence 1: The patch is security-relevant because it changes sequencer feed signature creation, verification gating, and message hashing.
- Evidence 2: Clarify signature applicability and canonicalize the data being signed, using a dedicated verifier path and strict serialization for hash construction.

## What Could Have Invalidated It

- Compensating control 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Compensating control 2: If a downstream verifier canonicalizes and rechecks the same bytes before use, earlier shaping bugs may be benign.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Caution 2: Do not claim key compromise or replay without evidence that invalid or tampered data is actually accepted.
