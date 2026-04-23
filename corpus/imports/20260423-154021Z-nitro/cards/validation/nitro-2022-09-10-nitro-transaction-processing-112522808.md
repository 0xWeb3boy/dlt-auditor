# Validation Card

## Metadata

- ID: `nitro-2022-09-10-nitro-transaction-processing-112522808`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `protocol-handshake-and-signature-validation`

## What Confirmed The Issue

- Evidence 1: The supplied evidence shows feed-handshake and test tightening around wrong-chain, missing-metadata, and invalid-signature cases, but it does not establish a concrete vulnerability or show that unsafe messages were previously accepted.
- Evidence 2: Make protocol rejection conditions explicit at the trust boundary and add regression tests that assert exact failure modes.

## What Could Have Invalidated It

- Compensating control 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Compensating control 2: If a downstream verifier canonicalizes and rechecks the same bytes before use, earlier shaping bugs may be benign.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
- Caution 2: Do not claim key compromise or replay without evidence that invalid or tampered data is actually accepted.
