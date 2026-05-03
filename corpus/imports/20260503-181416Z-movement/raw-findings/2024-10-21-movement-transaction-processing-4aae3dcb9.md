---
case_id: case_20241021_4aae3dcb9
project: movement
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2024-10-21
source_refs:
  - git:4aae3dcb9cd31e9c507ec247a3cfcea93e838933
  - "protocol-units/execution/opt-executor/src/transaction_pipe.rs:217"
  - "protocol-units/execution/opt-executor/src/transaction_pipe.rs:397"
  - "protocol-units/execution/opt-executor/src/transaction_pipe.rs:136"
  - "protocol-units/execution/opt-executor/src/transaction_pipe.rs:472"
bug_class: transaction-sequence-number-admission
impact_type:
  - replay-resistance
  - transaction-admission-integrity
tags:
  - blockchain-core
  - transaction-processing
  - mempool-admission
  - sequence-number-validation
  - replay-resistance
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is sequence-number admission hardening in the execution transaction pipe. The patch replaces an inline committed-state check that only visibly rejected too-old sequence numbers with a centralized `has_invalid_sequence_number` check, and the tests now expect duplicate submissions not to be forwarded again. The evidence does not establish a consensus break, signature flaw, on-chain invalid commit, economic exploit, or guaranteed denial of service.

## Observed Patch Facts

1. In `protocol-units/execution/opt-executor/src/transaction_pipe.rs`, the patch replaces `// Retrieve the current sequence number for the account from the db` with `let sequence_number = match self.has_invalid_sequence_number(&transaction)? {`.

2. In `protocol-units/execution/opt-executor/src/transaction_pipe.rs`, the patch replaces `let received_transaction = tx_receiver.recv().await.unwrap();` with `// assert that there is no new transaction`.

3. In `protocol-units/execution/opt-executor/src/transaction_pipe.rs`, the patch replaces `async fn submit_transaction(` with `fn has_invalid_sequence_number(`.

4. In `protocol-units/execution/opt-executor/src/transaction_pipe.rs`, the patch replaces `async fn test_sequence_number_too_old() -> Result<(), anyhow::Error> {` with `async fn test_cannot_submit_too_new() -> Result<(), anyhow::Error> {`.

## Project Context

The changed code sits primarily in `protocol-units/execution/opt-executor/src`, `protocol-units/execution/opt-executor`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `protocol-units/execution/opt-executor/src/gc_account_sequence_number.rs`, `protocol-units/execution/opt-executor/src/service.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `protocol-units/execution/opt-executor/src/service.rs`, `protocol-units/execution/opt-executor/src/executor/execution.rs`. The strongest project-level identifiers around this patch are `transaction`, `tokio::test`, `anyhow::Error`, and `sequence_number`.

## Before/After Behavior

Before the patch, `submit_transaction` visibly read the sender sequence number from the latest state checkpoint and rejected only `transaction.sequence_number() < sequence_number` as `SEQUENCE_NUMBER_TOO_OLD`. A duplicate-submission test expected the same transaction to be received again. After the patch, `submit_transaction` calls `has_invalid_sequence_number` and only continues on `SequenceNumberValidity::Valid`; duplicate submission coverage now expects no new transaction, and additional test coverage targets too-new sequence numbers.

# Root Cause

The evidenced root cause was an incomplete transaction admission guard at the execution mempool ingress path. The old visible check handled stale committed-state sequence numbers but did not account for sequence numbers already tracked as used or in flight. Stronger claims about cryptography, signing format, consensus safety, or committed invalid transactions are not supported by the provided diff evidence.

## Walkthrough

1. A `MempoolClientRequest::SubmitTransaction` is routed by `TransactionPipe::tick` into `submit_transaction`.

2. `submit_transaction` performs existing load shedding and VM validation before sequence-number handling.

3. The removed inline code read the latest state checkpoint and rejected only sequence numbers lower than committed account state.

4. The patch routes this decision through `has_invalid_sequence_number`.

5. The helper is shown consulting `used_sequence_number_pool` and then validating against the latest state view.

6. Accepted transactions continue only when the helper returns `SequenceNumberValidity::Valid`.

7. The duplicate transaction test was changed from expecting a second forwarded transaction to expecting no new transaction.

8. The added too-new test indicates the patch also covers sequence numbers that skip ahead, though the full helper logic is not shown in the supplied evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 187 | mempool submission path validates signed transactions before forwarding them |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 136 | centralized sequence-number validity check against in-flight pool and state view |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 92 | request pump routes SubmitTransaction API requests into submission validation |
| protocol-units/execution/opt-executor/src/gc_account_sequence_number.rs | 1 | tracks per-account used sequence numbers with TTL-based garbage collection |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 364 | regression test for duplicate transaction not being forwarded twice |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 472 | regression test for rejecting too-new sequence numbers |

## Code Snippets

## Snippet 1

Context: `protocol-units/execution/opt-executor/src/transaction_pipe.rs:217` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

		// Retrieve the current sequence number for the account from the db
		let state_view = self
			.db_reader
			.latest_state_checkpoint_view()
			.expect("Failed to get latest state checkpoint view.");
		let sequence_number =
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

Context: `protocol-units/execution/opt-executor/src/transaction_pipe.rs:397` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
callback.await??;

		let received_transaction = tx_receiver.recv().await.unwrap();
		assert_eq!(received_transaction, user_transaction);

		Ok(())
```
After
```rust
callback.await??;

		// assert that there is no new transaction
		assert!(tx_receiver.try_recv().is_err());

		Ok(())
```

