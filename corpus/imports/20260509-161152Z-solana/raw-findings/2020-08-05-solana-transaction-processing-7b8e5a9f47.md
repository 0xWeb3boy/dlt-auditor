---
case_id: case_20200805_7b8e5a9f47
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2020-08-05
source_refs:
  - git:7b8e5a9f47f9b4e2ed0024a2fee360b9ae0e24cc
  - "core/src/rpc.rs:3520"
  - "runtime/src/bank.rs:1137"
  - "sdk/src/transaction.rs:82"
  - "runtime/src/accounts.rs:630"
bug_class: missing-transaction-sanitization
impact_type:
  - input-validation
  - defense-in-depth
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - rpc
  - preflight
  - input-validation
  - transaction-sanitization
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds transaction sanitization to Solana RPC preflight simulation batch preparation. The evidence supports a missing validation fix for malformed transaction structure, specifically an invalid program_id_index in a preflight test. It does not establish an exploitable security vulnerability or concrete impact beyond clean rejection of malformed input.

## Observed Patch Facts

1. In `core/src/rpc.rs`, the patch replaces `let mut bad_transaction =` with `// sendTransaction will fail due to insanity`.

2. In `runtime/src/bank.rs`, the patch replaces `let mut batch = TransactionBatch::new(vec![Ok(()); txs.len()], &self, txs, None);` with `let lock_results: Vec<_> = txs`.

3. In `sdk/src/transaction.rs`, the patch replaces `/// An atomic transaction` with `impl From<SanitizeError> for TransactionError {`.

4. In `runtime/src/accounts.rs`, the patch replaces `tx.sanitize()` with `tx.sanitize().map_err(TransactionError::from)?;`.

## Project Context

The changed code sits primarily in `core/src`, `runtime/src`, `sdk/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/transaction_batch.rs`, `core/src/banking_stage.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/banking_stage.rs`, `sdk/src/transport.rs`. The strongest project-level identifiers around this patch are `TransactionBatch::new`, `TransactionError::SanitizeFailure`, `TransactionError`, and `batch`.

## Before/After Behavior

Before the patch, Bank::prepare_simulation_batch constructed a TransactionBatch with vec![Ok(()); txs.len()], so this simulation path did not record per-transaction sanitize failures before batch construction. After the patch, it maps each transaction through tx.sanitize() and stores any failure as TransactionError::SanitizeFailure. The RPC test now submits a transaction with program_id_index set to 255 and expects a JSON-RPC simulation failure reporting TransactionError::SanitizeFailure.

# Root Cause

The RPC preflight simulation batch path skipped explicit structural transaction sanitization before constructing its TransactionBatch, unlike paths that already called tx.sanitize().

## Walkthrough

1. A transaction is submitted through RPC sendTransaction with preflight simulation enabled, as represented by the rpc.rs regression test.

2. The test mutates the transaction message so instructions[0].program_id_index is 255, making the transaction structurally invalid.

3. Before the patch, prepare_simulation_batch initialized all batch results as Ok(()) instead of deriving them from tx.sanitize().

4. That meant malformed structure was not rejected at this batch-preparation point.

5. After the patch, prepare_simulation_batch sanitizes each transaction and converts sanitize failures into TransactionError::SanitizeFailure.

6. The regression test asserts that the malformed RPC preflight transaction now fails cleanly with TransactionError::SanitizeFailure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 1135 | Adds transaction sanitization to RPC simulation batch preparation before TransactionBatch::new. |
| core/src/rpc.rs | 3470 | Regression test sends malformed transaction through sendTransaction preflight and expects SanitizeFailure. |
| sdk/src/transaction.rs | 82 | Adds conversion from SanitizeError to TransactionError::SanitizeFailure for uniform error propagation. |
| runtime/src/accounts.rs | 630 | Uses the new SanitizeError to TransactionError conversion in account locking path; appears behaviorally equivalent cleanup for this path. |

## Code Snippets

## Snippet 1

Context: `core/src/rpc.rs:3520` (changes persisted or aggregate state handling)

Before
```rust
);

        let recent_blockhash = bank_forks.read().unwrap().root_bank().last_blockhash();
        let mut bad_transaction =
            system_transaction::transfer(&Keypair::new(), &Pubkey::default(), 42, recent_blockhash);

        // sendTransaction will fail due to poor node health
```
After
```rust
);

        // sendTransaction will fail due to insanity
        bad_transaction.message.instructions[0].program_id_index = 255u8;
        let recent_blockhash = bank_forks.read().unwrap().root_bank().last_blockhash();
        bad_transaction.sign(&[&mint_keypair], recent_blockhash);
        let req = format!(
            r#"{{"jsonrpc":"2.0","id":1,"method":"sendTransaction","params":["{}"]}}"#,
```

## Snippet 2

Context: `runtime/src/bank.rs:1137` (changes a sensitive control or state-update path)

