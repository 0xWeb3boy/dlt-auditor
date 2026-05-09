---
case_id: case_20251227_346847efe6
project: agave
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2025-12-27
source_refs:
  - git:346847efe6cdc4437adde44c8499b3b1b61e7e85
  - "runtime/src/bank/check_transactions.rs:223"
  - "runtime/src/bank/check_transactions.rs:342"
  - "svm/src/transaction_processor.rs:740"
  - "svm/src/transaction_processor.rs:646"
bug_class: nonce-state-validation-timing
impact_type:
  - replay-risk-reduction
  - authorization-validation-hardening
tags:
  - blockchain-core
  - durable-nonce
  - nonce-validation
  - svm
  - authorization-check
  - replay-sensitive-state
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch moves construction of durable nonce execution state out of the early Bank transaction-age check and into SVM transaction processing, where the nonce account is reloaded and validated closer to execution. The evidence supports a security-relevant nonce state and authorization timing hardening, especially around SIMD83-style lock relaxation, but does not prove a concrete exploit or unauthorized transaction acceptance.

## Observed Patch Facts

1. In `runtime/src/bank/check_transactions.rs`, the patch replaces `let nonce_is_authorized = message` with `Some((*nonce_address, nonce_data))`.

2. In `runtime/src/bank/check_transactions.rs`, the patch replaces `let nonce_account = bank.get_account(&nonce_pubkey).unwrap();` with `assert_eq!(`.

3. In `svm/src/transaction_processor.rs`, the patch replaces `nonce_info: &NonceInfo,` with `nonce_address: &Pubkey,`.

4. In `svm/src/transaction_processor.rs`, the patch replaces `// If this is a nonce transaction, validate the nonce info.` with `next_lamports_per_signature: u64,`.

## Project Context

The changed code sits primarily in `runtime/src/bank`, `runtime/src`, `svm/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `svm/src/nonce_info.rs`, `svm/src/message_processor.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `svm/src/account_loader.rs`, `runtime/src/bank/tests.rs`. The strongest project-level identifiers around this patch are `nonce_account`, `bank`, `nonce`, and `next_lamports_per_signature`.

## Before/After Behavior

Before the change, the Bank-side nonce path loaded and verified nonce account data and also checked the nonce authority signer during transaction age checking. After the change, the Bank-side check only identifies a valid durable nonce transaction and carries forward the nonce address plus the previous lamports_per_signature. SVM processing then reloads the nonce account, validates current state and reuse conditions, checks the current authority signer, and constructs NonceInfo there.

# Root Cause

Nonce-related state and authority were being evaluated too early relative to later transaction processing. With mutable nonce account conditions such as prior use, close/reopen, spoofing, or authority change, early validation could become stale unless the processing path revalidated the current account state.

## Walkthrough

1. Transaction age checking first chooses the normal blockhash path or durable nonce path.

2. For durable nonce transactions, Bank-side checking now verifies the nonce account against the transaction blockhash and records the nonce address plus prior fee data.

3. The Bank-side helper no longer performs the final nonce authority signer check or builds full NonceInfo.

4. Checked transaction details carry the nonce address into SVM transaction processing.

5. The SVM processor reloads the nonce account through AccountLoader before constructing NonceInfo.

6. Processing-time validation checks current nonce account validity, reuse conditions, and current authority signer status.

7. Transactions whose nonce account was already used, closed, reopened in an invalid form, spoofed, or had authority changed are intended to fail at this later validation point.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank/check_transactions.rs | 167 | initial transaction age check chooses blockhash path or durable nonce path and carries nonce address plus previous lamports_per_signature |
| runtime/src/bank/check_transactions.rs | 223 | loads nonce account data and no longer performs final nonce authority signer check at this early Bank stage |
| svm/src/transaction_processor.rs | 643 | passes checked nonce address into processing-time validation along with next_lamports_per_signature |
| svm/src/transaction_processor.rs | 739 | reloads and validates current nonce account state, batch reuse, and current authority signer before producing NonceInfo |
| runtime/src/bank/check_transactions.rs | 308 | regression test updates expected behavior for nonce validity and stale lamports_per_signature handling |

## Code Snippets

## Snippet 1

Context: `runtime/src/bank/check_transactions.rs:223` (changes a sensitive control or state-update path)

Before
```rust
nonce_account::verify_nonce_account(&nonce_account, message.recent_blockhash())?;

        let nonce_is_authorized = message
            .get_ix_signers(NONCED_TX_MARKER_IX_INDEX as usize)
            .any(|signer| signer == &nonce_data.authority);
        if !nonce_is_authorized {
            return None;
        }
```
After
```rust
nonce_account::verify_nonce_account(&nonce_account, message.recent_blockhash())?;

        Some((*nonce_address, nonce_data))
    }
```

## Snippet 2

Context: `runtime/src/bank/check_transactions.rs:342` (changes the branch that decides whether execution stops or continues)

Before
```rust
bank.store_account(&nonce_pubkey, &nonce_account);

        let nonce_account = bank.get_account(&nonce_pubkey).unwrap();
        let (_, next_lamports_per_signature) = bank.last_blockhash_and_lamports_per_signature();
        let mut expected_nonce_info = NonceInfo::new(nonce_pubkey, nonce_account);
        expected_nonce_info
            .try_advance_nonce(bank.next_durable_nonce(), next_lamports_per_signature)
            .unwrap();
```
After
```rust
bank.store_account(&nonce_pubkey, &nonce_account);

        assert_eq!(
            bank.check_nonce_transaction_validity(&message, &bank.next_durable_nonce()),
            Some((nonce_pubkey, STALE_LAMPORTS_PER_SIGNATURE)),
        );
    }
```

