# Validation Card

## Metadata

- ID: `reth-2023-06-06-reth-storage-c0fb169da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-error-handling`

## What Confirmed The Issue

- Commit subject explicitly says execution and sender errors now trigger unwind behavior.
- Receipt-root and logs-bloom mismatches are reclassified from execution errors to validation errors.

## What Could Have Invalidated It

- No downstream pipeline snippet proves the old error types actually skipped unwind handling
- No proof that invalid state was previously committed or made durable

## Severity Guidance

- Expected impact band: consensus_or_protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No downstream pipeline snippet proves the old error types actually skipped unwind handling
- No proof that invalid state was previously committed or made durable
