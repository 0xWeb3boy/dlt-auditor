# Root-Cause Card

## Metadata

- ID: `sui-2026-03-25-sui-core-logic-2265f3d6f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vm-recursion-bound-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Untrusted work must be bounded, attributed, and charged or throttled before it can consume shared validator resources.

## Trust Boundary

- Boundary: untrusted protocol input -> privileged core state

## Attack Surface

- Entrypoint type: state-transition
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: availability-hardening
- Secondary impact: resource-exhaustion-risk-reduction

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch is best classified as VM hardening, not a confirmed vulnerability fix. The evidence supports that recursive `TypeTag` loading and ability computation were changed to use `TypeSize::for_type_traversal()` and helper implementations, consistent with bounding recursive callsites.
