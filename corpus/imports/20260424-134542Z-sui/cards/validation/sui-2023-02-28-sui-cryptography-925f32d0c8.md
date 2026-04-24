# Validation Card

## Metadata

- ID: `sui-2023-02-28-sui-cryptography-925f32d0c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-metadata-validation`

## What Confirmed The Issue

- Committee construction now calls validator.metadata.verify() before using consensus address and network key fields.
- Worker-cache construction now calls validator.metadata.verify() before using worker key and worker address fields.
- The verified representation contains typed public keys, network keys, worker keys, and multiaddrs derived from validator metadata.
- The changed data feeds active-validator Narwhal consensus and networking configuration.

## What Could Have Invalidated It

- No full implementation of metadata.verify() is shown in the supplied evidence.
- No test assertions are provided showing rejected malformed or malicious metadata.
- No exploit path, validator admission bypass, or proof-of-possession failure is demonstrated.
- No evidence shows prior behavior caused state corruption or a concrete consensus safety failure.

## Severity Guidance

- Expected impact band: consensus-configuration-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as security hardening, not a proven security fix.
- Do not claim signature forgery, private key compromise, or replay vulnerability.
- Do not claim arbitrary validator admission or governance bypass.
- Do not claim state corruption from the supplied patch alone.