## Snippet 3

Context: `protocol-units/execution/opt-executor/src/transaction_pipe.rs:136` (changes how canonical state is encoded, returned, or reconstructed)

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

## Snippet 4

Context: `protocol-units/execution/opt-executor/src/transaction_pipe.rs:472` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

	#[tokio::test]
	async fn test_sequence_number_too_old() -> Result<(), anyhow::Error> {
		let (tx_sender, _tx_receiver) = mpsc::channel(16);
		let (executor, config, _tempdir) = Executor::try_test_default(GENESIS_KEYPAIR.0.clone())?;
		let (context, mut transaction_pipe) = executor.background(tx_sender)?;
```
After
```rust
}

	#[tokio::test]
	async fn test_cannot_submit_too_new() -> Result<(), anyhow::Error> {
		// set up
		let maptos_config = Config::default();
		let (mut transaction_pipe, mut _mempool_client_sender, _tx_receiver) = setup();
```

# Fix Pattern

Centralize sequence-number admission validation before forwarding transactions downstream, combining committed-state checks with local tracking of already used or in-flight sender sequence numbers.

## How It Was Fixed

The inline state-only sequence-number check in `submit_transaction` was replaced with a call to `has_invalid_sequence_number`. The new helper checks `used_sequence_number_pool` and the latest state view, returning either a valid sequence number or an invalid submission status. Regression tests were updated for duplicate submissions and too-new sequence numbers.

# Why It Matters

1. Sequence numbers are replay and ordering controls for account transactions.

2. Duplicate accepted submissions should not be forwarded as new work.

3. Too-new sequence numbers should not be admitted as valid fresh submissions.

4. The evidence supports hardening of transaction ingress, not a proven chain-level exploit.

# Evidence Notes

Grounded evidence comes from `protocol-units/execution/opt-executor/src/transaction_pipe.rs`: `submit_transaction` now calls `has_invalid_sequence_number`; the helper begins by checking `used_sequence_number_pool` and then state view; `tick` routes `SubmitTransaction` requests into this path; the duplicate test now asserts no new transaction is received; and a too-new sequence-number test was added. The supplied snippets do not show a concrete attacker flow, successful invalid commit, signature issue, consensus failure, economic loss, or guaranteed denial of service. Protocol security invariant: Transaction admission should not forward signed account transactions as fresh work when their sender sequence number is invalid relative to committed state or already accepted in-flight submissions. Verification notes: The patch does not prove that invalid transactions could be committed on-chain. The patch does not prove validator signature forgery or cryptographic failure. The patch does not prove a consensus safety violation. The patch does not show an economic exploit or guaranteed denial of service. The commit subject mentions signing, but the provided diff evidence supports sequence-number admission handling, not a signature-format bug. Kept the finding scoped to transaction admission hardening. Downgraded confidence from high to medium because the full helper body and exact rejection statuses are not fully shown. Rejected unsupported serialization, signing-format, cryptographic, and consensus claims. Kept security corpus inclusion because the patch directly affects replay/order-sensitive transaction admission behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-sequence-number-admission`
Final impact type: `replay-resistance, transaction-admission-integrity`
Final tags: `blockchain-core, transaction-processing, mempool-admission, sequence-number-validation, replay-resistance`

The supplied evidence supports keeping this as security hardening, but not as a concrete security fix. The patch tightens transaction admission around sequence numbers by replacing a state-only stale-sequence check with a centralized helper that also consults an in-flight or used sequence-number pool, and tests now assert duplicate submissions are not forwarded again. In a blockchain transaction path, sequence numbers are security-sensitive replay and ordering controls, but the evidence does not prove an exploitable consensus failure, signature flaw, invalid commit, economic loss, or denial of service.

## Security Evidence

1. Transaction submission now gates forwarding on has_invalid_sequence_number returning SequenceNumberValidity::Valid.
2. The new helper checks used_sequence_number_pool before validating against the latest state view.
3. Duplicate transaction test changed from expecting a second forwarded transaction to expecting no new transaction.
4. Added or changed coverage targets too-new sequence numbers in the transaction pipe.
5. The affected path handles MempoolClientRequest::SubmitTransaction before forwarding signed transactions downstream.

## Missing Evidence

1. No attacker scenario is shown.
2. No evidence that invalid transactions could be committed on-chain before the patch.
3. No evidence of signature forgery, signature misuse, or cryptographic failure despite the commit subject mentioning signing.
4. No demonstrated consensus safety violation or validator divergence.
5. No demonstrated economic exploit or guaranteed denial of service.

## Claim Boundaries

1. Validate only as transaction sequence-number admission hardening.
2. Do not classify as a serialization or state-representation bug.
3. Do not claim a signature-format or cryptographic vulnerability from the supplied evidence.
4. Do not claim consensus break, committed invalid state, or client-view divergence.
5. Security relevance comes from replay/order-sensitive transaction ingress behavior, not from a proven exploit.
