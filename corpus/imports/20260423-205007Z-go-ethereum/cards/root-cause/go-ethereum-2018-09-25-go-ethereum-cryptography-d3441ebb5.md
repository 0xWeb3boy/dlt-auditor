# Root-Cause Card

## Metadata

- ID: `go-ethereum-2018-09-25-go-ethereum-cryptography-d3441ebb5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-policy-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `domain-separated-signing`

## Violated Invariant

- Invariant: Clef/signer external requests should expose only intended API capabilities and should not proceed to transaction signing or account creation unless validation and UI policy allow them. Validation warnings are treated as blocking by default, with warning-only behavior reserved for explicit advanced mode.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `unsafe-signing-default`
- Secondary impact: `api-surface-reduction`

## Short Reusable Lesson

- The provided evidence supports a Clef/signer security-hardening finding, not a low-level cryptographic replay or signature-validation flaw.
