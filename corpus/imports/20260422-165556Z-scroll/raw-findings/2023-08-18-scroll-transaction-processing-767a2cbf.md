---
case_id: case_20230818_767a2cbf
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-08-18
source_refs:
  - git:767a2cbfdf6a566ea6991505a13e06a7ef09bfdd
  - "coordinator/internal/logic/submitproof/proof_receiver.go:311"
  - "common/version/version.go:7"
bug_class: improper-state-transition
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - proof-processing
  - state-integrity
  - replay-sensitive
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence shows a focused state-machine fix in the coordinator proof receiver: after a chunk or batch is already verified, the code now skips later chunk/batch-level status updates for all incoming statuses instead of only `ProvingTaskFailed`. That supports a post-verification integrity/correctness hardening claim. The provided diff does not establish an attacker-driven vulnerability, cryptographic bypass, or consensus-impacting exploit.

## Observed Patch Facts

1. In `coordinator/internal/logic/submitproof/proof_receiver.go`, the patch replaces `if status == types.ProvingTaskFailed && m.checkIsTaskSuccess(ctx, hash, proofMsg.Type) {` with `if m.checkIsTaskSuccess(ctx, hash, proofMsg.Type) {`.

2. In `common/version/version.go`, the patch replaces `var tag = "v4.1.73"` with `var tag = "v4.1.74"`.

## Project Context

The changed code sits primarily in `coordinator/internal/logic/submitproof`, `coordinator/internal/logic`, `common/version`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `coordinator/internal/logic/provertask/batch_prover_task.go`, `coordinator/internal/logic/provertask/prover_task.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `coordinator/internal/logic/provertask/prover_task.go`, `coordinator/internal/logic/provertask/chunk_prover_task.go`. The strongest project-level identifiers around this patch are `hash`, `status`, `batch`, and `proof`.

## Before/After Behavior

Before the patch, `updateProofStatus` returned early on `checkIsTaskSuccess(...)` only when the incoming status was `types.ProvingTaskFailed`, so other statuses could still continue into chunk/batch-level mutation even after the task was already verified. After the patch, the early return applies whenever `checkIsTaskSuccess(...)` is true, regardless of the incoming status, so verified tasks are treated as terminal for subsequent chunk/batch-level updates in this path.

# Root Cause

The terminal-state check in `updateProofStatus` was too narrow. It only blocked post-verification updates for one status (`ProvingTaskFailed`), leaving other later status paths able to continue after the task had already succeeded.

## Walkthrough

1. `updateProofStatus` runs inside the coordinator proof submission path and starts a transaction.

2. Within that transaction, it updates prover-task status first.

3. Before the patch, the next guard was `status == types.ProvingTaskFailed && m.checkIsTaskSuccess(...)`, so only failed-status updates were skipped after prior verification.

4. After the patch, the guard became just `m.checkIsTaskSuccess(...)`, removing the status restriction.

5. As a result, once the task is already verified, later calls return early before chunk/batch-level status updates proceed.

6. The separate change in `common/version/version.go` is only a version tag bump and does not affect the fix analysis.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| coordinator/internal/logic/submitproof/proof_receiver.go | 298 | Coordinator proof submission transaction that updates prover-task status and chunk/batch proof or proving state |
| coordinator/internal/logic/submitproof/proof_receiver.go | 311 | Terminal-state guard preventing further proof/proving-status mutation once a chunk or batch is already verified |
| common/version/version.go | 7 | Release tag bump only; metadata, not part of the security behavior |

## Code Snippets

## Snippet 1

Context: `coordinator/internal/logic/submitproof/proof_receiver.go:311` (changes signature or replay validation logic)

Before
```go
// if the block batch has proof verified, so the failed status not update block batch proving status
		if status == types.ProvingTaskFailed && m.checkIsTaskSuccess(ctx, hash, proofMsg.Type) {
			log.Info("update proof status ProvingTaskFailed skip because other prover have prove success", "hash", hash, "public key", proverPublicKey)
			return nil
		}
