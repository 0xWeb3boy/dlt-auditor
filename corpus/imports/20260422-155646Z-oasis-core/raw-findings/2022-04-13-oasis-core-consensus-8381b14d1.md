---
case_id: case_20220413_8381b14d1
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2022-04-13
source_refs:
  - git:8381b14d188e7b20bed200e5cf5e17a57f46edc4
  - "go/runtime/txpool/txpool.go:548"
  - "go/runtime/txpool/txpool.go:490"
  - "go/runtime/txpool/txpool.go:497"
  - "go/runtime/txpool/transaction.go:92"
bug_class: insufficient-resource-limits
impact_type:
  - denial-of-service
  - resource-exhaustion
confidence: medium
tags:
  - blockchain-core
  - txpool
  - admission-control
  - resource-control
  - sender-limit
  - dos-mitigation
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is a grounded txpool admission and error-reporting change, not a demonstrated vulnerability fix. The evidence shows that checked transactions now retain sender metadata, and schedule-queue insertion failures are mapped back into per-transaction results, but the supplied diff does not prove an exploitable denial-of-service condition or another concrete security flaw.

## Observed Patch Facts

1. In `go/runtime/txpool/txpool.go`, the patch replaces `for _, tx := range newTxs {` with `for i, tx := range newTxs {`.

2. In `go/runtime/txpool/txpool.go`, the patch replaces `newTxs := make([]*PendingCheckTransaction, 0, len(results))` with `notifySubmitter := func(i int) {`.

3. In `go/runtime/txpool/txpool.go`, the patch replaces `if !res.IsSuccess() {` with `newTxs := make([]*PendingCheckTransaction, 0, len(results))`.

4. In `go/runtime/txpool/transaction.go`, the patch adds `tx.sender = string(meta.Sender)`.

## Project Context

The changed code sits primarily in `go/runtime/txpool`, `go/runtime`, which anchors the finding in the `consensus` area of the project. Historical context from `go/runtime/txpool/schedule_queue_test.go`, `go/runtime/txpool/schedule_queue.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/runtime/txpool/schedule_queue_test.go`, `go/runtime/host/protocol/types.go`. The strongest project-level identifiers around this patch are `results`, `sender`, `range`, and `newTxs`. Nearby tests or test-like files include `go/runtime/client/tests/tester.go`, `go/runtime/host/tests/tester.go`.

## Before/After Behavior

Before the patch, `setChecked` copied only `Priority`, so txpool transactions did not retain `Sender` or `SenderSeq` from `CheckTxMetadata`. In `checkTxBatch`, checked transactions were queued for scheduling without preserving a stable mapping back to the original batch entry, and a `schedulerQueue.add` failure was logged but not clearly returned to the submitter. After the patch, `setChecked` also stores sender fields and assigns a unique hash-derived fallback sender when metadata is absent; `checkTxBatch` tracks `batchIndices`, uses indexed iteration over `newTxs`, and converts schedule-queue admission failure into a `txpool` error in the corresponding result before notifying the submitter.

# Root Cause

The txpool's checked-transaction state was missing sender metadata that later sender-aware queue logic could use, and the post-CheckTx scheduling stage did not retain enough index information to surface queue-admission failure back to the correct caller. That is a local admission-path consistency gap. The provided evidence does not by itself prove a security vulnerability beyond that.

## Walkthrough

1. `CheckTxMetadata` includes sender-related fields in the runtime host protocol types.

2. Before the change, `Transaction.setChecked` only copied `Priority`; after the change it also copies `Sender` and `SenderSeq` and assigns a hash-based fallback when sender metadata is empty.

3. The traced scheduling subsystem keeps sender-indexed state via `bySender`, which is consistent with sender-aware local queue handling.

4. `checkTxBatch` is refactored to use `notifySubmitter` and to track `batchIndices` alongside `newTxs`.

5. The scheduling loop changes to indexed iteration so a later `schedulerQueue.add` failure can be mapped back to the original result slot.

6. On scheduling failure, the patched code writes a `txpool` error into `results[batchIndices[i]]` and notifies the submitter instead of only logging the failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/runtime/txpool/transaction.go | 89 | Copies sender identity and sender sequence from CheckTx metadata into txpool transactions; falls back to unique sender IDs when metadata is absent. |
| go/runtime/host/protocol/types.go | 246 | Defines `CheckTxMetadata` fields, including sender information consumed by txpool admission logic. |
| go/runtime/txpool/schedule_queue.go | 34 | Maintains sender-indexed scheduling state (`bySender`) used to bound outstanding transactions per sender. |
| go/runtime/txpool/txpool.go | 491 | Processes batch CheckTx results and tracks original batch indices so later queue-admission failures can be converted into submitter-visible errors. |
| go/runtime/txpool/txpool.go | 548 | Queues checked transactions for scheduling and turns schedule-queue rejection into a txpool error instead of silently leaving the transaction accepted. |

## Code Snippets

## Snippet 1

