# Validation Card

## Metadata

- ID: `firedancer-2025-09-15-firedancer-transaction-processing-4507bc93b`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `buffer-overflow`

## What Confirmed The Issue

- Evidence 1: Commit subject says "replay: fix buffer overflow in scheduler".
- Evidence 2: fd_sched_fec_ingest now checks block->fec_buf_sz >= block->fec_buf_soff before using the residual length for memmove.

## What Could Have Invalidated It

- Compensating control 1: Complete body of the oversized-buffer rejection path is not shown.
- Compensating control 2: No proof is provided that malformed FEC/residual state is attacker-controllable.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: Complete body of the oversized-buffer rejection path is not shown.
- Caution 2: No proof is provided that malformed FEC/residual state is attacker-controllable.