## Snippet 3

Context: `svm/src/transaction_processor.rs:740` (changes an authorization or privilege gate)

Before
```rust
account_loader: &mut AccountLoader<CB>,
        message: &impl SVMMessage,
        nonce_info: &NonceInfo,
        next_durable_nonce: &DurableNonce,
        error_counters: &mut TransactionErrorMetrics,
    ) -> TransactionResult<()> {
        // When SIMD83 is enabled, if the nonce has been used in this batch already, we must drop
        // the transaction. This is the same as if it was used in different batches in the same slot.
```
After
```rust
account_loader: &mut AccountLoader<CB>,
        message: &impl SVMMessage,
        nonce_address: &Pubkey,
        next_durable_nonce: &DurableNonce,
        next_lamports_per_signature: u64,
        error_counters: &mut TransactionErrorMetrics,
    ) -> TransactionResult<NonceInfo> {
        // When SIMD83 is enabled, if the nonce has been used in this batch already, we must drop
```

## Snippet 4

Context: `svm/src/transaction_processor.rs:646` (changes signature or replay validation logic)

Before
```rust
checked_details: CheckedTransactionDetails,
        environment_blockhash: &Hash,
        rent: &Rent,
        error_counters: &mut TransactionErrorMetrics,
    ) -> TransactionResult<ValidatedTransactionDetails> {
        // If this is a nonce transaction, validate the nonce info.
        // This must be done for every transaction to support SIMD83 because
        // it may have changed due to use, authorization, or deallocation.
```
After
```rust
checked_details: CheckedTransactionDetails,
        environment_blockhash: &Hash,
        next_lamports_per_signature: u64,
        rent: &Rent,
        error_counters: &mut TransactionErrorMetrics,
    ) -> TransactionResult<ValidatedTransactionDetails> {
        let CheckedTransactionDetails {
            nonce_address,
```

# Fix Pattern

Defer construction of sensitive nonce execution state until the processing stage, and revalidate mutable account state and authorization immediately before accepting the transaction for processing.

## How It Was Fixed

The Bank nonce validity check was narrowed to nonce identification and fee-data extraction. The SVM transaction processor now receives the nonce address, reloads the account, validates the current nonce state and signer authorization, accounts for batch reuse constraints, and returns freshly built NonceInfo. Tests were updated so Bank nonce validity checking returns the stale lamports_per_signature value rather than pre-advancing NonceInfo.

# Why It Matters

1. Durable nonce reuse is replay-sensitive protocol state.

2. Nonce authority can change after an early check.

3. Closed or reopened nonce accounts need current-state validation.

4. Fee-only handling still needs nonce validity checks.

5. The evidence supports hardening, not a proven exploit scenario.

# Evidence Notes

Grounded evidence comes from changes in runtime/src/bank/check_transactions.rs and svm/src/transaction_processor.rs. The strongest support is the new processing-time validation shape and comments describing used, closed, reopened, spoofed, and authority-changed nonce accounts. Unsupported claims about cryptographic primitive failure, fund theft, remote exploitability, or a confirmed end-to-end vulnerability are removed. Protocol security invariant: A durable nonce transaction should only proceed if the referenced nonce account is still valid for the transaction blockhash, has not already been consumed under the relevant batch or slot rules, and is authorized by the nonce authority current at processing time. Verification notes: The patch does not prove that unauthorized transactions were accepted before the change in all configurations. The patch does not prove remote exploitability or economic impact. The patch does not show cryptographic primitive failure; it concerns nonce account state and authorization validation timing. The patch may also be enabling/refactoring behavior for SIMD83 lock relaxation, so security classification should stay tied to the concrete nonce validation invariant. No external context or file inspection was used. Provided evidence includes implementation changes and a nonce validity test update. Classification is downgraded from confirmed security fix to likely security hardening because the input does not establish exploitability or prior acceptance of invalid transactions in a complete scenario. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `nonce-state-validation-timing`
Final impact type: `replay-risk-reduction, authorization-validation-hardening`
Final tags: `blockchain-core, durable-nonce, nonce-validation, svm, authorization-check, replay-sensitive-state`

The supplied patch evidence supports retaining this as security hardening: nonce account state and authority validation are moved from an earlier Bank-side check into transaction processing, where the account is reloaded and checked closer to execution. Comments explicitly mention used, closed, reopened, spoofed, or authority-changed nonce accounts being rejected. The evidence does not prove a concrete exploitable bug or confirmed unauthorized transaction acceptance, so it should not be classified as a confirmed security fix.

## Security Evidence

1. Bank-side nonce checking no longer performs the final authority signer check or constructs full nonce execution state early.
2. SVM transaction processing now accepts the nonce address, reloads the nonce account, and returns fresh NonceInfo after validation.
3. Patch comments state that used, closed, reopened, spoofed, or authority-changed nonce accounts cannot be processed, even fee-only.
4. The changed path is durable nonce handling, which is replay-sensitive transaction validity state.

## Missing Evidence

1. No end-to-end exploit scenario is shown.
2. No proof that unauthorized nonce transactions were previously accepted.
3. No demonstrated economic impact, fund loss, or remote attack path.
4. No evidence of cryptographic primitive failure.

## Claim Boundaries

1. Classify as hardening of nonce validation timing, not a confirmed vulnerability fix.
2. Do not claim general signature verification or cryptographic failure.
3. Do not claim proven replay execution beyond replay-risk reduction.
4. Security relevance is tied to durable nonce state, account reload, and current authority validation.
