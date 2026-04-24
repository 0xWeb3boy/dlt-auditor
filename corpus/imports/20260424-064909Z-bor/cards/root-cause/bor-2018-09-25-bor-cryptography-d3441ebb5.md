# Root-Cause Card

## Metadata

- ID: `bor-2018-09-25-bor-cryptography-d3441ebb5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-trust-boundary-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature authorization and domain binding`

## Violated Invariant

- Invariant: A signature or signer action must cover the full security context that gives the message authority, including domain, chain, signer scope, and payload semantics.

## Trust Boundary

- Boundary: untrusted signed payload to verifier or signer boundary

## Attack Surface

- Entrypoint type: transaction/message signature verification path
- Sensitive sink: signer recovery, authorization, or replay-protection decision

## Impact Pattern

- Primary impact: unsafe-default-behavior
- Secondary impact: reduced-attack-surface

## Short Reusable Lesson

- The signer API was too permissive at the trust boundary: validator warnings were not enforced as blocking conditions by default, the remote API exposed an extra helper operation, and account-creation password input handling was weaker than the patched version.
