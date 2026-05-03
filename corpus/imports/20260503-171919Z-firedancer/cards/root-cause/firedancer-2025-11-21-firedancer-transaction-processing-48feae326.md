# Root-Cause Card

## Metadata

- ID: `firedancer-2025-11-21-firedancer-transaction-processing-48feae326`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `out-of-bounds-read`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `terminator-aware-length-validation`

## Violated Invariant

- Invariant: Parsers whose API requires a trailing byte must be given a backing span that includes that byte or use a length-safe variant.

## Trust Boundary

- Boundary: Operator- or peer-supplied JSON/config bytes crossing into a generic parser API.

## Attack Surface

- Entrypoint type: config or JSON parser
- Sensitive sink: parser read past end of the provided buffer

## Impact Pattern

- Primary impact: memory safety
- Secondary impact: none

## Short Reusable Lesson

- The code passed a parser a length-limited buffer even though the specific API still required one byte beyond the logical payload.
