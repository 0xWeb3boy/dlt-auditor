---
case_id: case_20210524_25f10e879
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2021-05-24
source_refs:
  - git:25f10e8790c89e0728cb399e675339caf37dc470
  - "go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go:208"
  - "go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go:53"
  - "go/runtime/scheduling/simple/simple.go:43"
  - "go/runtime/scheduling/simple/txpool/tester.go:89"
bug_class: improper-resource-limit-enforcement
impact_type:
  - resource-exhaustion
  - availability
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - txpool
  - resource-limits
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is grounded as a transaction-scheduler/resource-accounting change: txpool admission moves from raw-byte size checks to checks over CheckedTransaction weight metadata, and surrounding scheduler/test code is updated to use checked transactions and hash-based removal. The provided evidence does not establish that the prior behavior was an exploitable security vulnerability.

## Observed Patch Facts

1. In `go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go`, the patch replaces `func (q *orderedMap) checkTxLocked(tx []byte, txHash hash.Hash) error {` with `func (q *orderedMap) checkTxLocked(tx *transaction.CheckedTransaction) error {`.

2. In `go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go`, the patch replaces `if err := q.checkTxLocked(tx, txHash); err != nil {` with `if err := q.checkTxLocked(tx); err != nil {`.

3. In `go/runtime/scheduling/simple/simple.go`, the patch replaces `// AppendTxBatch appends a batch of transactions.` with `func (s *scheduler) RemoveTxBatch(tx []hash.Hash) error {`.

4. In `go/runtime/scheduling/simple/txpool/tester.go`, the patch replaces `err = pool.RemoveBatch(batch)` with `hashes := make([]hash.Hash, len(batch))`.

## Project Context

The changed code sits primarily in `go/runtime/scheduling/simple/txpool/orderedmap`, `go/runtime/scheduling/simple/txpool`, `go/runtime/scheduling/simple`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `go/runtime/scheduling/simple/simple_test.go`, `go/runtime/scheduling/simple/txpool/orderedmap/ordered_map_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/runtime/scheduling/simple/txpool/api/api.go`, `go/runtime/scheduling/simple/simple_test.go`. The strongest project-level identifiers around this patch are `batch`, `Hash`, `error`, and `pool`. Nearby tests or test-like files include `go/runtime/scheduling/tests/tester.go`.

## Before/After Behavior

Before the patch, the shown txpool check helper accepted raw transaction bytes and a hash, and the visible enforcement was a raw-size limit using len(tx) against maxBatchSizeBytes. After the patch, the helper accepts a CheckedTransaction and iterates configured weightLimits via tx.Weight(w), rejecting transactions that exceed those limits; the add path validates the checked transaction directly, and related scheduler/test plumbing is updated to operate on checked transactions and transaction hashes.

# Root Cause

Txpool admission logic was still tied to an older raw-byte interface and only the visible size-based check, so configured CheckedTransaction metadata such as per-weight limits was not enforced in that admission path.

## Walkthrough

1. In go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go, checkTxLocked changes from taking raw []byte plus a hash to taking *transaction.CheckedTransaction.

2. The pre-change excerpt shows only a raw-size gate based on len(tx) and maxBatchSizeBytes.

3. The post-change excerpt adds a loop over q.weightLimits, reads tx.Weight(w), and rejects transactions that exceed configured limits.

4. The add path in the same file now calls the metadata-aware checkTxLocked(tx) before insertion.

5. In go/runtime/scheduling/simple/simple.go, the scheduler-facing API shown is aligned around checked transactions and hash-based batch removal.

6. In go/runtime/scheduling/simple/txpool/tester.go, tests are updated to configure WeightLimits, add checked transactions, and remove scheduled entries by hashes derived from returned checked transactions.

7. These excerpts support a resource-accounting and interface-alignment fix, but they do not prove a crash, bypass, consensus failure, or concrete denial-of-service vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go | 46 | txpool admission path for checked transactions before enqueue |
| go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go | 204 | enforcement of configured transaction weight limits during pool checks |
| go/runtime/scheduling/simple/simple.go | 29 | scheduler entrypoint forwarding checked transactions to the txpool and removing scheduled hashes |
| go/runtime/scheduling/simple/txpool/tester.go | 50 | regression coverage for weight-limited admission and hash-based batch removal |

## Code Snippets

## Snippet 1

Context: `go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go:208` (changes signature or replay validation logic)

Before
```go
// NOTE: Assumes lock is held.
func (q *orderedMap) checkTxLocked(tx []byte, txHash hash.Hash) error {
	txSize := uint64(len(tx))

	if txSize > q.maxBatchSizeBytes {
		return api.ErrCallTooLarge
	}
```
After
```go
// NOTE: Assumes lock is held.
func (q *orderedMap) checkTxLocked(tx *transaction.CheckedTransaction) error {
	// Check weights.
	for w, l := range q.weightLimits {
		txW := tx.Weight(w)
		if txW > l {
			// Transaction weight greater than the limit.
```

## Snippet 2

Context: `go/runtime/scheduling/simple/txpool/orderedmap/ordered_map.go:53` (changes signature or replay validation logic)

Before
```go
}

	if err := q.checkTxLocked(tx, txHash); err != nil {
		return err
	}

	q.addTxLocked(tx, txHash)
```
After
```go
}

	if err := q.checkTxLocked(tx); err != nil {
		return err
	}

	p := &pair{
		Key:   tx.Hash(),
```

