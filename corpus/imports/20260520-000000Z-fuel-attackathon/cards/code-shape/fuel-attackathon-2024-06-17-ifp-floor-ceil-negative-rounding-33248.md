# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-floor-ceil-negative-rounding-33248`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-negative-rounding-error`

## Code Shape Summary

- The signed fixed-point floor and ceil implementations mixed raw fixed-point units with integer units and used asymmetric negative branches.

## Search Motifs

- IFP floor negative input
- UFP32::from(1) unit
- ceil unreachable branch sign change
- floor subtracts when rounded

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Reimplement floor and ceil from mathematical definitions, using correct fixed-point unit constructors and tests for negative exact and fractional values.

## False Match Warnings

- No issue if the helper is not used for settlement-sensitive values.
- No issue if negative values are disallowed at type boundaries.
