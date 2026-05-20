# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-ceil-double-increment-32700`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-rounding-double-adjustment`

## Code Shape Summary

- The wrapper rounded the underlying value, then applied a second from(1) adjustment when it detected a change.

## Search Motifs

- ceil underlying then add one
- double increase underlying
- round calls ceil
- fixed point ceil wrapper

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Make ceil a single adjustment from truncation to the next integer and add boundary tests for positive and negative fractional inputs.

## False Match Warnings

- No issue if the second adjustment is guarded by a distinct unit conversion that does not change value.
- Pure presentation rounding is lower risk without settlement use.
