# Validation Card

## Metadata

- ID: `oasis-core-2020-01-31-oasis-core-staking-956168c04`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## What Confirmed The Issue

- Evidence 1: The fix changed the freeze-end calculation from raw addition to guarded logic. It imports 'registry', checks whether 'epoch + penalty.FreezeInterval' would overflow 'uint64', and records 'registry.FreezeForever' instead of allowing wraparound.
- Evidence 2: The source finding states the invariant explicitly: When duplicate-vote evidence is processed, the recorded validator freeze end time should preserve the configured penalty and must not wrap if 'epoch + FreezeInterval' exceeds the representable epoch range.

## What Could Have Invalidated It

- Compensating control 1: Not a match if earlier invariants prove the operands stay far below the type bound in every reachable state.
- Compensating control 2: Not a match if the arithmetic is already checked or saturating before the security-sensitive assignment.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if earlier invariants prove the operands stay far below the type bound in every reachable state.
- Caution 2: Not a match if the arithmetic is already checked or saturating before the security-sensitive assignment.
