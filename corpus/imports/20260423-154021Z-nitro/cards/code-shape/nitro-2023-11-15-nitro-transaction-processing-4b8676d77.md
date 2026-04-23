# Code-Shape Card

## Metadata

- ID: `nitro-2023-11-15-nitro-transaction-processing-4b8676d77`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-index-derivation`

## Code Shape Summary

- Short description of what the buggy code looked like: The supplied diff supports a correctness fix in the staker state-provider path: proof and machine-hash lookups now derive the message index from batch metadata, equal-batch ranges are rejected, and missing batch-count data is surfaced as a catch-up condition. The evidence does not establish an exploitable vulnerability, invalid proof acceptance, or consensus impact.

## Search Motifs

- Motif 1: proof helpers accept caller-provided indices when batch metadata is available
- Motif 2: equal-batch or empty-range cases are treated as ordinary ranges
- Motif 3: missing batch counts are surfaced as catch-up conditions only in later hardening patches

## Typical Asymmetry

- What was checked in one path but missing in another: Callers had enough metadata to continue challenge or proof construction, but not enough authoritative context to bind indices, ranges, or fallback state to the intended dispute object.

## Patch Pattern

- What the fix changed structurally: Replace direct or ambiguous index inputs with indices derived from authoritative batch metadata, add stricter argument validation, and translate sync-lag conditions into an explicit error.

## False Match Warnings

- What looks similar but is often not a bug: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
