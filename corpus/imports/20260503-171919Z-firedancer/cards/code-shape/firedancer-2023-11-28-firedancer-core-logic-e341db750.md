# Code-Shape Card

## Metadata

- ID: `firedancer-2023-11-28-firedancer-core-logic-e341db750`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `elf-loader-memory-safety-hardening`

## Code Shape Summary

- The loader derived section sizes and loader-side memory operations from ELF metadata before proving the SHT_NOBITS and rodata spans were within the loaded image.

## Search Motifs

- Motif 1: SHT_NOBITS or zero-fill size trusted before bounds check
- Motif 2: loader-side memcpy/memset driven by section headers
- Motif 3: entrypoint or helper table offsets validated after use

## Typical Asymmetry

- The attacker controls executable metadata, but the loader treats section descriptors as authoritative for memory writes and reads.

## Patch Pattern

- Track loaded-size separately from declared size, tighten ELF validation, and gate every loader-side memory operation on validated section bounds.

## False Match Warnings

- No proof that malformed ELF input is attacker-controlled in a deployed configuration.
- No concrete crash, exploit, or vulnerability demonstration is supplied.
