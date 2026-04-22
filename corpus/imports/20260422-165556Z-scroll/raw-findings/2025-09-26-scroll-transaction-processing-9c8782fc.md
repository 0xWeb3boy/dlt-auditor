---
case_id: case_20250926_9c8782fc
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-09-26
source_refs:
  - git:9c8782fc1283ce95b7406039bbb621606b8a9044
  - "coordinator/internal/logic/provertask/batch_prover_task.go:344"
  - "crates/libzkp/src/tasks/batch.rs:205"
  - "coordinator/internal/logic/provertask/batch_prover_task.go:317"
  - "coordinator/internal/logic/provertask/prover_task.go:68"
bug_class: integrity-check-missing
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - proof-generation
  - validium
  - integrity-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a validium-task correctness fix, not a proven vulnerability fix. The coordinator now explicitly constructs a validium batch header for batch tasks, and the prover now sanity-checks that the header's recomputed hash matches the stored hash. That is an internal integrity/correctness improvement in the proving pipeline, but the snippets do not establish external attacker control or a concrete security impact.

## Observed Patch Facts

1. In `coordinator/internal/logic/provertask/batch_prover_task.go`, the patch adds `} else {`.

2. In `crates/libzkp/src/tasks/batch.rs`, the patch replaces `None` with `match &self.batch_header {`.

3. In `coordinator/internal/logic/provertask/batch_prover_task.go`, the patch replaces `return taskDetail, nil` with `taskDetail.BlobBytes = dbBatch.BlobBytes`.

4. In `coordinator/internal/logic/provertask/prover_task.go`, the patch replaces `// version get the version for the chain instance` with `return utils.Version(hardForkName, b.validiumMode())`.

## Project Context

The changed code sits primarily in `coordinator/internal/logic/provertask`, `coordinator/internal/logic`, `crates/libzkp/src/tasks`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `coordinator/internal/logic/provertask/chunk_prover_task.go`, `coordinator/internal/logic/provertask/bundle_prover_task.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `coordinator/internal/logic/provertask/chunk_prover_task.go`, `coordinator/internal/logic/provertask/bundle_prover_task.go`. The strongest project-level identifiers around this patch are `encoding`, `dbBatch`, `version`, and `CodecVersion`.

## Before/After Behavior

Before the patch, the shown coordinator logic populated blob-DA-related fields in the non-validium path, but the provided excerpt did not show a validium-specific branch that decoded and attached a validium batch header. In the Rust prover excerpt, the validium path asserted that blob-DA fields were absent and then ended without the later header/hash check. After the patch, the coordinator adds a validium branch that decodes `dbBatch.BatchHeader`, sets its hash from `dbBatch.Hash`, and stores it in `taskDetail.BatchHeader`; the prover now requires a validium header variant and asserts that the recomputed batch hash matches the hash stored in that header.

# Root Cause

The validium-specific batch-task path appears to have been incompletely assembled: the coordinator-side code did not show explicit validium header population in this path, and the prover-side validium path did not yet enforce header/hash consistency. That supports a mode-specific task-construction bug or missing invariant check, not a demonstrated exploitable security flaw.

## Walkthrough

1. `BatchProverTask.getBatchTaskDetail` creates a batch task and already has a non-validium path that decodes a DA batch header and fills blob-DA-related fields.

2. The patch adds a separate validium `else` branch in the same function.

3. In that branch, the coordinator derives a codec from the task version, decodes a validium batch header from `dbBatch.BatchHeader`, returns an error on decode failure, sets the header hash from `dbBatch.Hash`, and stores the header in `taskDetail.BatchHeader`.

4. On the Rust side, the validium path still asserts that blob-DA fields are absent.

5. The Rust code now also matches `self.batch_header` as `BatchHeaderV::Validium` and asserts that `h.header.batch_hash()` equals `h.batch_hash`, turning header/hash mismatch into an immediate failure.

6. A separate `BaseProverTask.version` change delegates to `utils.Version(hardForkName, b.validiumMode())`, but the excerpt alone does not prove that this changed behavior rather than refactoring existing logic.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| coordinator/internal/logic/provertask/batch_prover_task.go | 305 | Coordinator-side construction of batch proving tasks; now branches for validium mode and populates a validium batch header instead of only blob-DA fields. |
| coordinator/internal/logic/provertask/batch_prover_task.go | 344 | Validium-specific header decode and hash assignment before sending the proving task downstream. |
| coordinator/internal/logic/provertask/prover_task.go | 56 | Version/domain selection for prover tasks; now centralized through `utils.Version(..., validiumMode())` so validium tasks use the intended protocol version. |
| crates/libzkp/src/tasks/batch.rs | 199 | Prover-side sanity check that a validium task has no blob-DA fields and that the header-derived batch hash matches the coordinator-provided batch hash. |

## Code Snippets

## Snippet 1

Context: `coordinator/internal/logic/provertask/batch_prover_task.go:344` (changes signature or replay validation logic)

Before
```go
taskDetail.KzgProof = &message.Byte48{Big: hexutil.Big(*new(big.Int).SetBytes(dbBatch.BlobDataProof[112:160]))}
		taskDetail.KzgCommitment = &message.Byte48{Big: hexutil.Big(*new(big.Int).SetBytes(dbBatch.BlobDataProof[64:112]))}
	}