```
After
```go
// if the block batch has proof verified, so the failed status not update block batch proving status
		if m.checkIsTaskSuccess(ctx, hash, proofMsg.Type) {
			log.Info("update proof status skip because this chunk / batch has been verified", "hash", hash, "public key", proverPublicKey)
			return nil
		}
```

## Snippet 2

Context: `common/version/version.go:7` (changes a sensitive control or state-update path)

Before
```go
)

var tag = "v4.1.73"

var commit = func() string {
```
After
```go
)

var tag = "v4.1.74"

var commit = func() string {
```

# Fix Pattern

Broaden a terminal-state guard so that once success has been reached, all later aggregate-state mutations in that path are skipped.

## How It Was Fixed

The patch removed the `status == types.ProvingTaskFailed` condition from the `checkIsTaskSuccess(...)` early return in `updateProofStatus` and updated the log message to reflect the broader skip condition.

# Why It Matters

1. It prevents later status processing from changing chunk/batch-level state after verification.

2. It reduces inconsistent state from duplicate, delayed, or out-of-order proof results.

3. The evidence supports state-integrity hardening, but not a proven security exploit.

# Evidence Notes

The key evidence is the single behavioral hunk in `coordinator/internal/logic/submitproof/proof_receiver.go` where the guard changed from `if status == types.ProvingTaskFailed && m.checkIsTaskSuccess(...)` to `if m.checkIsTaskSuccess(...)`. The surrounding function context shows this guard sits before further chunk/batch-level status handling inside a transaction. `common/version/version.go` is only a tag bump. No provided evidence demonstrates attacker control, unauthorized proof acceptance, cryptographic verification failure, or chain-level impact. Protocol security invariant: Once a chunk or batch is already verified, later proof-status processing should not mutate the chunk/batch-level proof or proving state. Verification notes: The patch does not show a cryptographic verification bypass. The patch does not prove unauthorized proof acceptance by an attacker. The patch does not establish chain-level consensus failure or fund impact. The evidence supports post-verification state-integrity protection, not a full exploit narrative. It is not proven whether the triggering condition was a benign race between honest provers or an adversarial replay/ordering scenario. The diff clearly supports an improper state-transition fix in coordinator status handling. The evidence does not show whether the original issue was exploitable or only a race/correctness problem. No test changes or incident details are provided to validate a stronger security claim. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-state-transition`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, proof-processing, state-integrity, replay-sensitive`

The patch broadens a terminal-state guard in a proof-handling path so that once a chunk or batch is already verified, later proof-status processing no longer mutates aggregate proof/proving state. In a blockchain coordinator, that is a meaningful integrity hardening change in a security-sensitive workflow. However, the provided evidence does not prove an attacker-triggerable vulnerability, proof forgery, consensus break, or other concrete exploit, so this fits security hardening rather than a confirmed security fix.

## Security Evidence

1. The changed logic is in `updateProofStatus` within the coordinator proof submission path, not in metadata-only code.
2. The guard changed from blocking only `ProvingTaskFailed` after success to blocking all later status updates once `checkIsTaskSuccess(...)` is true.
3. The affected state is proof/proving status for a verified chunk or batch, which is integrity-sensitive and replay/order-sensitive in this subsystem.
4. The log message was updated to reflect a broader post-verification skip condition, matching the tightened behavior.

## Missing Evidence

1. No evidence shows attacker control over the triggering sequence versus a benign race between honest provers.
2. No test, incident, or advisory evidence demonstrates exploitable impact before the patch.
3. No patch evidence shows unauthorized proof acceptance, cryptographic verification bypass, or chain-level consensus impact.
4. No surrounding diff is provided to show what incorrect post-verification state mutation could concretely enable.

## Claim Boundaries

1. Treat this as post-verification state-integrity hardening, not a proven exploitable vulnerability.
2. Do not claim proof forgery, authentication bypass, or consensus failure from this patch alone.
3. Do not claim fund loss or attacker-controlled replay exploitation without additional evidence.
4. The version bump in `common/version/version.go` is release metadata and not part of the security behavior.
