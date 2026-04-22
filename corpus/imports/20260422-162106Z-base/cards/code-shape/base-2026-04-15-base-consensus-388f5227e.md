# Code-Shape Card

## Metadata

- ID: `base-2026-04-15-base-consensus-388f5227e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-coverage-gap`

## Code Shape Summary

- Short description of what the buggy code looked like: The scanner treated candidate discovery as mostly one-time state keyed by a scan watermark even though game state can change after first observation, and it encoded a classifier rule that treated a dual-proof no-challenge state as ignorable.

## Search Motifs

- Motif 1: challenge mode handled by a generic validation branch instead of the challenged case
- Motif 2: decision logic derives the target index or root from the wrong proof element
- Motif 3: retry or fallback state is dropped before the dispute path reaches a definitive decision

## Typical Asymmetry

- What was checked in one path but missing in another: The generic challenge machinery was present, but the branch for the specific challenged proof, root, or fallback transition reused the wrong validation rule or dropped the needed state.

## Patch Pattern

- What the fix changed structurally: Replace incremental watermark-based discovery with stateless rescanning when tracked objects can mutate after first observation, and convert previously skipped mixed states into explicit actionable classifications.

## False Match Warnings

- What looks similar but is often not a bug: This supports a security-sensitive detection and coverage hardening change, not a proven exploitable vulnerability.
