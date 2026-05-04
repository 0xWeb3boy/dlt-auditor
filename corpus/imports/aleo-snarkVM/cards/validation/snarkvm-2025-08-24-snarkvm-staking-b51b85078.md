# Validation Card

## Metadata

- ID: `snarkvm-2025-08-24-snarkvm-staking-b51b85078`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `deployment-upgrade-validation`

## What Confirmed The Issue

- The verifier now iterates existing functions and rejects missing functions in the new program.
- The V10 path checks that existing function inputs match exactly.

## What Could Have Invalidated It

- `Stack::check_upgrade_is_valid` already enforced the same invariant for every deployment.
- The changed path is unreachable for stored programs.

## Severity Guidance

- Expected impact band: consensus_state_consistency
- Expected severity band: medium_or_low

## False-Positive Cautions

- Another upgrade validation phase already checks function presence and full input/output equality.
- The consensus version is below the activation point for the new invariant.
