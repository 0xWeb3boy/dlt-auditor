# Validation Card

## Metadata

- ID: `agave-2026-03-16-agave-consensus-be02fe6ee0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation-failure-masking`

## What Confirmed The Issue

- The fix changes replay_err.or(verify_err) to replay_res.and(verify_res).
- The combined result gates mark_dead_slot behavior in ReplayStage.

## What Could Have Invalidated It

- Either validation path is intentionally redundant and independently sufficient.
- The combined result cannot influence voting, rooting, or dead-slot handling.

## Severity Guidance

- Expected impact band: `consensus validation hardening`
- Expected severity band: `medium`
- Rationale: Masking validation errors in replay-stage logic is consensus-sensitive, but no exploit, vote-safety bypass, or finalization impact was demonstrated.

## False-Positive Cautions

- Not every Result::or is wrong; flag only when both validations must succeed.
- Avoid claiming finality compromise without evidence that the masked error reaches voting or rooting.
