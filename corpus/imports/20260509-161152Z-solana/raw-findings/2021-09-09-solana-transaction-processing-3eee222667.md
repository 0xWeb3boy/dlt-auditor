---
case_id: case_20210909_3eee222667
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2021-09-09
source_refs:
  - git:3eee22266706c464ffebbf8f075b30de72da4b99
  - "runtime/src/accounts.rs:218"
  - "runtime/src/accounts.rs:234"
  - "runtime/src/bank.rs:2814"
  - "runtime/src/accounts.rs:1690"
bug_class: improper-writable-account-validation
tags:
  - infrastructure
  - transaction-processing
  - writable-account-validation
  - program-state
  - state-integrity
  - bpf-loader-upgradeable
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens Solana runtime account loading by rejecting writable locks on upgradeable-loader-owned program accounts when the upgradeable loader is not present. The evidence supports a security-relevant runtime invariant around protected program state, but it does not prove a complete exploit or unauthorized mutation path, so the verdict is downgraded from confirmed to likely security hardening.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch removes `if message.is_writable(i, demote_program_write_locks) {`.

2. In `runtime/src/accounts.rs`, the patch replaces `if account.executable && bpf_loader_upgradeable::check_id(&account.owner) {` with `if bpf_loader_upgradeable::check_id(&account.owner) {`.

3. In `runtime/src/bank.rs`, the patch adds `if 0 != error_counters.invalid_writable_account {`.

4. In `runtime/src/accounts.rs`, the patch replaces `fn test_accounts_account_not_found() {` with `fn test_load_accounts_executable_with_write_lock() {`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/accounts_db.rs`, `runtime/src/vote_account.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/message_processor.rs`, `runtime/src/accounts_db.rs`. The strongest project-level identifiers around this patch are `account`, `bpf_loader_upgradeable::check_id`, `demote_program_write_locks`, and `error_counters`.

## Before/After Behavior

Before the patch, the visible upgradeable-loader validation was scoped to accounts satisfying both `account.executable` and `bpf_loader_upgradeable::check_id(&account.owner)`, leaving broader upgradeable-loader-owned state less clearly covered by this rejection path. After the patch, any account owned by the upgradeable loader is checked, and if program write-lock demotion is active, the transaction marks the account writable, and the upgradeable loader is absent, the runtime increments `invalid_writable_account` and rejects the transaction. Bank processing also reports the new invalid writable account counter.

# Root Cause

Transaction account-loading validation was too narrowly scoped around executable upgradeable-loader-owned accounts, rather than consistently rejecting ordinary writable locks on upgradeable-loader-owned program state when the loader-mediated path was absent.

## Walkthrough

1. `Accounts::load_transaction` computes `demote_program_write_locks` and whether the upgradeable loader is present for the transaction.

2. For each non-loader key, the runtime loads the account and determines whether the message treats it as writable.

3. Before the patch, the shown validation branch only applied when the account was both executable and owned by the upgradeable loader.

4. After the patch, the runtime checks all upgradeable-loader-owned accounts with `bpf_loader_upgradeable::check_id(&account.owner)`.

5. If the account is writable under demotion rules and the upgradeable loader is not present, the transaction is counted as `invalid_writable_account` and rejected.

6. `runtime/src/bank.rs` adds reporting for the new invalid writable account counter.

7. A regression test covers loading an executable account with a writable lock.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts.rs | 186 | Loads transaction accounts, computes `demote_program_write_locks`, detects whether the upgradeable loader is present, and applies writable-account validation during account loading. |
| runtime/src/accounts.rs | 234 | Checks upgradeable-loader-owned accounts against transaction writability and returns an invalid writable account error when the loader-mediated path is absent. |
| runtime/src/bank.rs | 2808 | Records the new invalid writable account failure counter during bank transaction processing. |
| runtime/src/accounts.rs | 1690 | Adds regression coverage for executable accounts locked writable during transaction loading. |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts.rs:218` (changes a sensitive control or state-update path)

Before
```rust
&& feature_set.is_active(&feature_set::instructions_sysvar_enabled::id())
                    {
                        if message.is_writable(i, demote_program_write_locks) {
                            return Err(TransactionError::InvalidAccountIndex);
                        }
                        Self::construct_instructions_account(message, demote_program_write_locks)
                    } else {
```
After
```rust
&& feature_set.is_active(&feature_set::instructions_sysvar_enabled::id())
                    {
                        Self::construct_instructions_account(message, demote_program_write_locks)
                    } else {
```

## Snippet 2

Context: `runtime/src/accounts.rs:234` (changes an authorization or privilege gate)

