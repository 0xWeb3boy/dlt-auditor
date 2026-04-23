# Root-Cause Card

## Metadata

- ID: `nitro-2022-09-10-nitro-transaction-processing-112522808`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `protocol-handshake-and-signature-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `handshake-signature-validation`

## Violated Invariant

- Invariant: Handshake and feed setup messages should reject wrong-chain inputs, missing mandatory metadata, and invalid signatures at the protocol boundary.

## Trust Boundary

- Boundary: `peer handshake->feed session establishment`

## Attack Surface

- Entrypoint type: `protocol-handshake-or-session-setup`
- Sensitive sink: `establishing a feed session or accepting a peer stream`

## Impact Pattern

- Primary impact: `improper-input-validation`
- Secondary impact: `none`

## Short Reusable Lesson

- Handshake and feed setup messages should reject wrong-chain inputs, missing mandatory metadata, and invalid signatures at the protocol boundary. The supplied evidence shows feed-handshake and test tightening around wrong-chain, missing-metadata, and invalid-signature cases, but it does not establish a concrete vulnerability or show that unsafe messages were previously accepted. This is best treated as unclear security relevance rather than a validated security fix. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
