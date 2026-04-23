# Root-Cause Card

## Metadata

- ID: `nitro-2022-08-28-nitro-cryptography-d70317ed8`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `message-signature-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-message-signing`

## Violated Invariant

- Invariant: Sequencer or feed messages should be signed and hashed over one canonical serialized representation, and verification should be explicitly gated by the intended operating mode.

## Trust Boundary

- Boundary: `feed message bytes->signature creation and verification`

## Attack Surface

- Entrypoint type: `feed-message-signing-or-validation`
- Sensitive sink: `accepting or emitting signed feed messages`

## Impact Pattern

- Primary impact: `message-integrity-risk`
- Secondary impact: `none`

## Short Reusable Lesson

- Sequencer or feed messages should be signed and hashed over one canonical serialized representation, and verification should be explicitly gated by the intended operating mode. The patch is security-relevant because it changes sequencer feed signature creation, verification gating, and message hashing. However, the provided evidence does not establish an actual vulnerability, exploitable acceptance path, or production configuration in which forged, replayed, or malformed messages could bypass validation. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
