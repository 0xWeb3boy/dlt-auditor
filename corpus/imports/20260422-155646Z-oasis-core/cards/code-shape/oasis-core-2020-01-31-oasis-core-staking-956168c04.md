# Code-Shape Card

## Metadata

- ID: `oasis-core-2020-01-31-oasis-core-staking-956168c04`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## Code Shape Summary

- Short description of what the buggy code looked like: Unchecked integer addition when deriving 'nodeStatus.FreezeEndTime' from the current epoch and the configured freeze interval.

## Search Motifs

- Motif 1: unchecked arithmetic in consensus or security-sensitive state update
- Motif 2: overflow near sentinel values or maximum type bounds
- Motif 3: fail-open math instead of checked or fail-closed behavior

## Typical Asymmetry

- What was checked in one path but missing in another: The state transition assumed arithmetic stayed within bounds, but the implementation did not enforce that bound at the sink.

## Patch Pattern

- What the fix changed structurally: The fix changed the freeze-end calculation from raw addition to guarded logic. It imports 'registry', checks whether 'epoch + penalty.FreezeInterval' would overflow 'uint64', and records 'registry.FreezeForever' instead of allowing wraparound.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if earlier invariants prove the operands stay far below the type bound in every reachable state.