Context: `go/runtime/txpool/txpool.go:548` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// Queue checked transactions for scheduling.
	for _, tx := range newTxs {
		// NOTE: Scheduler exists as otherwise there would be no current block info above.
		if err := t.schedulerQueue.add(tx.Transaction); err != nil {
			t.logger.Error("unable to schedule transaction",
				"err", err,
				"tx", tx,
```
After
```go
// Queue checked transactions for scheduling.
	for i, tx := range newTxs {
		// NOTE: Scheduler exists as otherwise there would be no current block info above.
		if err := t.schedulerQueue.add(tx.Transaction); err != nil {
			t.logger.Error("unable to queue transaction for scheduling",
				"err", err,
				"tx_hash", tx.hash,
```

## Snippet 2

Context: `go/runtime/txpool/txpool.go:490` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
pendingCheckSize.With(t.getMetricLabels()).Set(float64(t.PendingCheckSize()))

	newTxs := make([]*PendingCheckTransaction, 0, len(results))
	var unschedule []hash.Hash
	for i, res := range results {
		// Send back the result of running the checks.
		if batch[i].notifyCh != nil {
```
After
```go
pendingCheckSize.With(t.getMetricLabels()).Set(float64(t.PendingCheckSize()))

	notifySubmitter := func(i int) {
		// Send back the result of running the checks.
		if batch[i].notifyCh != nil {
```

## Snippet 3

Context: `go/runtime/txpool/txpool.go:497` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
batch[i].notifyCh = nil
		}

		if !res.IsSuccess() {
			t.logger.Debug("check tx failed",
```
After
```go
batch[i].notifyCh = nil
		}
	}

	newTxs := make([]*PendingCheckTransaction, 0, len(results))
	batchIndices := make([]int, 0, len(results))
	var unschedule []hash.Hash
	for i, res := range results {
```

## Snippet 4

Context: `go/runtime/txpool/transaction.go:92` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
if meta != nil {
		tx.priority = meta.Priority
	}
}
```
After
```go
if meta != nil {
		tx.priority = meta.Priority
		tx.sender = string(meta.Sender)
		tx.senderSeq = meta.SenderSeq
	}

	// If the sender is empty (e.g. because the runtime does not support specifying a sender), we
	// treat each transaction as having a unique sender. This is to allow backwards compatibility.
```

# Fix Pattern

Propagate admission metadata needed by later queue stages, preserve index mapping across batch processing, and turn downstream queue rejection into an explicit caller-visible error.

## How It Was Fixed

The patch stores sender identity and sender sequence on checked txpool transactions, adds a unique fallback sender when the runtime provides none, and preserves original batch indices while processing checked transactions. That lets the code associate a later scheduling rejection with the correct transaction result and return a `txpool` error to the submitter.

# Why It Matters

1. It removes a log-only failure path after CheckTx succeeds.

2. It makes sender metadata available to later txpool scheduling logic.

3. It improves local admission-path correctness and operator visibility.

4. The evidence does not show a consensus, cryptographic, or clearly exploitable flaw.

# Evidence Notes

Directly supported observations are limited to: sender fields began being copied from `CheckTxMetadata`; empty sender metadata now falls back to a per-transaction hash-derived sender; `checkTxBatch` now preserves `batchIndices`; and `schedulerQueue.add` failure is translated into a `txpool` error returned through the batch result. The existence of `bySender` supports sender-aware queue state, but the supplied excerpts do not show the actual rejection condition inside `scheduleQueue.add`, so a stronger claim about the exact prior vulnerability or enforcement semantics is not established. Protocol security invariant: Txpool admission should preserve any sender identity returned by CheckTx so sender-aware scheduling or admission rules can be applied consistently, and any downstream queue rejection should be returned to the submitter instead of being left as a log-only condition. The provided evidence does not establish a stronger invariant than local txpool resource control, and the hash-based fallback shows sender-based handling is not uniformly available across runtimes. Verification notes: The patch shows node-local txpool admission hardening, not a consensus-validation or cryptographic fix. The diff does not prove a remotely exploitable denial of service beyond sender-local resource consumption pressure. The fallback for empty sender metadata means the new sender-based bound is not shown to apply to all runtimes. The evidence does not show the exact previous limits, memory impact, or whether other global queue caps already reduced exposure. The diff supports txpool admission hardening and better error propagation. The supplied evidence does not show the exact `scheduleQueue.add` rejection logic. No direct proof of remote exploitability or measurable resource exhaustion is provided. The hash-based fallback means sender-based behavior is not clearly enforced for runtimes that omit sender metadata. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-resource-limits`
Final impact type: `denial-of-service, resource-exhaustion`
Final confidence: `medium`
Final tags: `blockchain-core, txpool, admission-control, resource-control, sender-limit, dos-mitigation`

The patch is best kept as a security-hardening case, not as a proven vulnerability fix. The commit subject and code changes show sender metadata is now propagated into txpool transactions so sender-aware scheduling limits can be applied, and schedule-queue rejection is now surfaced back to the submitter instead of remaining a log-only condition. That is a meaningful tightening of node-local resource-control behavior in a transaction admission path, but the supplied diff does not by itself prove a concrete exploitable bug, consensus failure, or broader state-representation issue.

## Security Evidence

1. Commit subject explicitly states 'Limit outstanding transactions per sender'.
2. `setChecked` now copies `meta.Sender` and `meta.SenderSeq`, enabling sender-aware txpool handling.
3. Empty sender metadata now falls back to a unique per-transaction sender, avoiding accidental coalescing while preserving compatibility.
4. `checkTxBatch` now preserves `batchIndices`, allowing scheduling failures to be tied back to the correct transaction result.
5. `schedulerQueue.add` failure is converted into a returned `txpool` error instead of only being logged.
6. Project context shows `scheduleQueue` tracks transactions by sender (`bySender`), consistent with per-sender resource controls.

## Missing Evidence

1. The actual `scheduleQueue.add` rejection logic is not shown in the supplied patch evidence.
2. No proof is provided that the prior behavior was remotely exploitable in practice.
3. No concrete resource-exhaustion measurements, attack scenario, or impact bounds are included.
4. The evidence does not show that all runtimes provide sender metadata, and the fallback weakens claims about uniform enforcement.

## Claim Boundaries

1. This supports txpool admission hardening and DoS-risk reduction at the node-local queueing layer.
2. This does not support the original `serialization-or-state-representation` classification.
3. This does not prove a consensus bug, client-view divergence, or cryptographic flaw.
4. This does not prove a concrete exploitable vulnerability beyond reduced exposure to sender-driven queue abuse.
