# Validation Card

## Metadata

- ID: `oasis-core-2024-05-11-oasis-core-core-logic-ddf51345a`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## What Confirmed The Issue

- Evidence 1: The fix moved overflow handling into 'Dealer::new' by changing the API to return Result and rejecting thresholds whose doubled value does not fit in u8 via 'Error::ThresholdTooLarge'. Related call sites were updated to use the validated constructor contract.
- Evidence 2: The source finding states the invariant explicitly: CHURP dealer construction must not silently wrap the derived Y-degree when computing 2 * threshold. If the doubled threshold is not representable in u8, construction should fail so the derived polynomial degree and verification-matrix dimensions stay consistent with the input threshold.

## What Could Have Invalidated It

- Compensating control 1: Not a match if earlier invariants prove the operands stay far below the type bound in every reachable state.
- Compensating control 2: Not a match if the arithmetic is already checked or saturating before the security-sensitive assignment.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if earlier invariants prove the operands stay far below the type bound in every reachable state.
- Caution 2: Not a match if the arithmetic is already checked or saturating before the security-sensitive assignment.