Before
```rust
.unwrap_or_default();

                        if account.executable && bpf_loader_upgradeable::check_id(&account.owner) {
                            // The upgradeable loader requires the derived ProgramData account
                            if let Ok(UpgradeableLoaderState::Program {
                                programdata_address,
                            }) = account.state()
                            {
```
After
```rust
.unwrap_or_default();

                        if bpf_loader_upgradeable::check_id(&account.owner) {
                            if demote_program_write_locks
                                && message.is_writable(i, demote_program_write_locks)
                                && !is_upgradeable_loader_present
                            {
                                error_counters.invalid_writable_account += 1;
```

## Snippet 3

Context: `runtime/src/bank.rs:2814` (changes a sensitive control or state-update path)

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

Context: `runtime/src/accounts.rs:1690` (changes signature or replay validation logic)

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

Broaden transaction-load-time validation for protected program-state accounts and reject invalid writable locks before execution.

## How It Was Fixed

The fix changed `runtime/src/accounts.rs` so the upgradeable-loader-owned account check no longer depends on `account.executable`. It adds a rejection path when `demote_program_write_locks` is active, the account is still writable in the message, and the upgradeable loader is absent. The patch also adds an `invalid_writable_account` counter in bank processing and regression coverage for writable executable account loading.

# Why It Matters

1. Protects executable and upgradeable-loader-owned program state from ordinary writable transaction locks.

2. Keeps program-state mutation tied to the loader-mediated upgrade path.

3. Rejects invalid account sets before downstream execution.

4. Improves observability with a dedicated invalid writable account counter.

# Evidence Notes

Grounded evidence comes from `runtime/src/accounts.rs`, where validation changes from `account.executable && bpf_loader_upgradeable::check_id(&account.owner)` to `bpf_loader_upgradeable::check_id(&account.owner)` and rejects writable accounts when the upgradeable loader is absent. `runtime/src/bank.rs` adds the `bank-process_transactions-error-invalid_writable_account` metric. The commit message states the intent to return errors for writable executable or ProgramData accounts. The evidence does not establish an independent SDK or storage-proto vulnerability, a sysvar-specific vulnerability, successful exploitation, privilege escalation, or confirmed unauthorized code execution. Protocol security invariant: During transaction account loading, executable program accounts and upgradeable-loader-owned program data/state should not be accepted as ordinary writable accounts unless the upgradeable loader is present to mediate the valid upgrade path. Verification notes: The patch does not prove an end-to-end exploit or privilege escalation by itself. The evidence does not show whether all rejected transactions were previously executable to successful state mutation. The storage-proto and SDK changes are not enough here to infer an independent serialization vulnerability. The removed instructions sysvar writable check appears to be part of changed validation placement, not proof of a separate sysvar-specific bug. Downgraded confidence from high to medium because exploitability is not shown. Downgraded verdict from confirmed to likely because the patch clearly enforces a security-relevant invariant but the provided evidence does not prove impact. Classified as security hardening rather than confirmed security fix. Kept in security corpus because the change affects runtime validation of writable access to protected program state. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-writable-account-validation`
Final tags: `infrastructure, transaction-processing, writable-account-validation, program-state, state-integrity, bpf-loader-upgradeable`

The supplied patch evidence supports a security-hardening classification: transaction account loading now rejects writable locks on upgradeable-loader-owned accounts when the upgradeable loader is not present, tightening a runtime invariant around protected executable or ProgramData state. The evidence does not prove an exploit, unauthorized mutation, or concrete state corruption, so it should not be treated as a confirmed security fix and the original state-corruption/signature framing is too strong.

## Security Evidence

1. Commit message explicitly says transactions with writable executable or ProgramData accounts should return an error.
2. runtime/src/accounts.rs broadens validation from executable upgradeable-loader-owned accounts to all upgradeable-loader-owned accounts.
3. The new guard checks demote_program_write_locks, message writability, and absence of the upgradeable loader before incrementing invalid_writable_account and rejecting.
4. runtime/src/bank.rs adds observability for invalid_writable_account failures.
5. A regression test is added for executable accounts with writable locks.

## Missing Evidence

1. No evidence of a demonstrated exploit or attacker-controlled successful write.
2. No proof that prior accepted transactions could mutate protected program state in practice.
3. No evidence tying the change to signature verification, replay protection, or cryptographic validation.
4. No independent evidence that SDK or storage-proto changes fixed a serialization vulnerability.

## Claim Boundaries

1. Keep as security hardening, not a confirmed vulnerability fix.
2. Claim only transaction-load-time rejection of invalid writable locks on protected program-state accounts.
3. Do not claim confirmed state corruption, privilege escalation, unauthorized code execution, or signature bypass.
4. Do not infer separate vulnerabilities from metrics, tests, SDK, or storage-proto file touches alone.
