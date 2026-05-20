# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-zero-sign-change-33303`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `noncanonical-zero-sign`

## Code Shape Summary

- The add implementation changed sign in the equality case instead of normalizing zero to a canonical sign.

## Search Motifs

- 3 plus -3 negative zero
- self.underlying > other.underlying
- should use >=
- IFP add sign change

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Use an equality-aware branch and canonicalize all zero results to non_negative true, with tests for x + -x.

## False Match Warnings

- No issue if zero sign is never observable and all comparisons canonicalize.
- No issue if the library intentionally supports signed zero with documented semantics.
