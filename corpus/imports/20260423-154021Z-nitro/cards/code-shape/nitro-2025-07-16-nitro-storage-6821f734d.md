# Code-Shape Card

## Metadata

- ID: `nitro-2025-07-16-nitro-storage-6821f734d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation-hardening`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports a consensus-sensitive correctness hardening change in MEL state handling, not a confirmed vulnerability fix. The patch makes delayed-message validation tolerate a missing cached accumulator by rebuilding it from persisted partials, adds a batched head-state save path, and narrows backlog trimming to finalized-and-read entries.

## Search Motifs

- Motif 1: validators assume cached accumulators are populated instead of reconstructing them from disk
- Motif 2: pruning decisions depend on head state that is updated before validation completes
- Motif 3: patches add accumulator rebuilds from persisted partials and tighter pruning guards

## Typical Asymmetry

- What was checked in one path but missing in another: The code treated cached, lazily created, or non-finalized state as if it were authoritative, while later validation or cleanup logic depended on stronger finalized-state guarantees.

## Patch Pattern

- What the fix changed structurally: Re-derive cached validation state from canonical persisted data before use, and make pruning and head-state updates follow explicit safety conditions.

## False Match Warnings

- What looks similar but is often not a bug: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
