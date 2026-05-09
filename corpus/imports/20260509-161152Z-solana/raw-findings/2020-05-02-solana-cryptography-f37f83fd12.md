---
case_id: case_20200502_f37f83fd12
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: medium
date: 2020-05-02
source_refs:
  - git:f37f83fd12cd14f08950e69ca2ca7c45ecb169f6
  - "runtime/src/accounts.rs:144"
  - "runtime/src/accounts.rs:569"
  - "runtime/src/bank.rs:1071"
  - "runtime/src/accounts.rs:1354"
bug_class: transaction-sanitization-ordering
impact_type:
  - malformed-transaction-rejection
  - runtime-validation-hardening
confidence: medium
tags:
  - blockchain-core
  - runtime
  - transaction-validation
  - account-locking
  - sanitization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch moves transaction sanitization and duplicate account-key rejection into `Accounts::lock_accounts`, before account lock key extraction. It removes the duplicate-key check from `load_tx_accounts` and removes the shown later `Bank::check_refs` sanitization path. This is a grounded validation-order cleanup or hardening change, but the supplied evidence does not prove a vulnerability, exploitability, consensus break, balance impact, replay issue, or signature-validation flaw.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch replaces `// Check for unique account keys` with `// There is no way to predict what program will execute without an error`.

2. In `runtime/src/accounts.rs`, the patch replaces `let keys: Vec<_> = OrderedIterator::new(txs, txs_iteration_order)` with `let keys: Vec<Result<_>> = OrderedIterator::new(txs, txs_iteration_order)`.

3. In `runtime/src/bank.rs`, the patch replaces `fn check_refs(` with `fn check_age(`.

4. In `runtime/src/accounts.rs`, the patch replaces `assert_eq!(error_counters.account_loaded_twice, 1);` with `Err(TransactionError::InvalidAccountForFee),`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/system_instruction_processor.rs`, `runtime/src/message_processor.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/system_instruction_processor.rs`, `runtime/src/message_processor.rs`. The strongest project-level identifiers around this patch are `TransactionError::AccountLoadedTwice`, `OrderedIterator::new`, `TransactionError`, and `Self::has_duplicates`.

## Before/After Behavior

Before the patch, `lock_accounts` derived writable and readonly lock keys directly from each transaction message. Duplicate account-key rejection was performed later in `load_tx_accounts`, and `Bank::check_refs` separately checked transaction sanitization after lock results existed. After the patch, `lock_accounts` calls `tx.sanitize()`, maps failures to `TransactionError::SanitizeFailure`, checks for duplicate `tx.message.account_keys`, and only then derives account lock keys. The pay-to-self test was updated so the later account-loading path no longer expects `AccountLoadedTwice`.

# Root Cause

The provided evidence supports only that validation was split across stages and was moved earlier into the account-locking path. It does not show that this ordering allowed an attacker to bypass locks, corrupt state, forge signatures, replay transactions, or otherwise exploit the runtime.

## Walkthrough

1. A transaction reaches `Accounts::lock_accounts` before account loading.

2. Before the change, `lock_accounts` collected lock keys using `tx.message().get_account_keys_by_lock_type()` without the shown sanitize or duplicate-key checks.

3. The old duplicate account-key check appeared later in `load_tx_accounts`.

4. The old `Bank::check_refs` path checked `tx.sanitize()` after lock results were already available.

5. The patch adds `tx.sanitize()` inside `lock_accounts` before lock key extraction.

6. The patch adds duplicate account-key rejection inside `lock_accounts`.

7. The duplicate-key rejection block is removed from `load_tx_accounts`.

8. The shown `Bank::check_refs` sanitization function is removed, consistent with moving sanitization earlier.

9. The updated test confirms changed behavior at the account-loading stage, but does not demonstrate a security exploit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts.rs | 144 | removed duplicate account-key rejection from account loading path |
| runtime/src/accounts.rs | 566 | adds transaction sanitization before account lock key extraction |
| runtime/src/accounts.rs | 569 | adds duplicate account-key rejection during account locking |
| runtime/src/bank.rs | 1071 | removes separate post-lock transaction reference sanitization check |
| runtime/src/accounts.rs | 1335 | updates test expectation for pay-to-self duplicate account behavior after validation moved |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts.rs:144` (changes a sensitive control or state-update path)

Before
```rust
Err(TransactionError::MissingSignatureForFee)
        } else {
            // Check for unique account keys
            if Self::has_duplicates(&message.account_keys) {
                error_counters.account_loaded_twice += 1;
                return Err(TransactionError::AccountLoadedTwice);
            }
```
After
```rust
Err(TransactionError::MissingSignatureForFee)
        } else {
            // There is no way to predict what program will execute without an error
            // If a fee can pay for execution then the program will be scheduled
```

## Snippet 2

Context: `runtime/src/accounts.rs:569` (changes a sensitive control or state-update path)

