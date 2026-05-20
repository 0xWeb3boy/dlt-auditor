# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ufp-exp-returns-one-33170`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-exp-result-discarded`

## Code Shape Summary

- The Taylor-series intermediate was calculated and then ignored in favor of a constant return value.

## Search Motifs

- exp returns one
- res_minus_1 ignored
- Taylor series fixed point
- UFP exp constant

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Return one plus the computed series term and add tests for non-zero positive and negative exponent inputs.

## False Match Warnings

- No issue if exp is unused or explicitly documented as a stub.
- No issue if input is always zero and e^0 = 1 is expected.
