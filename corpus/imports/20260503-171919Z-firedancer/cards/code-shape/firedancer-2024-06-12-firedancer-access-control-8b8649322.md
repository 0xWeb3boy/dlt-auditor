# Code-Shape Card

## Metadata

- ID: `firedancer-2024-06-12-firedancer-access-control-8b8649322`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `secret-memory-hardening`

## Code Shape Summary

- The hardening adds a dedicated protected-memory allocator for key material and surfaces when an optional sandbox layer is unavailable, rather than proving an existing exploit path.

## Search Motifs

- Motif 1: guard-page allocator for secret buffers
- Motif 2: mlock/core-dump/fork protections around key memory
- Motif 3: runtime warning when optional sandbox layer unavailable

## Typical Asymmetry

- Secret-bearing memory is long-lived and high value, but generic allocator behavior does not automatically give it isolation properties.

## Patch Pattern

- Allocate secret memory inside guarded pages, disable swap/core-dump inheritance where possible, and expose missing sandbox layers to operators.

## False Match Warnings

- No concrete prior vulnerability or exploit path is shown.
- No attacker-controlled input path is connected to the changed code.
