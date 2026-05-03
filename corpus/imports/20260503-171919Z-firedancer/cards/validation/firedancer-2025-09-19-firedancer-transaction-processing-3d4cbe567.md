# Validation Card

## Metadata

- ID: `firedancer-2025-09-19-firedancer-transaction-processing-3d4cbe567`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `stack-buffer-overflow`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says "fix buffer overflows by fd_txn_parse".
- Evidence 2: Both changed call sites replace stack fd_txn_t output storage with aligned uchar txn_mem[FD_TXN_MAX_SZ].

## What Could Have Invalidated It

- Compensating control 1: No fd_txn_parse contract or documentation is provided to prove the exact required output size.
- Compensating control 2: No malformed transaction proof of concept is provided.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No fd_txn_parse contract or documentation is provided to prove the exact required output size.
- Caution 2: No malformed transaction proof of concept is provided.
