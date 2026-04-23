# Code-Shape Card

## Metadata

- ID: `nitro-2022-04-07-nitro-transaction-processing-b5cf8b667`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `module-root-mismatch`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch changes challenge-related machine loading so the validator can select a machine by module root instead of implicitly using the latest machine directory, and it adds an explicit module-root equality check before using the loaded machine.

## Search Motifs

- Motif 1: loaders default to latest or implicit directories instead of an explicit root parameter
- Motif 2: module-root equality is checked only after downstream work has already begun
- Motif 3: challenge setup relies on artifact selection conventions rather than measured identity

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Replace implicit default artifact selection with identifier-based selection, then add a fail-closed validation check at use time.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
