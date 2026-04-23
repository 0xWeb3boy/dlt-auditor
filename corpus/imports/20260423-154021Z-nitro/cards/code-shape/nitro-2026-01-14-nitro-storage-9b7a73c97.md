# Code-Shape Card

## Metadata

- ID: `nitro-2026-01-14-nitro-storage-9b7a73c97`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-gating`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch adds an explicit MEL validated-message-count gate before block validation creates new work, adjusts MEL validator progress tracking, and changes MEL state hash construction.

## Search Motifs

- Motif 1: block validation checks execution progress but not validated delayed-message progress
- Motif 2: progress fields for extraction and validation drift independently until later patches tie them together
- Motif 3: commitment or state-hash code changes accompany new validation gates between subsystems

## Typical Asymmetry

- What was checked in one path but missing in another: The code treated cached, lazily created, or non-finalized state as if it were authoritative, while later validation or cleanup logic depended on stronger finalized-state guarantees.

## Patch Pattern

- What the fix changed structurally: Add an explicit validation-progress gate at the boundary between MEL extraction validation and block validation, and align related progress-tracking and commitment construction code with that boundary.

## False Match Warnings

- What looks similar but is often not a bug: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
