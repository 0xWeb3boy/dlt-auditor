# Root-Cause Card

## Metadata

- ID: `stacks-core-2025-10-21-stacks-core-cryptography-1979ab3fc2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ambiguous-crypto-verification-api`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-domain-and-signer-binding`

## Violated Invariant

- Invariant: Every signed protocol message must be verified against the exact signer set, message domain, reward cycle, and payload hash that authorize the downstream action.

## Trust Boundary

- Boundary: Untrusted signed bytes or public-key material crosses into cryptographic verification.

## Attack Surface

- Entrypoint type: `signed_message_verification`
- Sensitive sink: signature verification result or authorized signer decision

## Impact Pattern

- Primary impact: signature-verification-misuse-risk
- Secondary impact: unauthorized-message-acceptance

## Short Reusable Lesson

- The commit changes the secp256r1 verification API from returning Result<bool, &'static str> to returning Result<(), Secp256r1Error>. Invalid signatures now return Err(Secp256r1Error::InvalidSignature) instead of Ok(false), and tests were updated to match that contract. This is security-relevant crypto API hardening, but the evidence does not establish a concrete vulnerability or accepted invalid-signature path.
