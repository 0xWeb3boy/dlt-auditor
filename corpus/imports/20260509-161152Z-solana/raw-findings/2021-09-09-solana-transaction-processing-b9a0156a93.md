---
case_id: case_20210909_b9a0156a93
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2021-09-09
source_refs:
  - git:b9a0156a9359b44984e1f78e796f59bfcdca0d7d
  - "runtime/src/accounts.rs:229"
  - "runtime/src/accounts.rs:248"
  - "runtime/src/bank.rs:2953"
  - "runtime/src/accounts.rs:1755"
bug_class: improper-writable-account-validation
impact_type:
  - state-integrity
  - access-control
tags:
  - infrastructure
  - transaction-processing
  - writable-account-validation
  - upgradeable-loader
  - state-integrity
  - access-control
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens Solana runtime account loading so writable executable accounts and upgradeable-loader-owned ProgramData/state accounts are rejected when the upgradeable loader is not present. The evidence supports a transaction validation and account access-control fix, but does not establish arbitrary code execution, unauthorized upgrade, or consensus divergence.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch removes `if message.is_writable(i, demote_program_write_locks) {`.

2. In `runtime/src/accounts.rs`, the patch replaces `if account.executable() && bpf_loader_upgradeable::check_id(account.owner())` with `if bpf_loader_upgradeable::check_id(account.owner()) {`.

3. In `runtime/src/bank.rs`, the patch adds `if 0 != error_counters.invalid_writable_account {`.

4. In `runtime/src/accounts.rs`, the patch replaces `fn test_accounts_account_not_found() {` with `fn test_load_accounts_executable_with_write_lock() {`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/accounts_db.rs`, `runtime/src/vote_account.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/message_processor.rs`, `runtime/src/accounts_db.rs`. The strongest project-level identifiers around this patch are `account`, `bpf_loader_upgradeable::check_id`, `demote_program_write_locks`, and `error_counters`.

## Before/After Behavior

Before the patch, the shown upgradeable-loader validation in `runtime/src/accounts.rs` was gated on `account.executable() && bpf_loader_upgradeable::check_id(account.owner())`, so the extracted logic applied only to executable accounts owned by the upgradeable loader. After the patch, the check is broadened to accounts whose owner is the upgradeable loader, and the code records `invalid_writable_account` when `demote_program_write_locks` is active, the message marks the account writable, and the upgradeable loader is absent. The patch also removes a local writable check from the instructions sysvar construction path and adds bank-level reporting for the new invalid writable account counter.

# Root Cause

The prior validation was scoped too narrowly to executable upgradeable-loader-owned accounts. Based on the commit message and diff, some upgradeable-loader-owned program state such as ProgramData accounts could be treated as writable in transaction loading when the upgradeable loader was not present.

## Walkthrough

1. `Accounts::load_transaction` computes feature-gated write-lock behavior and whether the upgradeable loader is present in the transaction message.

2. For each non-loader account key, the runtime loads the account and applies writable-account handling.

3. Before the fix, the relevant upgradeable-loader validation shown in the diff only ran for accounts that were both executable and owned by the upgradeable loader.

4. That left non-executable upgradeable-loader-owned state outside the shown validation condition.

5. After the fix, the validation is based on upgradeable-loader ownership rather than executable status alone.

6. When an upgradeable-loader-owned account is writable while program write-lock demotion is active and the loader is absent, the runtime records an invalid writable account condition and, per commit intent, rejects the transaction.

7. `runtime/src/bank.rs` now reports the `invalid_writable_account` counter.

8. Regression coverage was added for loading an executable account with a write lock.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts.rs | 195 | Loads transaction accounts, computes feature-gated demotion behavior, and decides whether each message account can be loaded for execution. |
| runtime/src/accounts.rs | 229 | Adjusts special handling for the instructions sysvar writable check during account construction. |
| runtime/src/accounts.rs | 248 | Enforces writable-account rejection for upgradeable-loader-owned accounts when the upgradeable loader is absent. |
| runtime/src/bank.rs | 2953 | Records invalid_writable_account errors from transaction processing. |
| runtime/src/accounts.rs | 1755 | Adds regression coverage for loading an executable account with a write lock. |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts.rs:229` (changes a sensitive control or state-update path)

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

