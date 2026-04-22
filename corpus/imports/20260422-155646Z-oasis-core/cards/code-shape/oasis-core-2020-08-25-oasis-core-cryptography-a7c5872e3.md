# Code-Shape Card

## Metadata

- ID: `oasis-core-2020-08-25-oasis-core-cryptography-a7c5872e3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-timeout-state`

## Code Shape Summary

- Short description of what the buggy code looked like: A round-transition helper ('emitEmptyBlock') did not perform the same timeout-state cleanup that the finalization path already treated as part of normal round lifecycle management. As a result, a previously armed timeout could remain in persistent state when commitments were reset via the empty-block path.

## Search Motifs

- Motif 1: stale state reused across round, epoch, or restart boundaries
- Motif 2: update path bypasses the same validation as fresh admission
- Motif 3: lifecycle cleanup tied to the wrong transition marker

## Typical Asymmetry

- What was checked in one path but missing in another: The nominal path updated state correctly, but restart, timeout, overwrite, or lifecycle-transition paths left stale or mismatched state behind.

## Patch Pattern

- What the fix changed structurally: The fix adds explicit 'ClearRoundTimeout' handling to 'emitEmptyBlock' when an executor pool has a scheduled timeout, then threads returned errors through callers so transition code aborts if cleanup fails.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
