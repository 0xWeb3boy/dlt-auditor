# Validation Card

## Metadata

- ID: `oasis-core-2020-08-25-oasis-core-cryptography-a7c5872e3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-timeout-state`

## What Confirmed The Issue

- Evidence 1: The fix adds explicit 'ClearRoundTimeout' handling to 'emitEmptyBlock' when an executor pool has a scheduled timeout, then threads returned errors through callers so transition code aborts if cleanup fails.
- Evidence 2: The source finding states the invariant explicitly: Round-timeout state must stay consistent with the active executor round; when an empty block ends or transitions a round, any previously scheduled timeout for that round should be cleared before commitments are reset and the new state proceeds.

## What Could Have Invalidated It

- Compensating control 1: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
- Compensating control 2: Not a match if old and new state coordinates are guaranteed equivalent for every reachable transition.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
- Caution 2: Not a match if old and new state coordinates are guaranteed equivalent for every reachable transition.
