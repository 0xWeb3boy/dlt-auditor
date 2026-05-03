# Root-Cause Card

## Metadata

- ID: `firedancer-2025-09-19-firedancer-transaction-processing-3d4cbe567`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `stack-buffer-overflow`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `parser-output-buffer-sizing`

## Violated Invariant

- Invariant: Callers must allocate parser output buffers to the parser’s maximum contract size, not the apparent size of one parsed view type.

## Trust Boundary

- Boundary: Transaction bytes crossing into a parser that writes structured output.

## Attack Surface

- Entrypoint type: transaction parser call site
- Sensitive sink: stack-local parser output buffer

## Impact Pattern

- Primary impact: memory corruption
- Secondary impact: none

## Short Reusable Lesson

- The call site handed a parser a stack-local object rather than a maximum-sized output buffer, even though the parser contract could write more bytes.
