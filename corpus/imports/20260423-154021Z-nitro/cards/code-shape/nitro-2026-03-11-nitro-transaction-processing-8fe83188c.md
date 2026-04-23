# Code-Shape Card

## Metadata

- ID: `nitro-2026-03-11-nitro-transaction-processing-8fe83188c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-integrity-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch appears to remove a MEL-specific gap where delayed-message sequencing could skip an accumulator continuity/reorg check and adds MEL support code needed to perform that check.

## Search Motifs

- Motif 1: one execution mode skips an accumulator continuity check that another mode performs
- Motif 2: reorg-detection helpers are missing from new backends or execution engines until later patches
- Motif 3: consistency checks migrate from optional branches into common sequencing code

## Typical Asymmetry

- What was checked in one path but missing in another: The code treated cached, lazily created, or non-finalized state as if it were authoritative, while later validation or cleanup logic depended on stronger finalized-state guarantees.

## Patch Pattern

- What the fix changed structurally: Move a previously conditional consistency check into the common execution path and add backend support methods so all modes can enforce the same invariant.

## False Match Warnings

- What looks similar but is often not a bug: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
