# Code-Shape Card

## Metadata

- ID: `nitro-2023-06-16-nitro-transaction-processing-edf0a0ec8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-challenge-metadata`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports a challenge-initiation correctness bug, not a clearly established vulnerability. The patch changes level-zero edge construction to use the challenged assertion's `creationInfo` instead of previously using `prevCreationInfo` for commitment inputs, and it threads that metadata back to the caller.

## Search Motifs

- Motif 1: challenge setup reads prevCreationInfo or parent-derived metadata instead of the challenged object's record
- Motif 2: commitments are assembled from nearby assertion state rather than the target assertion itself
- Motif 3: patches add early fetching of authoritative creation metadata before edge construction

## Typical Asymmetry

- What was checked in one path but missing in another: Callers had enough metadata to continue challenge or proof construction, but not enough authoritative context to bind indices, ranges, or fallback state to the intended dispute object.

## Patch Pattern

- What the fix changed structurally: Replace indirectly inferred or parent-derived state with authoritative creation metadata from the challenged assertion when building challenge-sensitive inputs.

## False Match Warnings

- What looks similar but is often not a bug: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
