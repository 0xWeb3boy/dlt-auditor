# Root-Cause Card

## Metadata

- ID: `reth-2023-05-04-reth-consensus-010b600f3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch adds an explicit consistency check in block insertion so a block is rejected when its `parent_hash` matches a canonical block but the canonical height of that hash does not equal the claimed parent number. The evidence supports that this is a consensus-sensitive invariant check, but it does not establish a concrete vulnerability or exploit path.
