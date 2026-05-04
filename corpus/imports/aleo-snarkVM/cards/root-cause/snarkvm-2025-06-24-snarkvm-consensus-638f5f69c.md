# Root-Cause Card

## Metadata

- ID: `snarkvm-2025-06-24-snarkvm-consensus-638f5f69c`
- Bug family: `authz_and_role_gates`
- Bug class: `reserved-locator-validation-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `reserved-entrypoint-gating`

## Violated Invariant

- Invariant: Reserved system upgrade entrypoints must not be callable through deployed user programs unless the verifier explicitly allows that path.

## Trust Boundary

- Boundary: user deployment bytecode -> reserved system program locator

## Attack Surface

- Entrypoint type: deployment-validation
- Sensitive sink: program-mediated call to `credits.aleo/upgrade`

## Impact Pattern

- Primary impact: deployment validation and reserved action gating
- Secondary impact: upgrade path integrity

## Short Reusable Lesson

- Reserved system entrypoints should be guarded at the bytecode admission boundary, not only at later runtime checks.
