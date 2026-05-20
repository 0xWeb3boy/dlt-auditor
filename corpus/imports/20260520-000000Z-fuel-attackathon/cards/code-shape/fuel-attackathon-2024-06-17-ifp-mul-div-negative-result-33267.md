# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-negative-result-33267`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`

## Code Shape Summary

- The same self-only sign expression was duplicated across fixed-point multiply and divide implementations.

## Search Motifs

- ifp64 multiply divide non_negative
- self.non_negative only
- negative times positive returns positive
- IFP128 IFP256 sign

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Replace self-only sign expressions with XOR-style operand sign comparison across all IFP widths.

## False Match Warnings

- No issue if using an unaffected version with sign-matrix tests.
- No issue if all values are unsigned by design.
