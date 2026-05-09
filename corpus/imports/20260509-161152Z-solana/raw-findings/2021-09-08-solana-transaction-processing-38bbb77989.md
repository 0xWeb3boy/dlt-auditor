---
case_id: case_20210908_38bbb77989
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
impact_type:
  - state-integrity
source_quality: high
date: 2021-09-08
source_refs:
  - git:38bbb779890c363cb4b7bcf7b19c1348fe41320c
  - "runtime/src/accounts.rs:251"
  - "runtime/src/accounts.rs:275"
  - "runtime/src/bank.rs:3123"
  - "runtime/src/accounts.rs:1700"
bug_class: account-mutability-validation
confidence: medium
tags:
  - infrastructure
  - transaction-processing
  - runtime-validation
  - writable-account
  - upgradeable-loader
  - account-mutability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens Solana runtime account-loading validation so transactions that request writable access to executable accounts or upgradeable-loader-owned accounts are rejected in the relevant loader-controlled cases. The evidence supports a security-relevant mutability invariant fix, but not stronger claims such as arbitrary code modification, consensus failure, or demonstrated state corruption.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch removes `if message.is_writable(i, demote_program_write_locks) {`.

2. In `runtime/src/accounts.rs`, the patch replaces `if account.executable() && bpf_loader_upgradeable::check_id(account.owner())` with `if bpf_loader_upgradeable::check_id(account.owner()) {`.

3. In `runtime/src/bank.rs`, the patch adds `if 0 != error_counters.invalid_writable_account {`.

4. In `runtime/src/accounts.rs`, the patch replaces `fn test_accounts_account_not_found() {` with `fn test_load_accounts_executable_with_write_lock() {`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/accounts_db.rs`, `runtime/src/vote_account.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/accounts_db.rs`, `runtime/src/vote_account.rs`. The strongest project-level identifiers around this patch are `account`, `bpf_loader_upgradeable::check_id`, `error_counters`, and `invalid_writable_account`.

## Before/After Behavior

Before the patch, the visible upgradeable-loader check in `runtime/src/accounts.rs::load_transaction` was limited by `account.executable() && bpf_loader_upgradeable::check_id(account.owner())`, and the instructions sysvar branch had a separate writable check returning `TransactionError::InvalidAccountIndex`. After the patch, the upgradeable-loader check is based on `bpf_loader_upgradeable::check_id(account.owner())`, with rejection when `demote_program_write_locks` is active, the account is writable, and the upgradeable loader is not present. `runtime/src/bank.rs` also records the new `invalid_writable_account` counter, and tests cover executable accounts requested with a write lock.

# Root Cause

The account-loading validation around loader-managed program state was too narrow. The provided diff supports that writable handling was previously conditioned on executable upgradeable-loader-owned accounts, while the fix applies validation based on upgradeable-loader ownership and loader presence.

## Walkthrough

1. A sanitized transaction reaches `runtime/src/accounts.rs::load_transaction`, which iterates through account keys and loads accounts before execution.

2. For non-loader keys, the runtime determines whether an account is writable using `message.is_writable(i, demote_program_write_locks)`.

3. Before the fix, the visible upgradeable-loader-specific logic was gated by both executable status and upgradeable-loader ownership.

4. The patch changes that guard to upgradeable-loader ownership, making non-executable loader-owned state visible to the same validation path.

5. The new rejection path applies when program write-lock demotion is active, the account is writable, and the upgradeable loader is absent from the transaction.

6. When this invalid writable-account condition is hit, the runtime increments `error_counters.invalid_writable_account` and fails the transaction through the new error path described by the commit context.

7. Bank metrics were updated to report `bank-process_transactions-error-invalid_writable_account`.

8. Regression tests were added for executable-account write-lock handling.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts.rs | 219 | loads transaction accounts and decides whether account keys marked writable are accepted before execution |
| runtime/src/accounts.rs | 275 | checks upgradeable-loader-owned accounts and rejects invalid writable access when the loader is absent |
| runtime/src/bank.rs | 3123 | records the new invalid writable account transaction error counter |
| runtime/src/accounts.rs | 1700 | adds regression coverage for executable accounts requested with a write lock |
| sdk/src/transaction/mod.rs | 0 | adds or exposes the transaction error used for invalid writable accounts |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts.rs:251` (changes a sensitive control or state-update path)

Before
```rust
if solana_sdk::sysvar::instructions::check_id(key) {
                        if message.is_writable(i, demote_program_write_locks) {
                            return Err(TransactionError::InvalidAccountIndex);
                        }
                        Self::construct_instructions_account(
                            message,
```
After
```rust
if solana_sdk::sysvar::instructions::check_id(key) {
                        Self::construct_instructions_account(
                            message,
```

## Snippet 2

Context: `runtime/src/accounts.rs:275` (changes an authorization or privilege gate)

Before
```rust
.unwrap_or_default();

                        if account.executable() && bpf_loader_upgradeable::check_id(account.owner())
                        {
                            // The upgradeable loader requires the derived ProgramData account
                            if let Ok(UpgradeableLoaderState::Program {
                                programdata_address,
                            }) = account.state()
```
After
```rust
.unwrap_or_default();

                        if bpf_loader_upgradeable::check_id(account.owner()) {
                            if demote_program_write_locks
                                && message.is_writable(i, demote_program_write_locks)
                                && !is_upgradeable_loader_present
                            {
                                error_counters.invalid_writable_account += 1;
```

