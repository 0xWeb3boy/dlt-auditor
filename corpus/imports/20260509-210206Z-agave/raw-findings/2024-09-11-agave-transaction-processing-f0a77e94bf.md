---
case_id: case_20240911_f0a77e94bf
project: agave
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2024-09-11
source_refs:
  - git:f0a77e94bf0f4fbe2f423689c153cf38294d2992
  - "svm/src/transaction_processing_result.rs:48"
  - "runtime/src/bank/check_transactions.rs:134"
  - "runtime/src/bank/check_transactions.rs:117"
  - "svm/src/rollback_accounts.rs:52"
bug_class: durable-nonce-consumption
impact_type:
  - replay-risk
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - durable-nonce
  - replay-prevention
  - state-rollback
  - fee-only-transaction
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely security-relevant durable nonce consumption fix. The patch moves nonce advancement into the transaction age fallback path and adjusts rollback account construction so an already-advanced nonce is preserved when the nonce account is also the fee payer. The evidence does not establish practical exploitability, signature bypass, fund theft, or consensus divergence.

## Observed Patch Facts

1. In `svm/src/transaction_processing_result.rs`, the patch replaces `fn processed_transaction_mut(&mut self) -> Option<&mut ProcessedTransaction> {` with `fn flattened_result(&self) -> TransactionResult<()> {`.

2. In `runtime/src/bank/check_transactions.rs`, the patch replaces `pub(super) fn check_and_load_message_nonce_account(` with `pub(super) fn check_load_and_advance_message_nonce_account(`.

3. In `runtime/src/bank/check_transactions.rs`, the patch replaces `} else if let Some((nonce, nonce_data)) =` with `} else if let Some((nonce, previous_lamports_per_signature)) = self`.

4. In `svm/src/rollback_accounts.rs`, the patch replaces `RollbackAccounts::SameNonceAndFeePayer {` with `// 'nonce' contains an AccountSharedData which has already been advanced to the curre...`.

## Project Context

The changed code sits primarily in `svm/src`, `runtime/src/bank`, `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `svm/src/nonce_info.rs`, `runtime/src/bank/tests.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank/tests.rs`, `svm/src/transaction_processor.rs`. The strongest project-level identifiers around this patch are `nonce`, `Some`, `message`, and `next_durable_nonce`.

## Before/After Behavior

Before the patch, the transaction age fallback path loaded nonce account information with `check_and_load_message_nonce_account` and rollback construction for the same nonce-and-fee-payer case could use the fee payer account while carrying untouched nonce data. After the patch, `check_transaction_age` calls `check_load_and_advance_message_nonce_account`, receives the previous lamports-per-signature while advancing nonce state, and rollback construction copies `nonce.account().data()` into the fee payer account when the nonce account is also the fee payer.

# Root Cause

Rollback state for fee-only or failed durable nonce transactions could combine fee-payer lamport or rent changes with nonce account data that had not been advanced, leaving the old durable nonce available contrary to nonce consumption semantics.

## Walkthrough

1. A transaction with an invalid recent blockhash can still be accepted through the durable nonce path.

2. The previous fallback helper loaded the nonce account but the provided evidence does not show nonce advancement at that point.

3. The new helper is named `check_load_and_advance_message_nonce_account` and accepts both `next_durable_nonce` and `next_lamports_per_signature`.

4. `check_transaction_age` now uses that helper and retains the previous lamports-per-signature for fee calculation.

5. Rollback construction receives nonce information whose account data is described in comments as already advanced.

6. When the nonce account is also the fee payer, the patch copies the advanced nonce account data into the fee payer account before constructing rollback state.

7. The `transaction_processing_result.rs` change appears supportive of the revised state flow, but is not independently shown to be the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank/check_transactions.rs | 104 | Checks transaction age and now falls back to loading and advancing a durable nonce when the recent blockhash is not valid. |
| runtime/src/bank/check_transactions.rs | 134 | Replaces nonce load-only behavior with check_load_and_advance_message_nonce_account, returning the previous lamports_per_signature while advancing to the next durable nonce. |
| svm/src/rollback_accounts.rs | 36 | Builds rollback state for failed or fee-only transactions and now preserves advanced nonce data when the nonce account is also the fee payer. |
| svm/src/transaction_processing_result.rs | 48 | Removes mutation-oriented access to processed transactions and uses flattened result handling, supporting the revised transaction state flow. |

## Code Snippets

## Snippet 1

Context: `svm/src/transaction_processing_result.rs:48` (changes a sensitive control or state-update path)

Before
```rust
}

    fn processed_transaction_mut(&mut self) -> Option<&mut ProcessedTransaction> {
        match self {
            Ok(processed_tx) => Some(processed_tx),
            Err(_) => None,
        }
    }
