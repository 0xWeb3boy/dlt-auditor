# Root-Cause Card

## Metadata

- ID: `stacks-core-2023-11-14-stacks-core-storage-3ae5e37f0e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cryptographic-signature-type-hardening`
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

- Primary impact: consensus-integrity
- Secondary impact: unauthorized-message-acceptance

## Short Reusable Lesson

- The patch changes Nakamoto stacker signatures from a generic `MessageSignature` placeholder to `SchnorrSignature`, converts them to `WSTSSignature` in `accept_block`, and rejects blocks whose stacker signature cannot be converted. This is plausibly security relevant because it affects consensus block acceptance and cryptographic signature representation, but the provided evidence does not establish that the old code accepted invalid blocks, bypassed signature verification, or caused a consensus vulnerability.
