# Root-Cause Card

## Metadata

- ID: `firedancer-2025-12-01-firedancer-core-logic-d94e26080`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-input-bounds-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `nested-block-length-validation`

## Violated Invariant

- Invariant: Nested capture blocks and option records must prove their declared lengths fit the buffered input before advancing parse offsets.

## Trust Boundary

- Boundary: Malformed capture or tooling input crossing into a block-based parser.

## Attack Surface

- Entrypoint type: block/option parser
- Sensitive sink: block length advancement and option iteration

## Impact Pattern

- Primary impact: memory safety hardening
- Secondary impact: parser robustness

## Short Reusable Lesson

- A block-oriented parser trusted nested record lengths just enough to advance internal offsets before all backing-buffer checks were complete.
