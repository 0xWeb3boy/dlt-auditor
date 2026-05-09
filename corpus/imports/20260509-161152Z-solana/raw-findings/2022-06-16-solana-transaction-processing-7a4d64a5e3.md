---
case_id: case_20220616_7a4d64a5e3
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2022-06-16
source_refs:
  - git:7a4d64a5e3c5f4920f8b0d97521cfa38bdc2e46e
  - "ledger/src/blockstore_processor.rs:1551"
  - "ledger/src/blockstore_processor.rs:222"
  - "ledger/src/blockstore_processor.rs:1632"
  - "ledger/src/blockstore_processor.rs:3972"
bug_class: missing-resource-limit-enforcement
impact_type:
  - resource-limit-bypass
  - consensus-integrity
tags:
  - blockchain-core
  - transaction-processing
  - replay-stage
  - accounts-data-size
  - resource-limit
  - consensus-critical
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Solana ledger replay by adding an unconditional account-data-size validation step in `execute_batch` and extending the helper to run a bank-level per-block accounts data check before preserving the existing total-size execution-result scan.

## Observed Patch Facts

1. In `ledger/src/blockstore_processor.rs`, the patch replaces `/// Check the transaction execution results to see if any instruction errored by exce...` with `/// Check to see if the transactions exceeded the accounts data size limits`.

2. In `ledger/src/blockstore_processor.rs`, the patch replaces `if bank` with `check_accounts_data_size(bank, &execution_results)?;`.

3. In `ledger/src/blockstore_processor.rs`, the patch replaces `system_instruction::SystemError,` with `instruction::InstructionError,`.

4. In `ledger/src/blockstore_processor.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `ledger/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `ledger/src/leader_schedule_cache.rs`, `ledger/src/shred.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/leader_schedule_cache.rs`, `ledger/src/shred.rs`. The strongest project-level identifiers around this patch are `bank`, `execution_results`, `check_accounts_data_size`, and `feature_set::cap_accounts_data_len::id`.

## Before/After Behavior

Before the patch, `execute_batch` only invoked the account-data-size helper under `feature_set::cap_accounts_data_len::id()`, and that helper only inspected transaction execution results for `InstructionError::MaxAccountsDataSizeExceeded`. After the patch, `execute_batch` always calls `check_accounts_data_size(bank, &execution_results)?`; the helper now accepts `&Bank`, first calls `check_accounts_data_block_size(bank)?`, and then calls the retained `check_accounts_data_total_size(bank, execution_results)`.

# Root Cause

The replay batch execution path lacked a bank-level per-block accounts data size validation step after transaction execution. The existing check was tied to feature-gated execution-result errors for the total accounts data limit, so the per-block limit was not evidenced as enforced in this path before the change.

## Walkthrough

1. ReplayStage executes a transaction batch and obtains `TransactionResults`, including `execution_results`.

2. Before the patch, account-data-size validation in `execute_batch` was guarded by `feature_set::cap_accounts_data_len::id()` and only passed execution results to the helper.

3. The old helper was documented as checking whether any instruction errored by exceeding the max accounts data size limit for all slots.

4. The patch changes `execute_batch` to call `check_accounts_data_size(bank, &execution_results)?` unconditionally after transaction results are unpacked.

5. The helper now receives `Bank` and invokes `check_accounts_data_block_size(bank)?` before checking execution results.

6. The retained total-size behavior remains in `check_accounts_data_total_size`, which still scans for `InstructionError::MaxAccountsDataSizeExceeded`.

7. The added regression test uses `MAX_ACCOUNT_DATA_BLOCK_LEN` and `MAX_PERMITTED_DATA_LENGTH`, supporting that the new behavior targets per-block accounts data limit enforcement.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| ledger/src/blockstore_processor.rs | 222 | ReplayStage batch execution now unconditionally validates account data size after transaction execution results are available. |
| ledger/src/blockstore_processor.rs | 1551 | `check_accounts_data_size` now receives `Bank` and invokes the per-block account data size check before total-size result inspection. |
| ledger/src/blockstore_processor.rs | 1581 | Existing total accounts data limit check remains feature-gated and scans transaction execution results for `MaxAccountsDataSizeExceeded`. |
| ledger/src/blockstore_processor.rs | 3972 | Regression test constructs accounts sized around `MAX_ACCOUNT_DATA_BLOCK_LEN` to verify per-block limit enforcement. |

## Code Snippets

## Snippet 1

Context: `ledger/src/blockstore_processor.rs:1551` (changes a sensitive control or state-update path)

Before
```rust
}

/// Check the transaction execution results to see if any instruction errored by exceeding the max
/// accounts data size limit for all slots.  If yes, the whole block needs to be failed.
fn check_accounts_data_size<'a>(
    execution_results: impl IntoIterator<Item = &'a TransactionExecutionResult>,
) -> Result<()> {
    if let Some(result) = execution_results
```
After
```rust
}

/// Check to see if the transactions exceeded the accounts data size limits
fn check_accounts_data_size<'a>(
    bank: &Bank,
    execution_results: impl IntoIterator<Item = &'a TransactionExecutionResult>,
) -> Result<()> {
    check_accounts_data_block_size(bank)?;
```

## Snippet 2

Context: `ledger/src/blockstore_processor.rs:222` (changes a sensitive control or state-update path)

Before
```rust
} = tx_results;

    if bank
        .feature_set
        .is_active(&feature_set::cap_accounts_data_len::id())
    {
        check_accounts_data_size(&execution_results)?;
    }
```
After
```rust
} = tx_results;

    check_accounts_data_size(bank, &execution_results)?;

    if let Some(transaction_status_sender) = transaction_status_sender {
```

