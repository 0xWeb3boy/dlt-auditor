# Validation Card

## Metadata

- ID: `firedancer-2025-02-06-firedancer-transaction-processing-4d173a092`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting-mismatch`

## What Confirmed The Issue

- Evidence 1: `fd_pack_compute_cost` gains an explicit `opt_loaded_accounts_data_cost` output.
- Evidence 2: Bank-side accounting changes from a single consumed CU value to separate execution and account-data CU values.

## What Could Have Invalidated It

- Compensating control 1: No concrete exploit scenario is shown.
- Compensating control 2: No evidence shows replay protection or signature validation was affected.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No concrete exploit scenario is shown.
- Caution 2: No evidence shows replay protection or signature validation was affected.
