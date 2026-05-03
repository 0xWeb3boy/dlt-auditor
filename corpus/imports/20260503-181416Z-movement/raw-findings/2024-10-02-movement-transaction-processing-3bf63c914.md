---
case_id: case_20241002_3bf63c914
project: movement
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2024-10-02
source_refs:
  - git:3bf63c9149676bd5484e14935dcecbd806ae77ff
  - "protocol-units/execution/opt-executor/src/transaction_pipe.rs:212"
  - "protocol-units/execution/opt-executor/src/transaction_pipe.rs:137"
  - "protocol-units/execution/opt-executor/src/gc_account_sequence_number.rs:1"
  - "protocol-units/execution/opt-executor/src/transaction_pipe.rs:126"
bug_class: transaction-sequence-number-reuse
impact_type:
  - replay-protection
  - transaction-ordering
  - state-consistency
tags:
  - blockchain-core
  - transaction-processing
  - mempool
  - sequence-number
  - replay-protection
  - state-consistency
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix for stale-state sequence-number validation in the execution mempool. The grounded change is that `TransactionPipe` no longer validates only against the latest state checkpoint; it now routes sequence-number validation through `has_invalid_sequence_number`, which consults a newly added used-sequence-number pool and then validates against state. The exact exploit path and impact are not proven by the snippets, so the finding should not be stated as confirmed.

## Observed Patch Facts

1. In `protocol-units/execution/opt-executor/src/transaction_pipe.rs`, the patch replaces `// Validate sequence number` with `let sequence_number = match self.has_invalid_sequence_number(&transaction)? {`.

2. In `protocol-units/execution/opt-executor/src/transaction_pipe.rs`, the patch replaces `async fn submit_transaction(` with `fn has_invalid_sequence_number(`.

3. In `protocol-units/execution/opt-executor/src/gc_account_sequence_number.rs`, the patch adds `pub struct UsedSequenceNumberPool {`.

4. In `protocol-units/execution/opt-executor/src/transaction_pipe.rs`, the patch replaces `self.last_gc = Instant::now();` with `// todo: these will be slightly off, but gc does not need to be exact`.

## Project Context

The changed code sits primarily in `protocol-units/execution/opt-executor/src`, `protocol-units/execution/opt-executor`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `protocol-units/execution/opt-executor/src/service.rs`, `protocol-units/execution/opt-executor/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `protocol-units/execution/opt-executor/src/service.rs`, `protocol-units/execution/opt-executor/src/lib.rs`. The strongest project-level identifiers around this patch are `Instant::now`, `sequence`, `number`, and `sequence_number`.

## Before/After Behavior

Before the patch, the visible submission path read `latest_state_checkpoint_view()` and fetched the sender account sequence number from that state view, then rejected at least transactions whose sequence number was too old relative to committed state. The evidence does not show a local pending or in-flight reservation check in the old path. After the patch, `submit_transaction` calls `has_invalid_sequence_number`; invalid results return a mempool status immediately, and valid results continue with the returned sequence number. The patch also introduces `UsedSequenceNumberPool` and wires its garbage collection into the transaction pipe tick loop.

# Root Cause

The apparent root cause was sequence-number validation that depended on committed checkpoint state without sufficient evidence of accounting for sequence numbers already tracked locally by the mempool or execution pipeline. That could allow stale-state decisions around reused sequence numbers before committed state advances, but the provided snippets do not prove the full attacker flow.

## Walkthrough

1. A transaction enters `TransactionPipe::submit_transaction` through the mempool client request flow.

2. The old visible validation path queried the latest state checkpoint for the sender account sequence number.

3. That old evidence shows rejection of sequence numbers older than committed state, but does not show checking a local used-sequence-number reservation pool.

4. The patch adds `has_invalid_sequence_number`, which first consults `used_sequence_number_pool` for the transaction sender.

5. `submit_transaction` now returns immediately when the helper reports an invalid sequence number.

6. A new `UsedSequenceNumberPool` stores per-account sequence-number information with TTL-oriented lifetime bins.

7. The transaction pipe tick loop now garbage-collects the used-sequence-number pool alongside core mempool GC.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 137 | Adds has_invalid_sequence_number helper that checks the used sequence number pool before validating against state. |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 182 | Transaction submission path now rejects invalid or previously used sequence numbers before accepting into mempool flow. |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 126 | Runs garbage collection for used sequence number reservations alongside core mempool GC. |
| protocol-units/execution/opt-executor/src/gc_account_sequence_number.rs | 1 | Introduces per-account used sequence number tracking with TTL-based garbage collection. |

## Code Snippets

## Snippet 1

Context: `protocol-units/execution/opt-executor/src/transaction_pipe.rs:212` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

		// Validate sequence number
		let state_view = self
			.db_reader
			.latest_state_checkpoint_view()
			.expect("Failed to get latest state view");
```
After
```rust
}

		let sequence_number = match self.has_invalid_sequence_number(&transaction)? {
			SequenceNumberValidity::Valid(sequence_number) => sequence_number,
			SequenceNumberValidity::Invalid(status) => {
				return Ok(status);
			}
		};
```

## Snippet 2

