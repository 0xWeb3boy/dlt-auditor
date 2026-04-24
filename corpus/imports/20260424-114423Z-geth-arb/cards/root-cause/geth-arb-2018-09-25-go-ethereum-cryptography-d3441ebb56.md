# Root-Cause Card

## Metadata

- ID: `geth-arb-2018-09-25-go-ethereum-cryptography-d3441ebb56`
- Bug family: `authz_and_role_gates`
- Bug class: `signer-boundary-policy-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signing-policy-fail-closed`

## Violated Invariant

- Invariant: Signing middleware should fail closed on validation warnings or policy failures before presenting or authorizing a signature request.

## Trust Boundary

- Boundary: external signing request -> local signer approval and key use

## Attack Surface

- Entrypoint type: signer transaction validation path
- Sensitive sink: user-mediated or policy-mediated signature generation

## Impact Pattern

- Primary impact: authorization-bypass-prevention
- Secondary impact: key-safety
- Severity guide: low-medium

## Short Reusable Lesson

- The signer boundary treated validation warnings as continuable by default instead of rejecting before UI-mediated signing. Make warning or policy rejection fail closed by default, with explicit handling for warning-only flows.
