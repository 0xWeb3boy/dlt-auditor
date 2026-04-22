# Validation Card

## Metadata

- ID: `scroll-2023-08-18-scroll-transaction-processing-767a2cbf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-transition`

## What Confirmed The Issue

- Evidence 1: In `coordinator/internal/logic/submitproof/proof_receiver.go`, the patch replaces `if status == types.ProvingTaskFailed && m.checkIsTaskSuccess(ctx, hash, proofMsg.Type) {` with `if m.checkIsTaskSuccess(ctx, hash, proofMsg.Type) {`.
- Evidence 2: In `common/version/version.go`, the patch replaces `var tag = "v4.1.73"` with `var tag = "v4.1.74"`.
- Evidence 3: `updateProofStatus` runs inside the coordinator proof submission path and starts a transaction.

## What Could Have Invalidated It

- Compensating control 1: If later status messages are append-only telemetry and cannot alter the canonical task status, a similar pattern may be benign.
- Compensating control 2: If the state transition is wrapped in a stronger idempotency guard or compare-and-swap on terminal status, the downgrade risk is lower.
- Compensating control 3: The evidence supports lifecycle integrity hardening, not a demonstrated proof-verification bypass.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If later status messages are append-only telemetry and cannot alter the canonical task status, a similar pattern may be benign.
- Caution 2: If the state transition is wrapped in a stronger idempotency guard or compare-and-swap on terminal status, the downgrade risk is lower.
- Caution 3: The evidence supports lifecycle integrity hardening, not a demonstrated proof-verification bypass.
