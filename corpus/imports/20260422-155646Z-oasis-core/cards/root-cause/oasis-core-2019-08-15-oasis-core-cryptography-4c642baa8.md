# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-08-15-oasis-core-cryptography-4c642baa8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Node registration validation should reject role declarations that omit mandatory role-specific metadata. In the provided diff, a node claiming the validator role must include at least one consensus address.

## Trust Boundary

- Boundary: `operator->registry`

## Attack Surface

- Entrypoint type: `registration-path`
- Sensitive sink: `node registry admission`

## Impact Pattern

- Primary impact: `invalid-state-acceptance`
- Secondary impact: `none`

## Short Reusable Lesson

- Node registration validation should reject role declarations that omit mandatory role-specific metadata. In the provided diff, a node claiming the validator role must include at least one consensus address. In this pattern, incomplete role-specific validation in the registry registration path: the validator role could be declared without enforcing the presence of consensus addresses. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
