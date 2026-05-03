# Root-Cause Card

## Metadata

- ID: `firedancer-2023-09-29-firedancer-access-control-7cbb71919`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `parser-bounds-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `buffer-length-threading`

## Violated Invariant

- Invariant: A packet parser must thread the actual backing-buffer length through every decode step and derive payload spans from validated parsed size fields.

## Trust Boundary

- Boundary: Untrusted shred bytes crossing into the validator packet parser.

## Attack Surface

- Entrypoint type: network packet parser
- Sensitive sink: payload-size derivation and buffer-backed structure parsing

## Impact Pattern

- Primary impact: input validation hardening
- Secondary impact: none

## Short Reusable Lesson

- The parser relied on protocol-derived size information without consistently threading the actual buffer length through shred decoding and payload accounting.
