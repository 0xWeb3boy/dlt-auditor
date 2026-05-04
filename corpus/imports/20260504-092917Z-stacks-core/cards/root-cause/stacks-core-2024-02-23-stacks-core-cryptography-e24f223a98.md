# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-02-23-stacks-core-cryptography-e24f223a98`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-vote-message-validation`
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

- Primary impact: signer-vote-integrity
- Secondary impact: consensus-adjacent-integrity

## Short Reusable Lesson

- The patch replaces an implicit signer vote encoding based on raw 32-byte hashes, 33-byte hash-plus-marker messages, and first-32-byte slicing with an explicit serialized `NakamotoBlockVote` containing `signer_signature_hash` and `rejected`. This is plausibly security-relevant because it touches signer vote validation and signature result handling, but the supplied evidence does not establish an exploitable vulnerability, consensus break, signature forgery, or threshold-signature bypass.
