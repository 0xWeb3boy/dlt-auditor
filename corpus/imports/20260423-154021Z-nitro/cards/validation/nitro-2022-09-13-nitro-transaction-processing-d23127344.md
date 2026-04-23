# Validation Card

## Metadata

- ID: `nitro-2022-09-13-nitro-transaction-processing-d23127344`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-initialization`

## What Confirmed The Issue

- Evidence 1: The supplied evidence supports an API and startup-hardening change around broadcast-feed verifier setup: `BroadcastClient` now builds its own verifier and can fail during construction, and relay startup now propagates those initialization errors.
- Evidence 2: Centralize security-sensitive dependency construction inside the consumer's constructor and propagate initialization failure to startup so the component fails closed.

## What Could Have Invalidated It

- Compensating control 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Compensating control 2: If a downstream verifier canonicalizes and rechecks the same bytes before use, earlier shaping bugs may be benign.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Caution 2: Do not claim key compromise or replay without evidence that invalid or tampered data is actually accepted.
