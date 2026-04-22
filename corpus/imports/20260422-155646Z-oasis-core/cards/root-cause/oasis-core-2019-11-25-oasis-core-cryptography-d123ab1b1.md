# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-11-25-oasis-core-cryptography-d123ab1b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-identity-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `identity-validation`

## Violated Invariant

- Invariant: Registry descriptors should only advertise addresses that carry valid identities, and optional address fields should only be included for roles that actually require them.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: `node registry admission`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Registry descriptors should only advertise addresses that carry valid identities, and optional address fields should only be included for roles that actually require them. In this pattern, the registration code was assembling node descriptors with weaker coupling between advertised roles and role-specific fields, and it did not explicitly reject validator consensus addresses whose embedded identity was invalid before building the registration payload. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
