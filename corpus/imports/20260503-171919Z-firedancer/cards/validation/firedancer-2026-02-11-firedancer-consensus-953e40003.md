# Validation Card

## Metadata

- ID: `firedancer-2026-02-11-firedancer-consensus-953e40003`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `missing-bounds-check-buffer-overflow`

## What Confirmed The Issue

- Evidence 1: Patch adds `caller_account->serialized_data_len != post_len` guard before the CPI copy-back memcpy.
- Evidence 2: Mismatch now returns `FD_EXECUTOR_INSTR_ERR_ACC_DATA_TOO_SMALL` instead of proceeding to copy.

## What Could Have Invalidated It

- Compensating control 1: No proof of remote exploitability or attacker-controlled code execution.
- Compensating control 2: No evidence of privilege bypass or access-control failure.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No proof of remote exploitability or attacker-controlled code execution.
- Caution 2: No evidence of privilege bypass or access-control failure.
