# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ufp32-fract-underflow-33233`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-fraction-underflow`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `fractional-mask-bounds`

## Violated Invariant

- A fractional-part helper must not underflow for any valid fixed-point input.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `fract result used by ceil and signed fixed-point wrappers`

## Attack Surface

- Call UFP32.fract or functions that delegate to it.
- Trigger ceil or IFP64.fract on valid values.

## Exploit Preconditions

- The implementation subtracts u32::max and one after a left shift that cannot exceed u32::max.
- The VM traps on underflow.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `arithmetic-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Bit-level fixed-point helpers should be tested for all-zero, max, and ordinary values before being used by higher-level rounding.
