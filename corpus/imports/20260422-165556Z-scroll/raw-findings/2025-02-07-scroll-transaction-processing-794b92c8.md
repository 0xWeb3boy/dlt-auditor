---
case_id: case_20250207_794b92c8
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-02-07
source_refs:
  - git:794b92c800bf867a96dadc118f8e33938f5fbd43
  - "coordinator/internal/logic/provertask/chunk_prover_task.go:143"
  - "coordinator/internal/logic/provertask/bundle_prover_task.go:145"
  - "coordinator/internal/logic/provertask/batch_prover_task.go:145"
bug_class: missing-compatibility-check
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - prover-coordinator
  - fork-compatibility
  - fail-closed
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch re-enables a fork-compatibility check in three prover-task assignment paths. The evidence shows the coordinator previously had this guard commented out and now rejects assignment when the prover does not advertise support for the task's required hard fork. That establishes a real correctness and safety check was restored, but the provided material does not prove a concrete security vulnerability or downstream acceptance of invalid proofs.

## Observed Patch Facts

1. In `coordinator/internal/logic/provertask/chunk_prover_task.go`, the patch replaces `//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {` with `if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {`.

2. In `coordinator/internal/logic/provertask/bundle_prover_task.go`, the patch replaces `//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {` with `if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {`.

3. In `coordinator/internal/logic/provertask/batch_prover_task.go`, the patch replaces `//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {` with `if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {`.

## Project Context

The changed code sits primarily in `coordinator/internal/logic/provertask`, `coordinator/internal/logic`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `coordinator/internal/logic/provertask/prover_task.go`, `coordinator/internal/logic/auth/login.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `coordinator/internal/logic/provertask/prover_task.go`, `coordinator/internal/logic/auth/login.go`. The strongest project-level identifiers around this patch are `hardForkName`, `taskCtx`, `HardForkNames`, and `prover`.

## Before/After Behavior

Before the patch, each affected `Assign` function computed the task's required `hardForkName`, but the subsequent `taskCtx.HardForkNames[hardForkName]` compatibility check was commented out in `chunk_prover_task.go`, `bundle_prover_task.go`, and `batch_prover_task.go`. After the patch, that check is active in all three files. On mismatch, the code recovers the active attempt, logs an "incompatible prover version" error, and returns an internal failure instead of continuing assignment.

# Root Cause

A required fork-compatibility guard in the prover-task assignment flow had been disabled by commented-out code across the chunk, bundle, and batch assignment paths.

## Walkthrough

1. In `coordinator/internal/logic/provertask/chunk_prover_task.go`, the code derives `hardForkName` for the task and already treats lookup failure as fatal.

2. Immediately after that, the patch restores an active `if _, ok := taskCtx.HardForkNames[hardForkName]; !ok { ... }` check that had been commented out before.

3. On chunk-task mismatch, the code now calls `recoverActiveAttempts`, logs the incompatibility, and returns an internal failure.

4. `coordinator/internal/logic/provertask/bundle_prover_task.go` receives the same restoration of the `HardForkNames` membership check in its `Assign` path.

5. `coordinator/internal/logic/provertask/batch_prover_task.go` receives the same restoration in its `Assign` path as well.

6. Across all three paths, the visible effect is consistent: unsupported fork assignments are now rejected instead of proceeding past the assignment gate.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| coordinator/internal/logic/provertask/chunk_prover_task.go | 143 | chunk proof task assignment now rejects provers that do not support the task's required hard fork |
| coordinator/internal/logic/provertask/bundle_prover_task.go | 145 | bundle proof task assignment now enforces hard-fork compatibility before continuing |
| coordinator/internal/logic/provertask/batch_prover_task.go | 145 | batch proof task assignment now enforces the same prover hard-fork eligibility check |

## Code Snippets

## Snippet 1

Context: `coordinator/internal/logic/provertask/chunk_prover_task.go:143` (changes signature or replay validation logic)

Before
```go
}

	//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {
	//	cp.recoverActiveAttempts(ctx, chunkTask)
	//	log.Error("incompatible prover version",
	//		"requisite hard fork name", hardForkName,
	//		"prover hard fork name", taskCtx.HardForkNames,
	//		"task_id", chunkTask.Hash)
```
After
```go
}

	if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {
		cp.recoverActiveAttempts(ctx, chunkTask)
		log.Error("incompatible prover version",
			"requisite hard fork name", hardForkName,
			"prover hard fork name", taskCtx.HardForkNames,
			"task_id", chunkTask.Hash)
```

## Snippet 2

Context: `coordinator/internal/logic/provertask/bundle_prover_task.go:145` (changes signature or replay validation logic)

Before
```go
}

	//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {
	//	bp.recoverActiveAttempts(ctx, bundleTask)
	//	log.Error("incompatible prover version",
	//		"requisite hard fork name", hardForkName,
	//		"prover hard fork name", taskCtx.HardForkNames,
	//		"task_id", bundleTask.Hash)
