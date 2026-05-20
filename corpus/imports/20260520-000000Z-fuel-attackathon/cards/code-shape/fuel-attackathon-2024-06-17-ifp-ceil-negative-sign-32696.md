# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-ceil-negative-sign-32696`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-rounding-sign-misbinding`

## Code Shape Summary

- The return struct reused self.non_negative after computing a rounded value whose sign should have changed.

## Search Motifs

- ceil == UFP64::from(1)
- non_negative from self
- round returns ceil
- IFP ceil sign flag

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Derive non_negative from the rounded mathematical result and add tests for negative values rounded across zero.

## False Match Warnings

- No issue if callers ignore the sign flag and use a canonical numeric representation.
- A display-only rounding bug has lower severity without asset accounting use.
