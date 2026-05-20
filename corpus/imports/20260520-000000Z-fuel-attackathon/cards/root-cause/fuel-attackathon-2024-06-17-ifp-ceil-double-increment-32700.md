# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-ceil-double-increment-32700`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-rounding-double-adjustment`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rounding-step-idempotence`

## Violated Invariant

- Ceil must add at most one unit of precision when the value has a fractional component.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `rounded fixed-point amount used in transfers or settlement`

## Attack Surface

- Submit values with fractional parts to contract logic using ceil or round.
- Choose negative inputs that enter the double-adjustment branch.

## Exploit Preconditions

- ceil delegates to underlying ceil and then adds another unit in the wrapper.
- The result is used as a token amount, debt amount, or price input.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Rounding helpers should have one canonical adjustment point; layered wrappers must not reapply the same unit step.
