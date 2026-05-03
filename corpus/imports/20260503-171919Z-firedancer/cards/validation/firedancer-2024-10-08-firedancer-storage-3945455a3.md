# Validation Card

## Metadata

- ID: `firedancer-2024-10-08-firedancer-storage-3945455a3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `runtime-program-admissibility`

## What Confirmed The Issue

- Evidence 1: Commit subject is "implementing program blacklist".
- Evidence 2: `fd_runtime_pre_execute_check()` now calls `fd_executor_check_executable_program_accounts(txn_ctx)` before loading/executing accounts.

## What Could Have Invalidated It

- Compensating control 1: Exact blacklist entries and matching logic are not shown.
- Compensating control 2: No end-to-end attacker-controlled exploit path is shown.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Exact blacklist entries and matching logic are not shown.
- Caution 2: No end-to-end attacker-controlled exploit path is shown.