```
After
```rust
}

    fn flattened_result(&self) -> TransactionResult<()> {
        self.as_ref()
```

## Snippet 2

Context: `runtime/src/bank/check_transactions.rs:134` (changes signature or replay validation logic)

Before
```rust
}

    pub(super) fn check_and_load_message_nonce_account(
        &self,
        message: &SanitizedMessage,
        next_durable_nonce: &DurableNonce,
    ) -> Option<(NonceInfo, nonce::state::Data)> {
        let nonce_is_advanceable = message.recent_blockhash() != next_durable_nonce.as_hash();
```
After
```rust
}

    pub(super) fn check_load_and_advance_message_nonce_account(
        &self,
        message: &SanitizedMessage,
        next_durable_nonce: &DurableNonce,
        next_lamports_per_signature: u64,
    ) -> Option<(NonceInfo, u64)> {
```

## Snippet 3

Context: `runtime/src/bank/check_transactions.rs:117` (changes signature or replay validation logic)

Before
```rust
lamports_per_signature: hash_info.lamports_per_signature(),
            })
        } else if let Some((nonce, nonce_data)) =
            self.check_and_load_message_nonce_account(tx.message(), next_durable_nonce)
        {
            Ok(CheckedTransactionDetails {
                nonce: Some(nonce),
                lamports_per_signature: nonce_data.get_lamports_per_signature(),
```
After
```rust
lamports_per_signature: hash_info.lamports_per_signature(),
            })
        } else if let Some((nonce, previous_lamports_per_signature)) = self
            .check_load_and_advance_message_nonce_account(
                tx.message(),
                next_durable_nonce,
                next_lamports_per_signature,
            )
