# Root-Cause Card

## Metadata

- ID: `snarkvm-2023-10-07-snarkvm-transaction-processing-289b9edad`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization-structure-validation`

## Violated Invariant

- Invariant: Serialized authorization state must preserve the one-to-one structure required by later request, transition, and signature checks.

## Trust Boundary

- Boundary: serialized authorization input -> trusted authorization object

## Attack Surface

- Entrypoint type: deserialization-path
- Sensitive sink: authorization object used by transaction execution and verification

## Impact Pattern

- Primary impact: authorization structure hardening
- Secondary impact: malformed input rejection

## Short Reusable Lesson

- Authorization containers reconstructed from multiple serialized sequences should validate relational invariants at construction time.
