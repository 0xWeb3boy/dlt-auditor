# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-negative-other-33039`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-wrong-sign`

## Code Shape Summary

- Branches for negative operands manipulated encoded values directly instead of applying signed arithmetic over normalized magnitudes.

## Search Motifs

- other parameter is negative
- subtract instead of add absolute value
- signed integer subtract
- indent offset

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Normalize negative operands to magnitudes before subtraction and add exhaustive tests for positive and negative operand pairs.

## False Match Warnings

- No issue if callers never use negative operands.
- A wrong return value is lower risk without financial or authorization use.
