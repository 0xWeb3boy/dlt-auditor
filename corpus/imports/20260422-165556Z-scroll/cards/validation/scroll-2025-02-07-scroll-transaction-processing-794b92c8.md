# Validation Card

## Metadata

- ID: `scroll-2025-02-07-scroll-transaction-processing-794b92c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-compatibility-check`

## What Confirmed The Issue

- Evidence 1: In `coordinator/internal/logic/provertask/chunk_prover_task.go`, the patch replaces `//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {` with `if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {`.
- Evidence 2: In `coordinator/internal/logic/provertask/bundle_prover_task.go`, the patch replaces `//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {` with `if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {`.
- Evidence 3: In `coordinator/internal/logic/provertask/batch_prover_task.go`, the patch replaces `//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {` with `if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {`.

## What Could Have Invalidated It

- Compensating control 1: If downstream verifiers or provers reject mismatched tasks before any stateful effect, similar bugs may be operational rather than security-relevant.
- Compensating control 2: Presence of a capability map alone is not enough; the key issue is whether every assignment path enforces it before dispatch.
- Compensating control 3: The evidence supports safety gating restoration, not a demonstrated invalid-proof acceptance bug.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If downstream verifiers or provers reject mismatched tasks before any stateful effect, similar bugs may be operational rather than security-relevant.
- Caution 2: Presence of a capability map alone is not enough; the key issue is whether every assignment path enforces it before dispatch.
- Caution 3: The evidence supports safety gating restoration, not a demonstrated invalid-proof acceptance bug.
