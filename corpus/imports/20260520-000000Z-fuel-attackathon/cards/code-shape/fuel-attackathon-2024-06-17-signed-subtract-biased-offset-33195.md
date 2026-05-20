# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-biased-offset-33195`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-formula-violation`

## Code Shape Summary

- Hand-written branches for biased signed integers used different formulas instead of one representation-preserving rule.

## Search Motifs

- a.underlying - b.underlying + indent
- signed integers subtract all widths
- incorrect calculations in subtraction
- biased offset branch

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Implement subtraction around a single canonical biased-offset formula and test all sign combinations across widths.

## False Match Warnings

- No issue if exhaustive branch tests show equivalence to mathematical subtraction.
- Pure documentation mismatch is not enough without executable wrong results.
