# Root-Cause Card

## Metadata

- ID: `firedancer-2023-01-30-firedancer-core-logic-4f66d0180`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-archive-metadata-parsing`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `bounded-metadata-parsing`

## Violated Invariant

- Invariant: Archive metadata fields must parse to finite, non-negative values within their fixed-width field boundaries before iterator state advances.

## Trust Boundary

- Boundary: Untrusted archive bytes crossing into a local archive parser and iterator.

## Attack Surface

- Entrypoint type: file-format metadata parser
- Sensitive sink: iterator advancement and size-based buffer slicing

## Impact Pattern

- Primary impact: denial of service
- Secondary impact: none

## Short Reusable Lesson

- A fixed-width metadata parser trusted whitespace-only or negative numeric fields before proving the parsed values were valid and bounded.
