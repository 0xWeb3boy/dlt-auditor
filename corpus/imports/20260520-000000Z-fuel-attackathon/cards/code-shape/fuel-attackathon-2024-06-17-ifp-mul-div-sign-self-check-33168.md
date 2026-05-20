# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-sign-self-check-33168`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`

## Code Shape Summary

- The result sign condition used self.non_negative in both operands, making the negative-result case unreachable.

## Search Motifs

- self.non_negative && !self.non_negative
- multiply divide sign
- IFP result always positive
- divisor.non_negative missing

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Compute sign from self versus other or divisor, and add sign-matrix tests for multiply and divide.

## False Match Warnings

- No issue in unsigned fixed-point math.
- No issue if callers reject negative operands before reaching multiply or divide.
