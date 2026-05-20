# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-small-int-pow-overflow-33227`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `small-width-pow-overflow`

## Code Shape Summary

- pow for u8/u16/u32 multiplied in a wide runtime representation without clamping to the source type's max value.

## Search Motifs

- u8 pow no overflow check
- u16 u32 compiled to u64
- math.sw pow narrow integer
- VM does not trap narrow overflow

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Add explicit checked multiplication or max-bound checks in narrow-type pow implementations and tests for overflow boundaries.

## False Match Warnings

- No issue if the operation returns a Result or panics before exceeding the declared type max.
- u64 and u256 behavior may be covered by separate VM checks.
