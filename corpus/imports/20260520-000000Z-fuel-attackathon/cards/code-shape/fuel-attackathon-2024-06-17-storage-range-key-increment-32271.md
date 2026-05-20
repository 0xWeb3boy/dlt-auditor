# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-storage-range-key-increment-32271`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `storage-range-iteration-off-by-one`

## Code Shape Summary

- A range helper advanced the mutable key cursor more often than the number of requested slots required.

## Search Motifs

- contract_state_range key.increase
- storage range helper loop
- SCWQ SRWQ SWWQ contiguous slots
- valid storage read errors

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Increment the key exactly once per processed slot and add boundary tests for range reads, inserts, and removes near max keys.

## False Match Warnings

- No issue if overflow is returned only when the requested range truly exceeds key space.
- Single-slot storage accessors are not this pattern.