Before
```rust
txs: &'b [Transaction],
    ) -> TransactionBatch<'a, 'b> {
        let mut batch = TransactionBatch::new(vec![Ok(()); txs.len()], &self, txs, None);
        batch.needs_unlock = false;
        batch
```
After
```rust
txs: &'b [Transaction],
    ) -> TransactionBatch<'a, 'b> {
        let lock_results: Vec<_> = txs
            .iter()
            .map(|tx| tx.sanitize().map_err(|e| e.into()))
            .collect();
        let mut batch = TransactionBatch::new(lock_results, &self, txs, None);
        batch.needs_unlock = false;
```

## Snippet 3

Context: `sdk/src/transaction.rs:82` (changes a sensitive control or state-update path)

Before
```rust
}

/// An atomic transaction
#[derive(Debug, PartialEq, Default, Eq, Clone, Serialize, Deserialize)]
```
After
```rust
}

impl From<SanitizeError> for TransactionError {
    fn from(_: SanitizeError) -> Self {
        Self::SanitizeFailure
    }
}
```

## Snippet 4

Context: `runtime/src/accounts.rs:630` (changes a sensitive control or state-update path)

Before
```rust
let keys: Vec<Result<_>> = OrderedIterator::new(txs, txs_iteration_order)
            .map(|tx| {
                tx.sanitize()
                    .map_err(|_| TransactionError::SanitizeFailure)?;

                if Self::has_duplicates(&tx.message.account_keys) {
```
After
```rust
let keys: Vec<Result<_>> = OrderedIterator::new(txs, txs_iteration_order)
            .map(|tx| {
                tx.sanitize().map_err(TransactionError::from)?;

                if Self::has_duplicates(&tx.message.account_keys) {
```

# Fix Pattern

Run structural validation at the RPC preflight simulation batch boundary and propagate validation failures through the existing transaction error type.

## How It Was Fixed

runtime/src/bank.rs now builds lock_results by calling tx.sanitize() for each transaction before TransactionBatch::new. sdk/src/transaction.rs adds From<SanitizeError> for TransactionError, mapping sanitize errors to TransactionError::SanitizeFailure. runtime/src/accounts.rs switches to the same conversion helper in an already-sanitizing path. core/src/rpc.rs adds a regression test for malformed preflight input.

# Why It Matters

1. Malformed RPC preflight transactions now get a stable sanitize failure.

2. The simulation path is brought closer to normal transaction validation behavior.

3. The evidence does not prove crashability, consensus impact, signature bypass, or unauthorized state changes.

# Evidence Notes

Grounded evidence is limited to the shown diff: prepare_simulation_batch changed from unconditional Ok results to tx.sanitize() results, the RPC test uses an invalid program_id_index and expects SanitizeFailure, and a helper conversion from SanitizeError to TransactionError was added. Claims about denial of service, panic, consensus failure, cryptographic weakness, or fund loss are not supported by the provided evidence. Protocol security invariant: Transactions used for RPC preflight simulation should be structurally sanitized before downstream simulation batch handling, so malformed message indexes are reported as TransactionError::SanitizeFailure. Verification notes: The patch does not prove remote node crashability. The patch does not show consensus safety failure or ledger corruption. The patch does not show signature verification bypass or cryptographic weakness. The patch does not prove funds can be stolen or unauthorized state can be changed. The accounts.rs hunk appears to be error-mapping cleanup rather than a new guard. Implementation evidence supports a missing validation fix in RPC preflight simulation. Security impact is not established by the supplied hunks. accounts.rs appears to be cleanup using the new conversion helper, not a new guard. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-transaction-sanitization`
Final impact type: `input-validation, defense-in-depth`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, rpc, preflight, input-validation, transaction-sanitization, security-hardening`

The patch clearly adds structural transaction sanitization to the RPC preflight simulation path, replacing unconditional success batch results with per-transaction sanitize results and adding a regression test for a malformed program_id_index submitted through sendTransaction. The evidence does not prove a concrete exploit, crash, consensus failure, or unauthorized state change, so this should not be treated as a confirmed security fix. It is appropriate to retain as security hardening because it tightens validation of externally supplied transaction input at a security-sensitive blockchain RPC boundary.

## Security Evidence

1. RPC preflight sendTransaction test constructs a malformed transaction with program_id_index = 255 and expects TransactionError::SanitizeFailure.
2. Bank::prepare_simulation_batch changed from vec![Ok(()); txs.len()] to calling tx.sanitize() for each transaction.
3. SanitizeError is mapped into TransactionError::SanitizeFailure for propagation through transaction processing.
4. The changed path handles transaction simulation/preflight, an exposed boundary for untrusted transaction data.

## Missing Evidence

1. No evidence that the prior behavior caused node crashability or denial of service.
2. No evidence of consensus failure, ledger corruption, signature bypass, or unauthorized state changes.
3. No before-patch failure mode is shown beyond missing clean sanitize rejection in preflight.
4. accounts.rs appears to be equivalent error-mapping cleanup rather than a new security guard.

## Claim Boundaries

1. Classify as security hardening, not a proven exploitable security fix.
2. Limit the bug class to missing transaction sanitization/input validation in RPC preflight simulation.
3. Do not claim liveness impact from the supplied patch alone.
4. Do not infer cryptographic, replay, fund-loss, or consensus impact from this evidence.