## Snippet 3

Context: `ledger/src/blockstore_processor.rs:1632` (changes a sensitive control or state-update path)

Before
```rust
epoch_schedule::EpochSchedule,
            hash::Hash,
            pubkey::Pubkey,
            signature::{Keypair, Signer},
            system_instruction::SystemError,
            system_transaction,
            transaction::{Transaction, TransactionError},
```
After
```rust
epoch_schedule::EpochSchedule,
            hash::Hash,
            instruction::InstructionError,
            native_token::LAMPORTS_PER_SOL,
            pubkey::Pubkey,
            signature::{Keypair, Signer},
            system_instruction::{SystemError, MAX_PERMITTED_DATA_LENGTH},
            system_transaction,
```

## Snippet 4

Context: `ledger/src/blockstore_processor.rs:3972` (changes signature or replay validation logic)

Before
```rust
assert!(!batch2.needs_unlock());
    }
}
```
After
```rust
assert!(!batch2.needs_unlock());
    }

    #[test]
    fn test_check_accounts_data_block_size() {
        const ACCOUNT_SIZE: u64 = MAX_PERMITTED_DATA_LENGTH;
        const NUM_ACCOUNTS: u64 = MAX_ACCOUNT_DATA_BLOCK_LEN / ACCOUNT_SIZE;
```

# Fix Pattern

Add the missing per-block resource-limit validation to the replay post-execution path while preserving the existing total accounts data size check.

## How It Was Fixed

`ledger/src/blockstore_processor.rs` was updated so `execute_batch` calls `check_accounts_data_size(bank, &execution_results)?` without the previous outer feature gate. `check_accounts_data_size` was refactored to accept `&Bank`, call `check_accounts_data_block_size(bank)?`, and then delegate to `check_accounts_data_total_size`. A regression test was added for per-block accounts data sizing around `MAX_ACCOUNT_DATA_BLOCK_LEN`.

# Why It Matters

1. Replay is a consensus-sensitive validation path.

2. The patch adds enforcement for a block-level resource/accounting limit.

3. Oversized account data growth could otherwise be processed farther than intended in ReplayStage.

4. The evidence supports security hardening, but not a proven exploit or observed network impact.

# Evidence Notes

Grounded evidence comes from `ledger/src/blockstore_processor.rs`: `execute_batch` changes from a feature-gated `check_accounts_data_size(&execution_results)?` call to an unconditional `check_accounts_data_size(bank, &execution_results)?`; `check_accounts_data_size` gains a `Bank` parameter and calls `check_accounts_data_block_size(bank)?`; `check_accounts_data_total_size` retains the prior scan for `InstructionError::MaxAccountsDataSizeExceeded`; and `test_check_accounts_data_block_size` is added. The evidence does not establish remote exploitability, cryptographic failure, permanent state corruption, actual consensus divergence, or the full internals of `check_accounts_data_block_size`. Protocol security invariant: ReplayStage block processing should enforce the accounts data size limits applicable to a block after transaction execution, including the per-block accounts data limit, before continuing with downstream replay/status handling. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show a cryptographic failure. The patch does not prove permanent state corruption occurred on mainnet. The patch does not establish whether the missing check caused consensus divergence in practice. The provided evidence does not detail the exact implementation of `check_accounts_data_block_size` beyond its invocation and tested purpose. Downgraded confidence from high to medium because the vulnerability impact is inferred from replay/resource-limit context rather than directly demonstrated. Kept `security_verdict` as likely because the patch adds runtime enforcement of a protocol resource limit in ReplayStage. Classified as security-hardening rather than confirmed security-fix because no concrete exploit or incident evidence is provided. Rejected unsupported claims about state corruption, cryptographic failure, or proven consensus divergence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-resource-limit-enforcement`
Final impact type: `resource-limit-bypass, consensus-integrity`
Final tags: `blockchain-core, transaction-processing, replay-stage, accounts-data-size, resource-limit, consensus-critical`

The supplied patch evidence supports retaining this as security hardening: ReplayStage batch execution now unconditionally runs account data size validation, and the helper now invokes a bank-level per-block accounts data size check before preserving the existing total-size check. Because this is a consensus-sensitive replay path and the change enforces a protocol resource limit, it is security-relevant. However, the evidence does not prove an exploitable vulnerability, actual consensus divergence, cryptographic failure, or concrete state corruption, so the original state-corruption/signature framing is too strong.

## Security Evidence

1. execute_batch changed from a feature-gated account-data-size check to an unconditional check_accounts_data_size(bank, &execution_results) call.
2. check_accounts_data_size now accepts Bank and calls check_accounts_data_block_size(bank) before the existing total-size execution-result scan.
3. The added test targets MAX_ACCOUNT_DATA_BLOCK_LEN and MAX_PERMITTED_DATA_LENGTH, supporting that the patch enforces a per-block account data resource limit.
4. The changed code is in ledger ReplayStage/block processing, a consensus-sensitive validation path.

## Missing Evidence

1. No evidence of a concrete exploit or incident.
2. No evidence that the missing check caused actual consensus divergence.
3. No internals of check_accounts_data_block_size are provided beyond its invocation and test context.
4. No evidence of cryptographic or signature-validation impact.
5. No proof of permanent state corruption.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed security-fix.
2. Do not claim signature bypass, cryptographic failure, or proven state corruption.
3. Do not claim demonstrated remote exploitability from this patch alone.
4. Supported claim is limited to stronger enforcement of per-block accounts data size limits during replay batch processing.