Before
```rust
txs_iteration_order: Option<&[usize]>,
    ) -> Vec<Result<()>> {
        let keys: Vec<_> = OrderedIterator::new(txs, txs_iteration_order)
            .map(|tx| tx.message().get_account_keys_by_lock_type())
            .collect();
        let mut account_locks = &mut self.account_locks.lock().unwrap();
        keys.into_iter()
            .map(|(writable_keys, readonly_keys)| {
```
After
```rust
txs_iteration_order: Option<&[usize]>,
    ) -> Vec<Result<()>> {
        use solana_sdk::sanitize::Sanitize;
        let keys: Vec<Result<_>> = OrderedIterator::new(txs, txs_iteration_order)
            .map(|tx| {
                tx.sanitize()
                    .map_err(|_| TransactionError::SanitizeFailure)?;
```

## Snippet 3

Context: `runtime/src/bank.rs:1071` (changes a sensitive control or state-update path)

Before
```rust
)
    }
    fn check_refs(
        &self,
        txs: &[Transaction],
        iteration_order: Option<&[usize]>,
        lock_results: &[Result<()>],
        error_counters: &mut ErrorCounters,
```
After
```rust
)
    }
    fn check_age(
        &self,
```

## Snippet 4

Context: `runtime/src/accounts.rs:1354` (changes the branch that decides whether execution stops or continues)

Before
```rust
let loaded_accounts = load_accounts(tx, &accounts, &mut error_counters);

        assert_eq!(error_counters.account_loaded_twice, 1);
        assert_eq!(loaded_accounts.len(), 1);
        assert_eq!(
            loaded_accounts[0],
            (
                Err(TransactionError::AccountLoadedTwice),
```
After
```rust
let loaded_accounts = load_accounts(tx, &accounts, &mut error_counters);

        assert_eq!(loaded_accounts.len(), 1);
        assert_eq!(
            loaded_accounts[0],
            (
                Err(TransactionError::InvalidAccountForFee),
                Some(HashAgeKind::Extant)
```

# Fix Pattern

Move malformed-transaction checks to the boundary that first consumes the transaction structure for account locking.

## How It Was Fixed

`Accounts::lock_accounts` now imports `Sanitize`, calls `tx.sanitize()`, returns `TransactionError::SanitizeFailure` on sanitize failure, and returns `TransactionError::AccountLoadedTwice` for duplicate account keys before deriving lock key sets. The later duplicate-key and sanitize checks shown in other paths were removed or adjusted.

# Why It Matters

1. Earlier validation can reduce inconsistent handling across runtime stages.

2. Account-lock derivation depends on transaction account metadata being well formed.

3. The patch is plausibly hardening, but exploitability is not established.

# Evidence Notes

Evidence is limited to diffs in `runtime/src/accounts.rs`, `runtime/src/bank.rs`, and a test expectation update. The commit subject says fuzzer test and fixes, but no commit body or issue context is provided. Claims about replay, cryptography, signature validation, balance impact, consensus corruption, or concrete attacker control are unsupported by the supplied evidence. Protocol security invariant: Transactions should be sanitized and duplicate account keys should be rejected before runtime code derives account lock keys from the transaction message. The provided evidence shows this invariant was enforced earlier after the patch, but does not establish that the previous ordering caused an exploitable security failure. Verification notes: The patch does not prove signature forgery, replay acceptance, or cryptographic failure. The patch does not show an end-to-end exploit against account balances or consensus state. The changed test shows behavior adjustment, not an attacker-controlled exploit path. The evidence supports validation relocation and hardening more strongly than a confirmed vulnerability fix. Grounded: sanitization moved into `Accounts::lock_accounts`. Grounded: duplicate account-key rejection moved from account loading to account locking. Grounded: later `Bank::check_refs` sanitization path was removed from the shown code. Unsupported: confirmed vulnerability or exploit path. Unsupported: replay or signature-validation bug class. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-sanitization-ordering`
Final impact type: `malformed-transaction-rejection, runtime-validation-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, runtime, transaction-validation, account-locking, sanitization`

The evidence supports retaining this as security hardening, not as a concrete security fix. The patch moves transaction sanitization and duplicate account-key rejection into the account-locking path before lock key extraction, which tightens validation at a security-sensitive runtime boundary. However, the evidence does not prove exploitability, replay, signature bypass, balance loss, or consensus corruption, so the original replay/signature framing is too strong.

## Security Evidence

1. `lock_accounts` now calls `tx.sanitize()` before deriving account lock keys.
2. Duplicate account keys are rejected in `lock_accounts` with `TransactionError::AccountLoadedTwice`.
3. The old later sanitization/reference check is removed, consistent with moving validation earlier.
4. The changed path is in Solana runtime account locking, a security-sensitive blockchain execution boundary.

## Missing Evidence

1. No commit body, issue, advisory, or exploit description is provided.
2. No evidence shows a transaction could bypass signatures or be replayed.
3. No evidence demonstrates balance impact, consensus divergence, or state corruption.
4. The test update shows changed validation ordering but not attacker exploitability.

## Claim Boundaries

1. Validate only as transaction validation/account-locking hardening.
2. Do not classify as cryptographic failure, replay, or signature-validation bypass.
3. Do not claim a confirmed exploitable vulnerability from this patch alone.
4. The strongest supported claim is earlier rejection of malformed or duplicate-key transactions before account locking.
