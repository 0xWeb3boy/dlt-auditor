# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-small-int-pow-overflow-33227`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `small-width-pow-overflow`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `type-width-overflow-checks`

## Violated Invariant

- Arithmetic helpers for narrow integer types must reject results outside the declared type width, even if the VM stores them in a wider word.

## Trust Boundary

- Boundary: `contract-input->standard-library-math`
- Entrypoint type: `library-function`
- Sensitive sink: `pow result used as token amount or SDK-returned value`

## Attack Surface

- Choose base and exponent that exceed u8, u16, or u32 bounds.
- Trigger pow in financial calculations.

## Exploit Preconditions

- Narrow types are represented as u64 at runtime.
- pow lacks manual overflow checks for the declared narrow type.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Language runtimes that widen narrow types still need source-type overflow checks in standard-library arithmetic.
