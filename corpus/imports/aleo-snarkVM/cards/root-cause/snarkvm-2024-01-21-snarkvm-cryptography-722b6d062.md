# Root-Cause Card

## Metadata

- ID: `snarkvm-2024-01-21-snarkvm-cryptography-722b6d062`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: User-supplied resource metadata must be checked with bounded arithmetic and enforced against an explicit active limit before deployment acceptance.

## Trust Boundary

- Boundary: deployment metadata -> circuit and ledger resource-limit enforcement

## Attack Surface

- Entrypoint type: deployment-validation
- Sensitive sink: deployment acceptance and circuit constraint-limit accounting

## Impact Pattern

- Primary impact: resource limit enforcement
- Secondary impact: deployment validation consistency

## Short Reusable Lesson

- Resource meters fed by deployment metadata should use checked arithmetic and a clearly scoped active limit.