## Snippet 3

Context: `go/runtime/scheduling/simple/simple.go:43` (changes signature or replay validation logic)

Before
```go
}

// AppendTxBatch appends a batch of transactions.
//
// Transactions that fail checks are skipped, not affecting the insertion of
// other transactions. If any transaction fails a check a non-nil error is
// returned.
// Aditionally this method does not try to schedule the transactions after the
```
After
```go
}

func (s *scheduler) RemoveTxBatch(tx []hash.Hash) error {
	return s.txPool.RemoveBatch(tx)
}

func (s *scheduler) GetBatch(force bool) []*transaction.CheckedTransaction {
	return s.txPool.GetBatch(force)
```

## Snippet 4

Context: `go/runtime/scheduling/simple/txpool/tester.go:89` (changes signature or replay validation logic)

Before
```go
require.EqualValues(t, 51, pool.Size(), "Size")

	err = pool.RemoveBatch(batch)
	require.NoError(t, err, "RemoveBatch")
	require.EqualValues(t, 41, pool.Size(), "Size")

	if pool.IsQueue() {
		require.EqualValues(t, batch[0], []byte("hello world"))
```
After
```go
require.EqualValues(t, 51, pool.Size(), "Size")

	hashes := make([]hash.Hash, len(batch))
	for i, tx := range batch {
		hashes[i] = tx.Hash()
	}
	err = pool.RemoveBatch(hashes)
	require.NoError(t, err, "RemoveBatch")
```

# Fix Pattern

Apply resource-limit enforcement at txpool admission using checked transaction metadata, and align surrounding scheduler interfaces with the same checked-transaction and hash-based model.

## How It Was Fixed

The patch changes txpool admission checks to consume CheckedTransaction objects, enforces configured weight limits through tx.Weight(w), updates the add path to validate the checked transaction directly, and adjusts scheduler/test code to batch checked transactions and remove them by hash.

# Why It Matters

1. It makes txpool admission honor configured weight metadata instead of relying only on raw byte length.

2. It reduces mismatch between checked transaction metadata and scheduler batching behavior.

3. The evidence supports stronger resource-limit enforcement, but not a confirmed security exploit or incident.

# Evidence Notes

The strongest direct evidence is the ordered_map.go change from a raw-size check to per-weight checks on CheckedTransaction. The commit subject mentions priority metadata, but the provided hunks mainly substantiate weight enforcement and API/plumbing updates. No supplied excerpt shows panic behavior, memory corruption, signature-validation failure, consensus divergence, or a demonstrated exploit path. Protocol security invariant: Txpool admission and batching should enforce configured transaction resource limits using the runtime's checked transaction metadata, not just raw byte length. Verification notes: The patch does not prove remote exploitability. The provided hunks do not show a panic, memory-safety issue, or signature-validation flaw. Consensus divergence is not established by the evidence. It is not proven that prior behavior let an attacker exceed global runtime limits, as opposed to causing suboptimal or failed scheduling. Priority-handling changes are implied by the commit subject and touched files, but the supplied diff excerpts mainly prove weight enforcement changes. Tests shown in go/runtime/scheduling/simple/txpool/tester.go were updated to configure WeightLimits and expect rejection of an oversized checked transaction. The provided evidence is sufficient to validate a scheduler resource-accounting change. The provided evidence is not sufficient to validate a confirmed security vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-resource-limit-enforcement`
Final impact type: `resource-exhaustion, availability`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, txpool, resource-limits, security-hardening`

The patch clearly strengthens a security-sensitive admission path by changing txpool checks from raw byte-length gating to enforcement of configured CheckedTransaction weight limits before queue insertion. In a blockchain transaction pool, that is exposed resource-control logic and the new checks reduce the risk of oversized or overweight transactions consuming scheduler or batching capacity. The supplied evidence does not prove a concrete exploitable vulnerability, consensus break, or demonstrated denial-of-service bug in the old behavior, so this is best retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `checkTxLocked` now validates `CheckedTransaction` metadata instead of only raw transaction bytes.
2. The new code iterates `q.weightLimits` and rejects transactions whose `tx.Weight(w)` exceeds configured limits.
3. The admission path calls the new metadata-aware `checkTxLocked(tx)` before adding the transaction to the pool.
4. Tests configure `WeightLimits` and expect rejection of an oversized checked transaction, showing intentional enforcement of resource bounds in txpool admission.
5. The changed subsystem is the scheduler/txpool path, which is an externally influenced resource-management boundary in a blockchain node.

## Missing Evidence

1. No proof that the prior code allowed a remotely exploitable denial-of-service in practice.
2. No evidence of a concrete security incident, crash, consensus divergence, or bypass caused by the old behavior.
3. No patch text or commit message explicitly describes a vulnerability, attacker model, or exploit scenario.
4. The excerpts do not show whether unchecked weight metadata was reachable from untrusted transactions across all relevant paths.

## Claim Boundaries

1. Supported claim: the patch hardens txpool resource accounting by enforcing configured transaction weight metadata during admission.
2. Supported claim: this reduces risk from overweight transactions consuming batching or queue resources.
3. Do not claim a confirmed exploitable DoS, consensus failure, replay flaw, or signature-validation bug from the provided evidence alone.
4. Do not claim the commit fixes priority handling as a security issue; the supplied hunks mainly substantiate weight-limit enforcement.
