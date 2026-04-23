# Code-Shape Card

## Metadata

- ID: `nitro-2024-11-07-nitro-transaction-processing-ae1d18a4c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-proof-generation-hardening`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports a correctness fix in BoLD challenge handling: virtual-range block challenges were previously handled with a boolean shortcut that did not provide the concrete finished state to use, and the commit message says this could lead to looking up a block index for which no real block existed and producing incorrect inclusion proofs.

## Search Motifs

- Motif 1: helpers return booleans like useFinishedMachine instead of the actual state object required by the sink
- Motif 2: boundary-case challenge logic is duplicated across proof and hash generation entry points
- Motif 3: virtual range handling gains a concrete virtualState API after correctness bugs are found

## Typical Asymmetry

- What was checked in one path but missing in another: Callers had enough metadata to continue challenge or proof construction, but not enough authoritative context to bind indices, ranges, or fallback state to the intended dispute object.

## Patch Pattern

- What the fix changed structurally: Replace a boolean boundary-case shortcut with an API that returns the concrete fallback state, and use that state at each proof/hash generation entry point.

## False Match Warnings

- What looks similar but is often not a bug: If a later proof verifier deterministically recomputes the same boundary state from canonical inputs, similar cases may stay local correctness bugs.
