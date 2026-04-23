# Validation Card

## Metadata

- ID: `go-ethereum-2016-10-28-go-ethereum-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-separation`

## What Confirmed The Issue

- Evidence 1: The commit body states that `eth_sign` now prefixes arbitrary messages and signs the resulting hash instead of exposing the older semantics.
- Evidence 2: Comments and helper split changes explicitly warn about chosen-input risk and separate Ethereum-format signing from the raw primitive.

## What Could Have Invalidated It

- Compensating control 1: The raw signing primitive was never reachable from untrusted callers, so the change was only cosmetic.
- Compensating control 2: Another layer already prefixed and hashed all externally supplied messages before they reached the signing API.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Keep the claim at signing-boundary hardening unless a concrete misuse path is shown.
- Caution 2: This is not a transaction-validation or nonce-handling fix based on the supplied evidence.