```
After
```go
}

	if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {
		bp.recoverActiveAttempts(ctx, bundleTask)
		log.Error("incompatible prover version",
			"requisite hard fork name", hardForkName,
			"prover hard fork name", taskCtx.HardForkNames,
			"task_id", bundleTask.Hash)
```

## Snippet 3

Context: `coordinator/internal/logic/provertask/batch_prover_task.go:145` (changes signature or replay validation logic)

Before
```go
}

	//if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {
	//	bp.recoverActiveAttempts(ctx, batchTask)
	//	log.Error("incompatible prover version",
	//		"requisite hard fork name", hardForkName,
	//		"prover hard fork name", taskCtx.HardForkNames,
	//		"task_id", batchTask.Hash)
```
After
```go
}

	if _, ok := taskCtx.HardForkNames[hardForkName]; !ok {
		bp.recoverActiveAttempts(ctx, batchTask)
		log.Error("incompatible prover version",
			"requisite hard fork name", hardForkName,
			"prover hard fork name", taskCtx.HardForkNames,
			"task_id", batchTask.Hash)
```

# Fix Pattern

Restore a fail-closed eligibility check at task-assignment entry points so advertised prover capabilities are validated before assignment continues.

## How It Was Fixed

The fix uncommented and reinstated the `HardForkNames` membership guard in the chunk, bundle, and batch `Assign` functions. Each path now checks whether the prover supports the required `hardForkName` and, if not, recovers the active attempt, logs the mismatch, and returns `ErrCoordinatorInternalFailure`.

# Why It Matters

1. It prevents assigning work to a prover that does not advertise support for the task's required fork.

2. It restores consistent fail-closed behavior across chunk, bundle, and batch assignment flows.

3. It reduces the chance that incompatible proving work proceeds after assignment.

4. The evidence supports restored compatibility enforcement, not a proven exploitable vulnerability.

# Evidence Notes

The supplied diff evidence is limited to three assignment functions in `coordinator/internal/logic/provertask`. In each file, the same compatibility block was present as commented-out code before the patch and active code after the patch. The active block checks `taskCtx.HardForkNames[hardForkName]`, calls `recoverActiveAttempts(...)`, logs "incompatible prover version", and returns an internal failure. Related context shows this is part of prover-task coordination, but the evidence does not show whether later verification stages would also reject mismatched-fork work or whether any invalid proof could previously be accepted. Protocol security invariant: The coordinator should assign chunk, bundle, and batch proving tasks only to provers whose advertised `HardForkNames` include the task's required `hardForkName`. If the fork is unsupported, assignment should fail and the active attempt should be recovered. Verification notes: The patch does not prove that an incompatible prover could previously cause acceptance of an invalid proof on chain or by the verifier. It does not show whether later verification stages already rejected mismatched-fork proofs, which would limit impact to availability or operational integrity. It does not establish attacker reachability beyond whatever entities can register or operate a prover. It does not show data corruption, key compromise, or direct authentication bypass; the change is a capability/compatibility gate in task assignment. No test changes or execution results were provided. The evidence is sufficient to confirm restored assignment-time compatibility checking. The evidence is not sufficient to confirm exploitability or concrete security impact beyond assignment correctness and operational safety. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-compatibility-check`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, prover-coordinator, fork-compatibility, fail-closed`

The patch clearly restores a fail-closed compatibility check in three prover-task assignment paths, preventing a prover from receiving work for an unsupported hard fork. That is a security-sensitive hardening change in a blockchain proof-coordination boundary because it removes an exposed risky condition in validator/prover eligibility enforcement. However, the diff alone does not prove that incompatible provers could previously cause acceptance of invalid proofs or any concrete exploit, so this is best kept as security hardening rather than a confirmed vulnerability fix.

## Security Evidence

1. Previously disabled fork-support check was re-enabled in chunk, bundle, and batch assignment paths.
2. On mismatch, the code now aborts assignment, recovers active attempts, and returns an internal failure.
3. The guarded condition validates advertised prover capabilities against the task's required hard fork.
4. The change sits in prover-task coordination logic, a security-sensitive protocol enforcement path.

## Missing Evidence

1. No evidence shows that mismatched provers could previously submit proofs that were accepted.
2. No downstream verifier or on-chain acceptance path is shown.
3. No attacker model or reachability evidence is provided for malicious prover registration or abuse.
4. No tests or incident details demonstrate concrete exploitability or user impact.

## Claim Boundaries

1. Supported claim: the commit restores assignment-time hard-fork compatibility enforcement.
2. Supported claim: the change hardens a fail-open or disabled eligibility check in a sensitive workflow.
3. Unsupported claim: this patch proves a prior consensus break, invalid-proof acceptance, or direct exploit.
4. Unsupported claim: the impact exceeded operational/protocol integrity hardening based on the provided diff alone.