Context: `protocol-units/execution/opt-executor/src/transaction_pipe.rs:137` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

	async fn submit_transaction(
		&mut self,
```
After
```rust
}

	fn has_invalid_sequence_number(
		&self,
		transaction: &SignedTransaction,
	) -> Result<SequenceNumberValidity, Error> {
		// check against the used sequence number pool
		let used_sequence_number = self
```

## Snippet 3

Context: `protocol-units/execution/opt-executor/src/gc_account_sequence_number.rs:1` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
(no before snippet captured)
```
After
```rust
use aptos_types::account_address::AccountAddress;
use std::collections::{BTreeMap, HashMap};

pub struct UsedSequenceNumberPool {
	/// The number of milliseconds a sequence number is valid for.
	sequence_number_ttl_ms: u64,
	/// The duration of a garbage collection slot in milliseconds.
	/// This is used to bin sequence numbers into slots for O(sequence_number_ttl_ms/gc_slot_duration_ms * log sequence_number_ttl_ms/gc_slot_duration_ms) garbage collection.
```

## Snippet 4

Context: `protocol-units/execution/opt-executor/src/transaction_pipe.rs:126` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
if self.last_gc.elapsed() >= GC_INTERVAL {
			self.core_mempool.gc();
			self.last_gc = Instant::now();
		}
```
After
```rust
if self.last_gc.elapsed() >= GC_INTERVAL {
			// todo: these will be slightly off, but gc does not need to be exact
			let now = Instant::now();
			let epoch_ms_now = chrono::Utc::now().timestamp_millis() as u64;
			self.used_sequence_number_pool.gc(epoch_ms_now);
			self.core_mempool.gc();
			self.last_gc = now;
```

# Fix Pattern

Validate replay- or ordering-sensitive transaction identifiers against both durable committed state and local pending or reserved state, with bounded lifetime management for local reservations.

## How It Was Fixed

The fix adds a used-sequence-number tracking module, calls the new validation helper from `submit_transaction`, and garbage-collects the tracking pool during the transaction pipe's regular GC path.

# Why It Matters

1. Reduces risk of accepting a sender sequence number based on stale committed state alone.

2. Strengthens replay and ordering checks for account-sequence-number transaction submission.

3. The evidence supports a likely security fix, but not claims of theft, signature bypass, or consensus failure.

# Evidence Notes

Grounded evidence comes from `transaction_pipe.rs` changes around sequence-number validation and GC, plus the new `gc_account_sequence_number.rs` support module. The commit subject says `fix: used sequence number prevents exploit.`, which supports security relevance. Unsupported or overstrong claims removed: direct economic impact, consensus safety failure, signature verification bypass, and confirmed exploit mechanics. The snippets also do not show every method of `UsedSequenceNumberPool` or exactly where sequence numbers are inserted into the pool. Protocol security invariant: For each sender account, transaction sequence numbers should not be accepted based only on committed checkpoint state when the same sequence number may already be reserved or used in local pending transaction state. Verification notes: The patch does not prove theft of funds or direct economic loss. The patch does not show a signature verification bypass. The patch does not prove consensus safety failure across validators. The exact exploit mechanics and attacker prerequisites are not shown. The TTL garbage collection policy is shown, but its full correctness is not proven by the snippet. No direct test evidence was provided. Exact attacker prerequisites are not established by the supplied snippets. Full correctness of the TTL garbage-collection policy is not proven by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `transaction-sequence-number-reuse`
Final impact type: `replay-protection, transaction-ordering, state-consistency`
Final tags: `blockchain-core, transaction-processing, mempool, sequence-number, replay-protection, state-consistency`

The supplied evidence supports keeping this as a security-relevant fix. The commit subject explicitly references preventing an exploit, and the patch changes transaction submission validation from relying on checkpoint state alone to consulting a local used-sequence-number pool before accepting a transaction. Because account sequence numbers are replay- and ordering-sensitive in this context, this is more than routine reliability work. However, the snippets do not prove the full exploit mechanics or concrete impact, so the verdict should remain likely rather than confirmed, and the original serialization/client-divergence framing should be narrowed.

## Security Evidence

1. Commit subject says "fix: used sequence number prevents exploit."
2. Transaction submission now calls has_invalid_sequence_number and rejects invalid sequence numbers before continuing.
3. New validation checks a used_sequence_number_pool for the transaction sender before validating against state.
4. A new UsedSequenceNumberPool tracks per-account sequence numbers with TTL-based garbage collection.
5. The changed path is transaction submission in the execution/mempool pipeline, where sequence numbers are replay- and ordering-sensitive.

## Missing Evidence

1. No full before/after implementation of UsedSequenceNumberPool insertion behavior is shown.
2. No test, advisory, issue, or exploit reproduction is provided.
3. The snippets do not prove theft, consensus failure, signature bypass, or client-view divergence.
4. The exact attacker prerequisites and exploitable transaction flow are not established.

## Claim Boundaries

1. Treat as a likely sequence-number reuse or replay-prevention security fix.
2. Do not claim confirmed exploitation from the patch alone.
3. Do not classify as serialization or canonical state representation based on the supplied evidence.
4. Do not claim settlement, validator consensus, or economic-loss impact without additional evidence.
