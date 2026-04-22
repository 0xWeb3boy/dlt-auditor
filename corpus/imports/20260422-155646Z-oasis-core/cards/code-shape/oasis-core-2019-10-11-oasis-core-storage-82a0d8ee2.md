# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-10-11-oasis-core-storage-82a0d8ee2`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`

## Code Shape Summary

- Short description of what the buggy code looked like: Eviction and commit logic in the remote merge path did not account for the pointer currently being dereferenced, so cache pressure could remove that active node during merge.

## Search Motifs

- Motif 1: stale state reused across round, epoch, or restart boundaries
- Motif 2: update path bypasses the same validation as fresh admission
- Motif 3: lifecycle cleanup tied to the wrong transition marker

## Typical Asymmetry

- What was checked in one path but missing in another: The nominal path updated state correctly, but restart, timeout, overwrite, or lifecycle-transition paths left stale or mismatched state behind.

## Patch Pattern

- What the fix changed structurally: The patch adds a locked-pointer check to the LRU eviction loop, refactors commit into a fallible 'try_commit_node(..., locked_ptr)' path, and passes the dereferenced pointer through remote merge commit. On lock conflict, the merge stops retaining additional nodes. The commit message also states item ordering was adjusted to reduce eviction pressure on the active path and that dereference now errors instead of silently proceeding.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
