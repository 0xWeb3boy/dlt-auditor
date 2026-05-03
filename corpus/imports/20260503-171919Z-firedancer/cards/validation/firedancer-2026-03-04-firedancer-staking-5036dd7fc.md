# Validation Card

## Metadata

- ID: `firedancer-2026-03-04-firedancer-staking-5036dd7fc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `bounds-check-hardening`

## What Confirmed The Issue

- Evidence 1: Pre-patch calculate_reward_points_partitioned formed &runtime_stack->stakes.stake_points_result[ stake_delegation->idx ] without the supplied evidence showing a bounds check.
- Evidence 2: Post-patch code checks stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS and routes out-of-capacity entries to a local fd_calculated_stake_points_t buffer.

## What Could Have Invalidated It

- Compensating control 1: No supplied evidence proves an externally triggerable exploit path.
- Compensating control 2: No supplied evidence proves actual memory corruption, crash, or consensus divergence occurred pre-patch.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No supplied evidence proves an externally triggerable exploit path.
- Caution 2: No supplied evidence proves actual memory corruption, crash, or consensus divergence occurred pre-patch.
