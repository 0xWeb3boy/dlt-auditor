# Root-Cause Card

## Metadata

- ID: `scroll-2024-08-06-scroll-cryptography-72f88bae`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-preimage-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-payload-consistency`

## Violated Invariant

- Invariant: Signer recovery for legacy and current login flows must hash the same canonical payload that the prover actually signed for that compatibility mode.

## Trust Boundary

- Boundary: `legacy-prover->coordinator-auth-session`

## Attack Surface

- Entrypoint type: `session-setup`
- Sensitive sink: `public-key recovery used to authenticate a prover login`

## Impact Pattern

- Primary impact: `unauthorized-action`
- Secondary impact: `none`

## Short Reusable Lesson

- Signer recovery for legacy and current login flows must hash the same canonical payload that the prover actually signed for that compatibility mode. The evidence supports a targeted compatibility fix in coordinator authentication: the legacy Curie public-key recovery path was changed to hash a dedicated legacy identity payload instead of the current Message object. That shows a signer-recovery mismatch, but the provided diff does not establish that this caused acceptance of forged logins, replay, or an authorization bypass. The robust fix is to reconstruct the legacy identity payload explicitly in the compatibility branch and recover the signer from that canonical legacy preimage instead of the current message object.
