# Code-Shape Card

## Metadata

- ID: `nitro-2025-06-03-nitro-storage-300a695a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finality-boundary-handling`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch changes MEL startup and state-recovery logic to use the finalized parent-chain block when initializing delayed-message tracking. The evidence supports a reorg-resilience fix in message-extraction state handling, but it does not establish a concrete security vulnerability or exploit path.

## Search Motifs

- Motif 1: startup paths initialize tracking from current heads without consulting finalized state
- Motif 2: recovery code trims or seeds state based on read progress rather than finality boundaries
- Motif 3: later patches thread finalized parent block numbers through extraction or recovery APIs

## Typical Asymmetry

- What was checked in one path but missing in another: The code treated cached, lazily created, or non-finalized state as if it were authoritative, while later validation or cleanup logic depended on stronger finalized-state guarantees.

## Patch Pattern

- What the fix changed structurally: Thread an explicit finalized-boundary parameter through recovery code, and gate state initialization and trimming on finality rather than read-progress alone.

## False Match Warnings

- What looks similar but is often not a bug: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
