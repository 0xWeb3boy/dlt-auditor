# Code-Shape Card

## Metadata

- ID: `base-2026-01-22-base-transaction-processing-13a095daa`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-cache-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: An inverted condition in the cached-execution guard caused the validator to key rejection off a successful transaction-prefix comparison instead of a mismatch. The iterator-signature and cache-hydration changes appear to support the corrected flow rather than show a separate root cause.

## Search Motifs

- Motif 1: cache or retry reuse happens without rechecking canonical chain state
- Motif 2: request identity is treated as sufficient even though the historical state coordinate can change
- Motif 3: stale checkpoint, execution, or proof data is reused across parent-context changes

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that an existing request or cache entry matched a local identifier, but did not recheck that the cached state still matched the canonical chain state being acted on.

## Patch Pattern

- What the fix changed structurally: Correct the cache-validation predicate so the system fails closed on detected mismatch before reusing cached execution results.

## False Match Warnings

- What looks similar but is often not a bug: Supported: the patch hardens cached-execution reuse by rejecting reuse on transaction-prefix mismatch.
