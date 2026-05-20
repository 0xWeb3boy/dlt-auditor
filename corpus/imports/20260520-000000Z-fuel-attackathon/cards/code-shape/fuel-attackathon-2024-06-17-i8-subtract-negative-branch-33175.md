# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-i8-subtract-negative-branch-33175`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-i8-subtraction-branch-error`

## Code Shape Summary

- The last conditional branch in I8 subtract mixed underlying ordering with the wrong indent adjustment.

## Search Motifs

- I8 subtract last branch
- Self::indent add instead of subtract
- -2 - -3
- biased signed subtraction

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Fix the branch adjustment and add tests for negative-minus-negative operands around the indent boundary.

## False Match Warnings

- No issue if the implementation delegates to a shared tested signed subtraction primitive.
- A single-width bug has lower scope if larger signed types are not affected.
