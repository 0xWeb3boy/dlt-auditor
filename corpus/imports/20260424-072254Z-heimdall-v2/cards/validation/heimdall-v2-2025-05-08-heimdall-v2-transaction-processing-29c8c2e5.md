# Validation Card

## Metadata

- ID: `heimdall-v2-2025-05-08-heimdall-v2-transaction-processing-29c8c2e5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-continuity-validation`

## What Confirmed The Issue

- Evidence 1: direct checkpoint handling changed from `lastCheckpoint.EndBlock > msg.StartBlock` to exact `lastCheckpoint.EndBlock+1 != msg.StartBlock` rejection.
- Evidence 2: side-message checkpoint handling now returns on checkpoint-buffer read errors before buffer-dependent logic.

## What Could Have Invalidated It

- Compensating control 1: sparse checkpoints are explicitly valid and downstream consumers account for gaps.
- Compensating control 2: a downstream root-chain contract or proof verifier already enforces exact checkpoint continuity.

## Severity Guidance

- Expected impact band: checkpoint-integrity / protocol-invariant hardening.
- Expected severity band: medium.

## False-Positive Cautions

- Caution 1: do not claim a concrete chain split or root-chain compromise without exploit evidence.
- Caution 2: bridge processor cleanup is not standalone security evidence here.
