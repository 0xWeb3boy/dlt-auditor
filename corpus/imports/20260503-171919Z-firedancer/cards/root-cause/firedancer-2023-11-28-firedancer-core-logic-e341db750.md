# Root-Cause Card

## Metadata

- ID: `firedancer-2023-11-28-firedancer-core-logic-e341db750`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `elf-loader-memory-safety-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `loader-section-bounds-validation`

## Violated Invariant

- Invariant: An executable loader must prove every section, zero-fill span, and derived entrypoint stays within the loaded image before touching memory.

## Trust Boundary

- Boundary: Untrusted ELF/program bytes crossing into the loader.

## Attack Surface

- Entrypoint type: program loader / executable parser
- Sensitive sink: section-size accounting, rodata writes, and entrypoint resolution

## Impact Pattern

- Primary impact: memory safety
- Secondary impact: input validation

## Short Reusable Lesson

- The loader derived section sizes and loader-side memory operations from ELF metadata before proving the SHT_NOBITS and rodata spans were within the loaded image.
