# Validation Card

## Metadata

- ID: `firedancer-2025-03-05-firedancer-consensus-97c08c390`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-bound-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject calls this a vote program overflow patch.
- Evidence 2: Patch clamps confirmation_count to MAX_LOCKOUT_HISTORY before fd_ulong_pow2_up.

## What Could Have Invalidated It

- Compensating control 1: No proof that normal execution can produce confirmation_count greater than MAX_LOCKOUT_HISTORY.
- Compensating control 2: No concrete exploit path or attacker-controlled input flow is shown.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No proof that normal execution can produce confirmation_count greater than MAX_LOCKOUT_HISTORY.
- Caution 2: No concrete exploit path or attacker-controlled input flow is shown.
