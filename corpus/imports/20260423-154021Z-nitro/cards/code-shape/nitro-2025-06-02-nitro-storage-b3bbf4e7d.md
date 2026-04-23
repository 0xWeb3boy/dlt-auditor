# Code-Shape Card

## Metadata

- ID: `nitro-2025-06-02-nitro-storage-b3bbf4e7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The provided evidence supports that this patch implements previously missing delayed-message accumulation and accumulator checks in native-mode MEL. It does not, by itself, establish that the prior behavior was a proven exploitable vulnerability rather than an incomplete or unfinished validation path.

## Search Motifs

- Motif 1: validation functions return success without reconstructing accumulators or indexes they depend on
- Motif 2: placeholder state update code is replaced by real accumulator reconstruction in later fixes
- Motif 3: delayed-message validators begin tracking explicit context objects only after hardening patches

## Typical Asymmetry

- What was checked in one path but missing in another: The code treated cached, lazily created, or non-finalized state as if it were authoritative, while later validation or cleanup logic depended on stronger finalized-state guarantees.

## Patch Pattern

- What the fix changed structurally: Replace placeholder state/update and always-success validation code with explicit accumulator reconstruction, indexed context tracking, and real checks.

## False Match Warnings

- What looks similar but is often not a bug: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
