# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ccp-zero-fill-undercharged-32465`
- Bug family: `resource_accounting_and_limits`
- Bug class: `undercharged-memory-zero-fill`

## Code Shape Summary

- The opcode loaded code, charged using source contract size, then zero-filled the caller-selected destination length when the source slice was empty.

## Search Motifs

- code_copy offset greater than code length
- zero fill after copy_from_slice
- charge contract size not requested length
- CCP cheaper than MCL

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Charge CCP for the requested output bytes or align zero-fill accounting with memory-clear gas costs, with tests for out-of-range offsets.

## False Match Warnings

- No issue if the charged cost scales with the destination length including zero fill.
- Small bounded copies with equal charge and write length are not this pattern.
