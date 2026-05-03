# Validation Card

## Metadata

- ID: `firedancer-2024-03-18-firedancer-transaction-processing-b39f4b4a3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vm-syscall-bounds-validation`

## What Confirmed The Issue

- Evidence 1: Commit body explicitly says sol_log_data was susceptible to buffer overflow and DOS attacks.
- Evidence 2: Commit body describes a fixed overflow when a large slice_cnt is passed.

## What Could Have Invalidated It

- Compensating control 1: No full sol_log_data implementation diff is provided.
- Compensating control 2: No concrete before/after code for the slice_cnt overflow fix is shown.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No full sol_log_data implementation diff is provided.
- Caution 2: No concrete before/after code for the slice_cnt overflow fix is shown.