Context: `runtime/src/accounts.rs:248` (changes an authorization or privilege gate)

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

Context: `runtime/src/bank.rs:2953` (changes a sensitive control or state-update path)

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

Context: `runtime/src/accounts.rs:1755` (changes signature or replay validation logic)

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

Enforce the writable-account invariant during transaction account loading, using ownership and transaction context rather than executable status alone, and add explicit error accounting and regression coverage.

## How It Was Fixed

The fix broadened the check in `runtime/src/accounts.rs` from executable upgradeable-loader-owned accounts to all accounts owned by the upgradeable loader, then treats writable access as invalid when the upgradeable loader is absent under the relevant feature gate. It also added `invalid_writable_account` reporting in `runtime/src/bank.rs` and tests for writable executable account loading.

# Why It Matters

1. Protects executable program accounts from ordinary writable transaction locks.

2. Extends validation to upgradeable-loader-owned ProgramData/state accounts.

3. Keeps loader-owned program state behind the loader-managed path.

4. Improves observability for invalid writable-account rejections.

5. Does not prove arbitrary code execution or unauthorized program upgrade.

# Evidence Notes

Grounded evidence comes from `runtime/src/accounts.rs` around account loading and the upgradeable-loader ownership check, `runtime/src/bank.rs` reporting of `invalid_writable_account`, the new regression test, and the commit message explicitly stating that writable executable or ProgramData accounts should return an error. The snippets do not include the full rejection return statement, so claims about the exact control-flow endpoint rely partly on commit context and mapper interpretation. Protocol security invariant: Transactions should not obtain writable access to executable program accounts or upgradeable-loader-owned program state unless the upgradeable loader is present in the transaction path that is allowed to manage those accounts. Verification notes: The patch does not prove arbitrary code execution. The patch does not prove that a writable lock alone allowed a successful unauthorized program upgrade. The patch does not show consensus divergence mechanics beyond transaction validation behavior. The storage-proto changes are not enough on their own to classify this as a serialization vulnerability. The evidence supports account access-control/state-integrity impact, not cryptographic breakage. Code evidence supports a runtime validation/access-control fix. Security impact is likely because the protected objects are executable program accounts and loader-owned program state. No evidence proves arbitrary code execution. No evidence proves a successful unauthorized program upgrade. Storage-proto changes should be treated as supporting compatibility work, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-writable-account-validation`
Final impact type: `state-integrity, access-control`
Final tags: `infrastructure, transaction-processing, writable-account-validation, upgradeable-loader, state-integrity, access-control`

The supplied evidence supports retaining this as security hardening, not a proven concrete security exploit fix. The commit and patch tighten transaction account-loading rules around writable executable accounts and upgradeable-loader-owned accounts, including ProgramData/state accounts, and add invalid writable account accounting and regression coverage. However, the snippets do not prove a successful exploit path such as arbitrary code execution, unauthorized upgrade, or consensus divergence, so the original security-fix/state-corruption framing is too strong.

## Security Evidence

1. Commit message explicitly says transactions should error when containing writable executable or ProgramData accounts.
2. Runtime account loading now checks upgradeable-loader ownership rather than only executable upgradeable-loader accounts.
3. The new condition rejects writable upgradeable-loader-owned accounts when program write-lock demotion is active and the upgradeable loader is absent.
4. A new invalid_writable_account counter is added in bank transaction processing.
5. Regression coverage was added for executable accounts with write locks.

## Missing Evidence

1. No full control-flow snippet shows the exact transaction rejection return path after invalid_writable_account is incremented.
2. No evidence demonstrates arbitrary code execution or unauthorized program upgrade.
3. No evidence demonstrates consensus divergence or a concrete chain-state corruption scenario.
4. No exploit, advisory, or vulnerability impact statement is provided beyond the commit and patch behavior.

## Claim Boundaries

1. Classify as security-hardening because it enforces a security-sensitive account writability invariant.
2. Do not claim arbitrary code execution, unauthorized upgrade, or signature bypass.
3. Do not treat storage-proto changes as evidence of a serialization vulnerability.
4. State-integrity and access-control impact are plausible, but concrete exploitability is not proven from the supplied evidence.