```
After
```go
taskDetail.KzgProof = &message.Byte48{Big: hexutil.Big(*new(big.Int).SetBytes(dbBatch.BlobDataProof[112:160]))}
		taskDetail.KzgCommitment = &message.Byte48{Big: hexutil.Big(*new(big.Int).SetBytes(dbBatch.BlobDataProof[64:112]))}
	} else {
		log.Debug("Apply validium mode for batch proving task")
		codec := cutils.FromVersion(version)
		batchHeader, decodeErr := codec.DABatchForTaskFromBytes(dbBatch.BatchHeader)
		if decodeErr != nil {
			return nil, fmt.Errorf("failed to decode batch header version %d: %w", dbBatch.CodecVersion, decodeErr)
```

## Snippet 2

Context: `crates/libzkp/src/tasks/batch.rs:205` (changes signature or replay validation logic)

Before
```rust
"domain=validium has no blob-da"
            );
            None
        };
```
After
```rust
"domain=validium has no blob-da"
            );

            match &self.batch_header {
                BatchHeaderV::Validium(h) => assert_eq!(
                    h.header.batch_hash(),
                    h.batch_hash,
                    "calculated batch hash match which from coordinator"
```

## Snippet 3

Context: `coordinator/internal/logic/provertask/batch_prover_task.go:317` (changes persisted or aggregate state handling)

Before
```go
}

	dbBatchCodecVersion := encoding.CodecVersion(dbBatch.CodecVersion)
	switch dbBatchCodecVersion {
	case encoding.CodecV3, encoding.CodecV4, encoding.CodecV6, encoding.CodecV7, encoding.CodecV8:
	default:
		return taskDetail, nil
	}
```
After
```go
}

	taskDetail.BlobBytes = dbBatch.BlobBytes
	if !bp.validiumMode() {
		dbBatchCodecVersion := encoding.CodecVersion(dbBatch.CodecVersion)
		switch dbBatchCodecVersion {
		case encoding.CodecV3, encoding.CodecV4, encoding.CodecV6, encoding.CodecV7, encoding.CodecV8:
		default:
```

## Snippet 4

Context: `coordinator/internal/logic/provertask/prover_task.go:68` (changes a sensitive control or state-update path)

Before
```go
}

// version get the version for the chain instance
//
// TODO: This is not foolproof and does not cover all scenarios.
func (b *BaseProverTask) version(hardForkName string) (uint8, error) {
	var domain, stfVersion uint8
```
After
```go
}

func (b *BaseProverTask) version(hardForkName string) (uint8, error) {
	return utils.Version(hardForkName, b.validiumMode())
}

// validiumMode induce different behavior in task generation:
// + skip the point_evaluation part in batch task
```

# Fix Pattern

Add explicit mode-specific task assembly for validium and a fail-fast sanity check that the decoded header and stored batch hash remain consistent.

## How It Was Fixed

The coordinator now has an explicit validium path that decodes and attaches a validium batch header instead of only following the blob-DA-oriented logic. The prover-side validium path now checks that the provided header is the expected validium variant and that its recomputed batch hash matches the stored hash. The visible version-helper change should be treated as supporting context only, because the supplied excerpts do not prove a semantic change there.

# Why It Matters

1. It reduces coordinator/prover disagreement about which validium batch is being proved.

2. It makes malformed or inconsistent validium task data fail early in the proving workflow.

3. It separates validium handling from blob-DA-specific assumptions.

4. The evidence supports internal correctness or integrity hardening, not a confirmed external security bug.

# Evidence Notes

The strongest support comes from `coordinator/internal/logic/provertask/batch_prover_task.go`, where a new validium branch decodes `dbBatch.BatchHeader`, sets its hash, and stores it in `taskDetail.BatchHeader`, and from `crates/libzkp/src/tasks/batch.rs`, where the validium path now asserts header/hash consistency. The `BaseProverTask.version` change in `coordinator/internal/logic/provertask/prover_task.go` is visible, but the provided snippets do not show enough to claim a meaningful behavior change from that refactor alone. No supplied evidence shows attacker control over these inputs, prior acceptance of invalid proofs, or impact beyond the coordinator-to-prover proving flow. Protocol security invariant: For validium batch proving, the coordinator and prover should agree on the same validium batch header and its batch hash, and validium tasks should not rely on blob-DA-specific fields. Verification notes: The diff does not prove that an external attacker can directly control the malformed validium batch data reaching this path. The patch shows internal coordinator/prover consistency checks, not proof that invalid proofs were previously accepted on-chain. No confidentiality, privilege-escalation, or key-compromise impact is evidenced here. The new Rust assertion is fail-fast validation, but the provided snippets do not establish a concrete denial-of-service boundary beyond the proving workflow. The commit message and hunks are consistent with a functional validium-batch generation fix; security impact remains unproven from this evidence alone. No tests, crash traces, or exploit scenario are provided. Only partial diff hunks are available, so prior behavior and reachability must be inferred conservatively. The evidence does not show whether `dbBatch` contents are externally attacker-controlled or only internally generated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integrity-check-missing`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, proof-generation, validium, integrity-hardening`

The patch is mostly a validium batch-construction correctness fix, but the supplied evidence also shows a concrete integrity hardening change in a security-sensitive proving path: the prover now rejects validium tasks whose decoded header hash does not match the stored batch hash, and the coordinator now explicitly decodes and attaches the validium batch header instead of relying on blob-DA-oriented behavior. That supports retaining this as security-hardening rather than a confirmed security-fix. The evidence does not prove attacker control, prior acceptance of invalid proofs, or a concrete exploitable impact.

## Security Evidence

1. Rust validium task handling now asserts that the recomputed header `batch_hash()` equals the coordinator-provided `batch_hash`, adding an explicit integrity check.
2. Coordinator batch-task generation now has a dedicated validium branch that decodes `dbBatch.BatchHeader` and attaches it to `taskDetail.BatchHeader`.
3. Decode errors in the validium header path now fail task generation instead of allowing malformed header data to pass further into the proving flow.
4. The modified code sits in batch proving / proof task generation, which is a cryptographic integrity-sensitive path in a blockchain system.

## Missing Evidence

1. No evidence shows that `dbBatch.BatchHeader` or `dbBatch.Hash` are attacker-controlled across an external trust boundary.
2. No supplied patch text proves that invalid proofs were previously accepted, submitted, or could bypass downstream verification.
3. No advisory, test, incident report, or exploit scenario demonstrates a real-world security impact.
4. The excerpts do not prove whether the pre-patch behavior caused only correctness/liveness failures versus a true security failure.

## Claim Boundaries

1. Supported claim: the commit hardens validium batch-task integrity by enforcing header/hash consistency and explicit validium header construction.
2. Unsupported claim: this patch fixes a proven exploitable vulnerability or prior invalid-proof acceptance bug.
3. Unsupported claim: the evidence shows external attacker reachability, replay abuse, privilege escalation, or confidentiality impact.
4. Impact should be bounded to coordinator/prover task integrity hardening based on the supplied patch evidence.
