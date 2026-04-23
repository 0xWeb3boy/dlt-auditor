# Validation Card

## Metadata

- ID: `nitro-2025-11-07-nitro-cryptography-4272c4cfa`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-hardening`

## What Confirmed The Issue

- Evidence 1: The provided evidence supports correctness and hardening changes in the Anytrust DAS RPC/data-streaming path, not a confirmed vulnerability fix.
- Evidence 2: Reject unsupported security-sensitive configuration early and make verifier selection explicit for each operating mode.

## What Could Have Invalidated It

- Compensating control 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Compensating control 2: If a downstream verifier canonicalizes and rechecks the same bytes before use, earlier shaping bugs may be benign.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Caution 2: Do not claim key compromise or replay without evidence that invalid or tampered data is actually accepted.
