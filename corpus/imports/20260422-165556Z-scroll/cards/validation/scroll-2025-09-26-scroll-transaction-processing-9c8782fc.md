# Validation Card

## Metadata

- ID: `scroll-2025-09-26-scroll-transaction-processing-9c8782fc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integrity-check-missing`

## What Confirmed The Issue

- Evidence 1: In `coordinator/internal/logic/provertask/batch_prover_task.go`, the patch adds `} else {`.
- Evidence 2: In `crates/libzkp/src/tasks/batch.rs`, the patch replaces `None` with `match &self.batch_header {`.
- Evidence 3: In `coordinator/internal/logic/provertask/batch_prover_task.go`, the patch replaces `return taskDetail, nil` with `taskDetail.BlobBytes = dbBatch.BlobBytes`.

## What Could Have Invalidated It

- Compensating control 1: If downstream verification always recomputes and binds the same header hash, a similar task-building bug may remain a correctness-only issue.
- Compensating control 2: Header-serialization refactors are not enough; the real signal is whether the stored hash and canonical header can diverge before proving.
- Compensating control 3: The evidence supports integrity hardening, not a demonstrated forged-batch exploit.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If downstream verification always recomputes and binds the same header hash, a similar task-building bug may remain a correctness-only issue.
- Caution 2: Header-serialization refactors are not enough; the real signal is whether the stored hash and canonical header can diverge before proving.
- Caution 3: The evidence supports integrity hardening, not a demonstrated forged-batch exploit.
