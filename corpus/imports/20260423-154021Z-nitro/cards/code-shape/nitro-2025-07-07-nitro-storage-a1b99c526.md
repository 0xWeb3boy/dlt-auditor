# Code-Shape Card

## Metadata

- ID: `nitro-2025-07-07-nitro-storage-a1b99c526`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-state-retention`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch is well supported as a correctness/state-handling change in MEL delayed-message tracking. It replaces the older seen-unread deque flow with an explicitly initialized delayedMetaBacklog, stops silently creating missing tracking state during accumulation, and changes trimming logic to depend on finalized MEL state.

## Search Motifs

- Motif 1: tracking state is silently created on demand instead of explicitly initialized at startup
- Motif 2: cleanup code deletes backlog state based on local assumptions rather than finalized progress
- Motif 3: deque or seen/unread structures are replaced by explicit backlog objects in hardening patches

## Typical Asymmetry

- What was checked in one path but missing in another: The code treated cached, lazily created, or non-finalized state as if it were authoritative, while later validation or cleanup logic depended on stronger finalized-state guarantees.

## Patch Pattern

- What the fix changed structurally: Replace implicit or lazily created tracking state with an explicitly initialized backlog, and tie retention/cleanup to finalized state rather than local assumptions.

## False Match Warnings

- What looks similar but is often not a bug: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
