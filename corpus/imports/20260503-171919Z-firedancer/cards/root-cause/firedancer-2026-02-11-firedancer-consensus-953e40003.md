# Root-Cause Card

## Metadata

- ID: `firedancer-2026-02-11-firedancer-consensus-953e40003`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `missing-bounds-check-buffer-overflow`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `copy-back-length-equality-check`

## Violated Invariant

- Invariant: Caller-owned account buffers must only be written after the callee-returned length is proven equal to the caller buffer length.

## Trust Boundary

- Boundary: CPI callee output crossing back into caller-owned serialized account storage.

## Attack Surface

- Entrypoint type: nested execution copy-back path
- Sensitive sink: final memcpy into caller account storage

## Impact Pattern

- Primary impact: memory safety
- Secondary impact: memory corruption

## Short Reusable Lesson

- The copy-back path trusted a post-call data length even though the caller-side serialized buffer length could be stale in shared-data scenarios.
