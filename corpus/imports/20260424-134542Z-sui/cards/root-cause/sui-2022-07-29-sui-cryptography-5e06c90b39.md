# Root-Cause Card

## Metadata

- ID: `sui-2022-07-29-sui-cryptography-5e06c90b39`
- Bug family: `authz_and_role_gates`
- Bug class: `epoch-authentication-invariant`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A request crossing a trust boundary must prove the required authority before it can influence privileged protocol state.

## Trust Boundary

- Boundary: epoch-scoped certificate material -> signature verifier

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: authorizing object access or privileged state mutation

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Authorization must be checked at the boundary where authority is consumed, not inferred from caller-controlled fields or earlier best-effort filters. The patch strengthens Sui epoch authentication checks by making signed and certified epoch verification reject records whose authentication epoch is not exactly the immediately previous epoch.
