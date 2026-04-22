# Root-Cause Card

## Metadata

- ID: `oasis-core-2023-02-01-oasis-core-rpc-client-api-8eabf0d47`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `version-and-membership-validation`

## Violated Invariant

- Invariant: Key manager committee membership should be derived only from nodes whose supported key manager runtime versions all conform to the authoritative key manager status. Accepting a node based on only the first matching runtime entry is insufficient.

## Trust Boundary

- Boundary: `operator->registry`

## Attack Surface

- Entrypoint type: `registration-path`
- Sensitive sink: `runtime registry admission`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Key manager committee membership should be derived only from nodes whose supported key manager runtime versions all conform to the authoritative key manager status. Accepting a node based on only the first matching runtime entry is insufficient. In this pattern, committee construction validated only a first matching runtime registration instead of validating every supported key manager runtime version advertised by the node against the same status fields. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
