# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-small-type-alu-overflow-33331`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `narrow-integer-overflow-check-missing`

## Code Shape Summary

- The standard library implemented pow without the manual checks present in other narrow-type arithmetic helpers.

## Search Motifs

- types less than u64 overflow
- pow implementation lacks check
- u8 stored as u64
- manual overflow checks in add but not pow

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Add declared-width overflow checks to pow and test u8, u16, and u32 results at max boundaries.

## False Match Warnings

- No issue if the operation is performed on true u64/u256 where VM overflow semantics match the type.
- No issue if the compiler inserts declared-width checks before return and storage.
