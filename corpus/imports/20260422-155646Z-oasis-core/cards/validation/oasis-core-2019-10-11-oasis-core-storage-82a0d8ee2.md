# Validation Card

## Metadata

- ID: `oasis-core-2019-10-11-oasis-core-storage-82a0d8ee2`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`

## What Confirmed The Issue

- Evidence 1: The patch adds a locked-pointer check to the LRU eviction loop, refactors commit into a fallible 'try_commit_node(..., locked_ptr)' path, and passes the dereferenced pointer through remote merge commit. On lock conflict, the merge stops retaining additional nodes. The commit message also states item ordering was adjusted to reduce eviction pressure on the active path and that dereference now errors instead of silently proceeding.
- Evidence 2: The source finding states the invariant explicitly: During remote subtree merge and dereference, cache admission must not evict the node currently being dereferenced; if capacity prevents preserving that pointer, the operation should stop or fail rather than continue with inconsistent in-memory tree state.

## What Could Have Invalidated It

- Compensating control 1: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
- Compensating control 2: Not a match if old and new state coordinates are guaranteed equivalent for every reachable transition.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
- Caution 2: Not a match if old and new state coordinates are guaranteed equivalent for every reachable transition.
