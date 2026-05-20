# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ufp32-fract-underflow-33233`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-fraction-underflow`

## Code Shape Summary

- The fractional calculation used subtractive masking that is always below the subtrahend after shifting.

## Search Motifs

- UFP32 fract underflow
- left shift then subtract u32::max
- IFP64 fract reverts
- ceil uses fract

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Replace subtractive masking with correct fractional extraction and add tests that fract and ceil work for representative valid inputs.

## False Match Warnings

- No issue if the helper uses bit masks or modulo without underflow.
- No issue if all callers catch the revert and preserve liveness.
