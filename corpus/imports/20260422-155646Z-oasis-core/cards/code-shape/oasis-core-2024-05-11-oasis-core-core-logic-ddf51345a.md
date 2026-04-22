# Code-Shape Card

## Metadata

- ID: `oasis-core-2024-05-11-oasis-core-core-logic-ddf51345a`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## Code Shape Summary

- Short description of what the buggy code looked like: Dealer::new used unchecked u8 arithmetic for a derived protocol parameter ('dy = 2 * threshold'), allowing overflow instead of rejecting an unrepresentable value.

## Search Motifs

- Motif 1: unchecked arithmetic in consensus or security-sensitive state update
- Motif 2: overflow near sentinel values or maximum type bounds
- Motif 3: fail-open math instead of checked or fail-closed behavior

## Typical Asymmetry

- What was checked in one path but missing in another: The state transition assumed arithmetic stayed within bounds, but the implementation did not enforce that bound at the sink.

## Patch Pattern

- What the fix changed structurally: The fix moved overflow handling into 'Dealer::new' by changing the API to return Result and rejecting thresholds whose doubled value does not fit in u8 via 'Error::ThresholdTooLarge'. Related call sites were updated to use the validated constructor contract.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if earlier invariants prove the operands stay far below the type bound in every reachable state.
