---
case_id: case_20200502_fa254ff18f
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2020-05-02
source_refs:
  - git:fa254ff18f5c0793a092628679ede5da5f2eb1b8
  - "runtime/src/accounts.rs:148"
  - "runtime/src/accounts.rs:577"
  - "runtime/src/bank.rs:1070"
  - "runtime/src/accounts.rs:1362"
bug_class: malformed-transaction-validation-ordering
impact_type:
  - transaction-validation-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - input-validation
  - account-locking
  - fuzzer-driven
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch moves transaction sanitization and duplicate-account-key rejection into `Accounts::lock_accounts` before lock key derivation, removes the duplicate-key rejection from later account loading, and removes a separate post-lock reference-check path in `Bank`. This is plausibly security relevant because it affects malformed transaction handling in runtime account locking, but the evidence does not prove a vulnerability or exploit path.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch replaces `// Check for unique account keys` with `// There is no way to predict what program will execute without an error`.

2. In `runtime/src/accounts.rs`, the patch replaces `let keys: Vec<_> = OrderedIterator::new(txs, txs_iteration_order)` with `let keys: Vec<Result<_>> = OrderedIterator::new(txs, txs_iteration_order)`.

3. In `runtime/src/bank.rs`, the patch replaces `fn check_refs(` with `fn check_age(`.

4. In `runtime/src/accounts.rs`, the patch replaces `assert_eq!(error_counters.account_loaded_twice, 1);` with `Err(TransactionError::InvalidAccountForFee),`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/system_instruction_processor.rs`, `runtime/src/message_processor.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/system_instruction_processor.rs`, `runtime/src/message_processor.rs`. The strongest project-level identifiers around this patch are `TransactionError::AccountLoadedTwice`, `OrderedIterator::new`, `TransactionError`, and `Self::has_duplicates`.

## Before/After Behavior

Before the patch, account locking derived lock keys from transaction messages without the shown evidence of first calling `tx.sanitize()` or rejecting duplicate account keys at that boundary. Duplicate account keys were rejected later in `load_tx_accounts`, and `Bank::check_refs` separately checked sanitization after locks for successful lock results. After the patch, `lock_accounts` calls `tx.sanitize()`, maps failures to `TransactionError::SanitizeFailure`, rejects duplicate `tx.message.account_keys` with `TransactionError::AccountLoadedTwice`, and only then derives lock keys. The later duplicate check in account loading and the separate `check_refs` path are removed in the supplied evidence.

# Root Cause

The grounded root cause is validation ordering and duplication: malformed transaction checks were split across account locking, post-lock bank validation, and account loading. The evidence does not show a concrete state corruption, unauthorized access, balance impact, consensus failure, or remotely exploitable crash.

## Walkthrough

1. A transaction enters the account-locking path through `Accounts::lock_accounts`.

2. Before the patch, the shown code collected writable and readonly keys using `tx.message().get_account_keys_by_lock_type()`.

3. Duplicate account keys were checked later in `load_tx_accounts`, returning `TransactionError::AccountLoadedTwice`.

4. A separate `Bank::check_refs` path checked `tx.sanitize().is_err()` after successful locks.

5. After the patch, `lock_accounts` calls `tx.sanitize()` before deriving lock keys.

6. After sanitization, `lock_accounts` rejects duplicate account keys with `TransactionError::AccountLoadedTwice`.

7. The later duplicate-key rejection in `load_tx_accounts` is removed.

8. The pay-to-self test expectation changes from load-time `AccountLoadedTwice` to `InvalidAccountForFee`, showing changed error ordering for that path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts.rs | 135 | account loading no longer performs the duplicate account key rejection at this later stage |
| runtime/src/accounts.rs | 574 | account locking now sanitizes each transaction and rejects duplicate account keys before deriving lock sets |
| runtime/src/bank.rs | 1055 | bank processing removes the separate post-lock reference validation path |
| runtime/src/accounts.rs | 1343 | test expectation changes for a pay-to-self duplicate-account transaction error path |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts.rs:148` (changes a sensitive control or state-update path)

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

Context: `runtime/src/accounts.rs:577` (changes a sensitive control or state-update path)

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

Context: `runtime/src/bank.rs:1070` (changes a sensitive control or state-update path)

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

Context: `runtime/src/accounts.rs:1362` (changes the branch that decides whether execution stops or continues)

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

Move malformed transaction validation to the earlier shared boundary that consumes transaction shape for lock derivation, and remove later duplicate validation paths whose ordering no longer matches the new flow.

## How It Was Fixed

`Accounts::lock_accounts` now imports `Sanitize`, returns per-transaction key derivation results, sanitizes each transaction, rejects duplicate account keys, and then derives lock sets. The duplicate-key check was removed from `load_tx_accounts`, and the shown `Bank::check_refs` post-lock validation function was removed.

# Why It Matters

1. Account locks are now derived only after sanitization succeeds.

2. Duplicate account keys are rejected earlier in the lock path.

3. Validation logic is less split across runtime stages.

4. Security impact is not proven by the supplied evidence.

5. The commit may be fuzzer-driven robustness cleanup.

# Evidence Notes

Evidence is limited to hunks in `runtime/src/accounts.rs`, `runtime/src/bank.rs`, and a changed test expectation. The code supports a malformed transaction validation and error-ordering change. It does not support claims of unauthorized account access, balance theft, consensus divergence, state corruption, or a remotely exploitable crash. Protocol security invariant: Transactions should be sanitized and duplicate account keys should be rejected before account lock sets are derived. The provided evidence supports a validation-ordering cleanup in this critical path, but does not establish that the prior ordering violated a proven security invariant in an exploitable way. Verification notes: The patch does not prove unauthorized account access or balance theft. The patch does not prove consensus divergence from the provided evidence alone. The patch does not prove a remotely exploitable crash, only malformed transaction validation changes. The commit subject references fuzzer fixes, so some changes may be robustness cleanup rather than a confirmed vulnerability fix. No exploit scenario is provided. No consensus or balance-impact evidence is provided. No security advisory or vulnerability description is included. The safest classification is security-relevant unclear work, not a confirmed security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `malformed-transaction-validation-ordering`
Final impact type: `transaction-validation-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, input-validation, account-locking, fuzzer-driven`

The patch does not prove a concrete exploitable vulnerability, but it does move transaction sanitization and duplicate account-key rejection into the account-locking boundary before lock key derivation in a blockchain runtime. That is a security-sensitive validation-ordering hardening change. The original state-corruption and signature framing is too strong for the supplied evidence.

## Security Evidence

1. `Accounts::lock_accounts` now calls `tx.sanitize()` before deriving account lock keys.
2. Duplicate account keys are rejected in `lock_accounts` before lock acquisition logic proceeds.
3. A separate post-lock sanitization path in `Bank::check_refs` is removed, indicating validation was intentionally centralized earlier.
4. The changed path is transaction processing and account locking in blockchain runtime code.

## Missing Evidence

1. No advisory, CVE, exploit scenario, or vulnerability description is provided.
2. No evidence shows unauthorized account access, fund loss, consensus divergence, or state corruption.
3. No proof that the prior post-lock validation allowed malformed transactions to execute successfully.
4. Commit subject references fuzzer fixes, which may also indicate robustness work.

## Claim Boundaries

1. This should not be described as a confirmed security fix.
2. Do not claim balance theft, signature bypass, state corruption, or consensus failure from this evidence alone.
3. The supported claim is earlier rejection of malformed or duplicate-account-key transactions in a security-sensitive lock derivation path.
4. Classification should remain hardening with medium confidence, not a concrete vulnerability class.