## Snippet 3

Context: `runtime/src/bank.rs:3123` (changes a sensitive control or state-update path)

Before
```rust
);
        }
    }
```
After
```rust
);
        }
        if 0 != error_counters.invalid_writable_account {
            inc_new_counter_info!(
                "bank-process_transactions-error-invalid_writable_account",
                error_counters.invalid_writable_account
            );
        }
```

## Snippet 4

Context: `runtime/src/accounts.rs:1700` (changes signature or replay validation logic)

Before
```rust
}

    #[test]
    fn test_accounts_account_not_found() {
```
After
```rust
}

    #[test]
    fn test_load_accounts_executable_with_write_lock() {
        let mut accounts: Vec<(Pubkey, AccountSharedData)> = Vec::new();
        let mut error_counters = ErrorCounters::default();

        let keypair = Keypair::new();
```

# Fix Pattern

Enforce account mutability invariants during transaction account loading, before execution, and fail transactions that request unauthorized writable access to executable or loader-managed program state.

## How It Was Fixed

The runtime guard in `load_transaction` was broadened from executable upgradeable-loader-owned accounts to upgradeable-loader-owned accounts generally. The patch added an invalid writable-account rejection path tied to loader presence, added bank-level metrics for the new counter, added a transaction error according to the commit context, and added regression coverage for executable write locks.

# Why It Matters

1. Protects the pre-execution account-loading boundary for program and loader-managed state.

2. Prevents loader-owned accounts from being treated as ordinary writable accounts when the loader is absent.

3. Makes invalid writable-account failures explicit and observable.

4. The evidence supports a mutability validation security fix, but not a proven exploit scenario.

# Evidence Notes

Grounded evidence comes from `runtime/src/accounts.rs::load_transaction`, where the check changes from `account.executable() && bpf_loader_upgradeable::check_id(account.owner())` to `bpf_loader_upgradeable::check_id(account.owner())`, and the after-snippet rejects writable upgradeable-loader-owned accounts when `demote_program_write_locks` is active and the upgradeable loader is absent. `runtime/src/bank.rs` adds reporting for `invalid_writable_account`. Tests include `test_load_accounts_executable_with_write_lock`. The input mentions `sdk/src/transaction/mod.rs`, storage proto, and conversion changes, but no code excerpts for those files were supplied, so claims about their exact contents should remain limited to commit-context support. Protocol security invariant: During transaction account loading, executable accounts and upgradeable-loader-owned program state must not be accepted as ordinary writable accounts unless the upgradeable loader is present to govern that write path. Verification notes: The patch does not by itself prove arbitrary program-code modification was possible. The patch does not prove consensus failure or chain-state corruption occurred in production. The evidence does not show a signature or owner-check bypass outside the account-loading mutability check. Storage proto and conversion changes appear supporting serialization updates for the new error, not a separate vulnerability. Supported: runtime account-loading validation was tightened for writable executable or upgradeable-loader-owned accounts. Supported: a new invalid writable-account counter is reported in bank metrics. Supported: regression coverage was added for executable write locks. Not supported: arbitrary program-code modification was possible. Not supported: consensus failure or production state corruption occurred. Not supported: helper serialization/proto files are root cause rather than supporting updates. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `account-mutability-validation`
Final confidence: `medium`
Final tags: `infrastructure, transaction-processing, runtime-validation, writable-account, upgradeable-loader, account-mutability`

The supplied patch evidence supports keeping this as a security-hardening case, not a confidently proven security-fix. The runtime now rejects transactions that request writable access to executable or upgradeable-loader-owned program state when the upgradeable loader is not present, which tightens a security-sensitive account mutability invariant in transaction loading. However, the evidence does not prove an exploit, arbitrary code modification, consensus failure, or actual state corruption, so the original state-corruption/security-fix framing is too strong.

## Security Evidence

1. Commit subject and body explicitly describe returning errors for writable executable or ProgramData accounts.
2. runtime/src/accounts.rs broadens validation from executable upgradeable-loader-owned accounts to upgradeable-loader-owned accounts generally.
3. New guard rejects writable upgradeable-loader-owned accounts when demote_program_write_locks is active and the upgradeable loader is absent.
4. A new invalid_writable_account error counter is incremented and reported.
5. Regression coverage was added for executable accounts with write locks.

## Missing Evidence

1. No supplied evidence shows a concrete exploit path or attacker-controlled code modification.
2. No supplied evidence proves production state corruption or consensus failure.
3. No supplied evidence shows signature verification or ownership authorization bypass beyond writable-account validation.
4. No detailed snippets are supplied for the new TransactionError or proto/storage changes.

## Claim Boundaries

1. Treat this as runtime hardening of account mutability rules, not as proven arbitrary program-code overwrite.
2. Do not claim demonstrated state corruption from the provided patch alone.
3. Do not classify the supporting metric/proto changes as separate vulnerabilities.
4. Do not retain the original signature-related tag because the evidence does not support a signature issue.
