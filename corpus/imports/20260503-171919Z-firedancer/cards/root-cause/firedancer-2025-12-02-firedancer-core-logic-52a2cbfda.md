# Root-Cause Card

## Metadata

- ID: `firedancer-2025-12-02-firedancer-core-logic-52a2cbfda`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `content-length-integer-overflow`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `narrowing-conversion-bound-check`

## Violated Invariant

- Invariant: Parsed Content-Length values must fit the destination integer type before allocation, copy, or read sizing uses them.

## Trust Boundary

- Boundary: HTTP header text crossing into RPC/genesis content-length parsing.

## Attack Surface

- Entrypoint type: HTTP header parser
- Sensitive sink: buffer sizing and read length derived from narrowed content length

## Impact Pattern

- Primary impact: out of bounds read
- Secondary impact: none

## Short Reusable Lesson

- The parser accepted any successfully parsed unsigned value, then later narrowed it to a smaller integer type without an upper-bound check.
