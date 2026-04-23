# Code-Shape Card

## Metadata

- ID: `nitro-2024-02-05-nitro-core-logic-6b420cb12`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-state-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The supported finding is a business-logic guard addition: the patch teaches the assertion confirmation flow to stop when the target assertion is locally known to be challenged.

## Search Motifs

- Motif 1: confirmation logic delays or retries without rechecking challenge membership before the final call
- Motif 2: state predicates such as IsChallenged are added only after finalization bugs are found
- Motif 3: sensitive actions rely on stale snapshots of challenge sets across wait windows

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Add explicit state guards around a sensitive action, including re-checking after delay windows before issuing the final side effect.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
