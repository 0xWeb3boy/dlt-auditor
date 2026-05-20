# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-impl-dependency-name-collision-32973`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `compiler-symbol-identity-collision`

## Code Shape Summary

- A compiler dependency map used a synthesized human-readable name as a uniqueness key for multiple impl blocks.

## Search Motifs

- decl_name impl block dependency
- DependentSymbol overwritten
- multiple self impl same type
- concatenation of declaration names

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Use compiler-generated unique IDs for impl dependency keys and add tests for colliding declaration-name sequences.

## False Match Warnings

- No issue if impl blocks receive unique node ids independent of declaration names.
- A collision that always hard-fails compilation has liveness impact but less security risk.
