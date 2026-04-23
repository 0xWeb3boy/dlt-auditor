# Code-Shape Card

## Metadata

- ID: `nitro-2022-02-17-nitro-transaction-processing-8ad394df3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-boundary-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch fixes correctness bugs in validator challenge setup and machine initialization around genesis-relative indexing and boundary handling. The shown evidence supports dispute-path correctness hardening, but it does not establish a concrete exploitable vulnerability.

## Search Motifs

- Motif 1: genesis-relative offsets are reconstructed ad hoc during challenge setup
- Motif 2: boundary cases such as zero, final, or empty ranges are handled by generic code paths
- Motif 3: challenge machine state is derived before validating the requested range against genesis context

## Typical Asymmetry

- What was checked in one path but missing in another: Callers had enough metadata to continue challenge or proof construction, but not enough authoritative context to bind indices, ranges, or fallback state to the intended dispute object.

## Patch Pattern

- What the fix changed structurally: Thread canonical genesis context through challenge construction, handle valid boundary special cases explicitly, and add fail-closed checks before deriving machine state from challenge metadata.

## False Match Warnings

- What looks similar but is often not a bug: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