```

## Snippet 4

Context: `svm/src/rollback_accounts.rs:52` (changes signature or replay validation logic)

Before
```rust
if let Some(nonce) = nonce {
            if &fee_payer_address == nonce.address() {
                RollbackAccounts::SameNonceAndFeePayer {
                    nonce: NonceInfo::new(fee_payer_address, fee_payer_account),
```
After
```rust
if let Some(nonce) = nonce {
            if &fee_payer_address == nonce.address() {
                // `nonce` contains an AccountSharedData which has already been advanced to the current DurableNonce
                // `fee_payer_account` is an AccountSharedData as it currently exists on-chain
                // thus if the nonce account is being used as the fee payer, we need to update that data here
                // so we capture both the data change for the nonce and the lamports/rent epoch change for the fee payer
                fee_payer_account.set_data_from_slice(nonce.account().data());
```

# Fix Pattern

Advance durable nonce state before or as the transaction enters fee-paying handling, and ensure rollback state preserves advanced nonce data together with fee-payer lamport and rent adjustments.

## How It Was Fixed

The patch replaced load-only nonce checking with load-and-advance nonce checking in `runtime/src/bank/check_transactions.rs`. It also updated `svm/src/rollback_accounts.rs` so the same-account nonce-and-fee-payer rollback case copies the already-advanced nonce data into the rollback fee payer account representation.

# Why It Matters

1. Durable nonce reuse prevention depends on consuming the nonce once fees are charged.

2. Fee-only or failed transactions must not leave the old nonce reusable.

3. Rollback state can otherwise undo nonce advancement while keeping fee-related side effects.

4. The evidence supports replay-sensitive nonce correctness, not broader claims such as signature bypass or fund theft.

# Evidence Notes

Grounded evidence comes from the changed helper name and signature in `runtime/src/bank/check_transactions.rs`, its use from `check_transaction_age`, the switch from nonce account lamports-per-signature data to a returned previous lamports-per-signature value, and comments in `svm/src/rollback_accounts.rs` stating that `nonce` contains account data already advanced to the current durable nonce. The commit message also states that rollback accounts previously carried an untouched nonce and that the patch advances nonce when creating rollback accounts. Claims about attacker profit, consensus divergence, signature verification bypass, or theft are unsupported by the provided evidence. Protocol security invariant: A durable nonce transaction that enters the fee-paying path must consume and advance the nonce even if execution later fails or only fees are charged; rollback state must not restore an untouched nonce while preserving fee-payer side effects. Verification notes: The patch does not prove an attacker could profit from replaying transactions. The evidence does not show bypass of signature verification. The evidence does not establish consensus divergence or fund theft by itself. The transaction_processing_result.rs change appears supporting/refactor-like unless tied to the nonce state-flow changes. The precise behavior for all failed transaction classes is not proven beyond the fee-only nonce path described by the commit and shown snippets. Supported: nonce handling moved from load-only to load-and-advance in transaction age checking. Supported: rollback same-account nonce-and-fee-payer case now preserves advanced nonce data. Supported: commit message identifies fee-only nonce transactions and untouched rollback nonce state. Not supported: practical exploitability or concrete attacker impact. Not supported: independent security relevance of the transaction result helper removal. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `durable-nonce-consumption`
Final impact type: `replay-risk`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, durable-nonce, replay-prevention, state-rollback, fee-only-transaction`

The supplied patch evidence supports retaining this as security hardening, not a fully proven security fix. The code moves durable nonce handling from load-only behavior to load-and-advance behavior during transaction age checking, and rollback construction now preserves already-advanced nonce data when the nonce account is also the fee payer. That clearly tightens replay-sensitive nonce consumption semantics, especially for fee-only or failed transactions, but the evidence does not prove practical exploitability, signature bypass, theft, or consensus divergence.

## Security Evidence

1. Commit subject and body explicitly describe advancing nonce for fee-only transactions and fixing rollback accounts that previously carried an untouched nonce.
2. runtime/src/bank/check_transactions.rs changes the durable nonce fallback from check-and-load to check-load-and-advance, with next durable nonce and lamports-per-signature inputs.
3. check_transaction_age now receives a nonce object that has gone through the advance path while preserving previous lamports-per-signature for fee calculation.
4. svm/src/rollback_accounts.rs comments state the nonce account data is already advanced and copies that data when nonce and fee payer are the same account.
5. The touched behavior concerns durable nonce consumption, a replay-sensitive transaction-processing invariant.

## Missing Evidence

1. No evidence demonstrates that an attacker could actually replay a transaction successfully in production.
2. No evidence shows signature verification bypass or forged authorization.
3. No evidence establishes fund theft, privilege escalation, or consensus divergence.
4. The transaction_processing_result.rs change is not independently shown to be security-relevant.
5. The exact affected failure modes beyond fee-only or rollback nonce handling are not fully proven by the snippets.

## Claim Boundaries

1. Keep claims limited to durable nonce consumption and rollback-state correctness.
2. Do not claim concrete exploitability or attacker profit from the provided evidence alone.
3. Do not characterize this as a signature-validation bug; the evidence is about nonce state advancement and replay prevention.
4. Treat this as security hardening of a replay-sensitive invariant rather than a confirmed exploitable vulnerability.
