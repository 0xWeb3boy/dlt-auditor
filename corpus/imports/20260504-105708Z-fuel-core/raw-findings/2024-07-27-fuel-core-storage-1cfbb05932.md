---
case_id: case_20240727_1cfbb05932
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
confidence: high
source_quality: high
date: 2024-07-27
source_refs:
  - git:1cfbb05932e54a05db2bd0f4c79d5f1b6e45b0f1
  - "crates/services/executor/src/executor.rs:1366"
  - "crates/fuel-core/src/executor.rs:2532"
  - "crates/fuel-core/src/executor.rs:55"
bug_class: reverted-transaction-withdrawal-message-inclusion
impact_type:
  - duplicate-withdrawal
  - asset-reuse
tags:
  - blockchain-core
  - executor
  - withdrawal-message
  - reverted-transaction
  - consensus-state
  - asset-duplication
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes executor handling of withdrawal/message receipt IDs for reverted transactions. Before the change, `update_execution_data` added every receipt `message_id()` to `execution_data.message_ids` regardless of whether the transaction reverted. The patch gates that aggregation with `if !reverted`, matching the commit message's stated issue that failed transactions could otherwise be used to create many withdrawals with the same assets.

## Observed Patch Facts

1. In `crates/services/executor/src/executor.rs`, the patch replaces `let status = if reverted {` with `if !reverted {`.

2. In `crates/fuel-core/src/executor.rs`, the patch replaces `fn get_block_height_returns_current_executing_block() {` with `fn withdrawal_message_included_in_header_for_successfully_executed_transaction() {`.

3. In `crates/fuel-core/src/executor.rs`, the patch replaces `fuel_merkle::sparse,` with `fuel_merkle::{`.

## Project Context

The changed code sits primarily in `crates/services/executor/src`, `crates/services/executor`, `crates/fuel-core/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/services/executor/src/refs.rs`, `crates/services/executor/src/ports.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/fuel-core/src/p2p_test_helpers.rs`, `crates/fuel-core/src/database/state.rs`. The strongest project-level identifiers around this patch are `ExecutorError::GasOverflow`, `TransactionBuilder::script`, `fuel_crypto::SecretKey`, and `fuel_merkle::sparse`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/tx_pool_gas_price_tests.rs`, `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the patch, `update_execution_data` updated fee and gas accounting, then unconditionally extended `execution_data.message_ids` from receipt message IDs before deriving failed or successful transaction status from `reverted`. After the patch, fee and gas accounting remain unchanged, but receipt-derived message IDs are added only when `reverted` is false. Reverted transactions can still be represented as failed executions, but their withdrawal/message receipt IDs are no longer promoted into execution data.

# Root Cause

The executor treated receipt observation as sufficient for withdrawal/message inclusion and did not couple receipt-derived message ID aggregation to transaction success. As a result, receipts from reverted execution could still affect `execution_data.message_ids`.

## Walkthrough

1. A transaction executes and produces receipts, some of which may expose a message ID through `receipt.message_id()`.

2. `update_execution_data` receives those receipts together with the transaction's `reverted` flag.

3. Previously, the executor extended `execution_data.message_ids` from all receipt message IDs without checking `reverted`.

4. That meant a failed or reverted withdrawal-message transaction could still contribute a withdrawal/message ID to execution data.

5. The commit message states this allowed the same assets to be used to create many withdrawals with failed transactions.

6. The patched code checks `if !reverted` before extending `execution_data.message_ids`, excluding receipt message IDs from reverted transactions.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/services/executor/src/executor.rs | 1349 | Executor update_execution_data aggregates fees, gas, and receipt-derived message IDs into block execution data; patched to exclude message IDs when the transaction reverted. |
| crates/fuel-core/src/executor.rs | 2532 | Regression test constructs an SMO withdrawal-message transaction and checks message inclusion behavior for successful execution. |
| crates/fuel-core/src/executor.rs | 55 | Test import update for merkle helper used by the new withdrawal-message/header assertion. |

## Code Snippets

## Snippet 1

Context: `crates/services/executor/src/executor.rs:1366` (changes a sensitive control or state-update path)

Before
```rust
.checked_add(used_gas)
            .ok_or(ExecutorError::GasOverflow)?;
        execution_data
            .message_ids
            .extend(receipts.iter().filter_map(|r| r.message_id()));
        let status = if reverted {
            TransactionExecutionResult::Failed {
```
After
```rust
.checked_add(used_gas)
            .ok_or(ExecutorError::GasOverflow)?;

        if !reverted {
            execution_data
                .message_ids
                .extend(receipts.iter().filter_map(|r| r.message_id()));
        }
```

## Snippet 2

Context: `crates/fuel-core/src/executor.rs:2532` (changes signature or replay validation logic)

Before
```rust
}

    #[test]
    fn get_block_height_returns_current_executing_block() {
```
After
```rust
}

    #[test]
    fn withdrawal_message_included_in_header_for_successfully_executed_transaction() {
        // Given
        let amount_from_random_input = 1000;
        let smo_tx = TransactionBuilder::script(
            vec![
```

## Snippet 3

Context: `crates/fuel-core/src/executor.rs:55` (changes a sensitive control or state-update path)

Before
```rust
},
        fuel_crypto::SecretKey,
        fuel_merkle::sparse,
        fuel_tx::{
            consensus_parameters::gas::GasCostsValuesV1,
```
After
```rust
},
        fuel_crypto::SecretKey,
        fuel_merkle::{
            common::empty_sum_sha256,
            sparse,
        },
        fuel_tx::{
            consensus_parameters::gas::GasCostsValuesV1,
```

# Fix Pattern

Gate consensus-relevant receipt side effects on transaction success. Receipt data from a reverted execution should not be promoted into withdrawal/message execution data unless the transaction completed successfully.

## How It Was Fixed

In `crates/services/executor/src/executor.rs`, the existing `execution_data.message_ids.extend(receipts.iter().filter_map(|r| r.message_id()))` call was moved behind an `if !reverted` guard. Regression test support was added in `crates/fuel-core/src/executor.rs` around withdrawal-message inclusion for successful execution, with a merkle helper import added for the test assertion path.

# Why It Matters

1. Prevents reverted transactions from creating committed withdrawal/message entries.

2. Preserves the success requirement for withdrawal-message inclusion.

3. Addresses the commit-stated risk of reusing the same assets across many failed withdrawals.

4. Keeps the finding scoped to executor receipt handling, not storage, panics, or generic node liveness.

# Evidence Notes

The strongest evidence is the executor hunk where unconditional extension of `execution_data.message_ids` from receipt message IDs became conditional on `if !reverted`. The commit message explicitly states withdrawal messages should be included only if the transaction executes successfully and that otherwise the same assets could create many withdrawals with failed transactions. The evidence does not establish a panic, node crash, generic storage vulnerability, arbitrary minting outside this receipt path, or full remote exploit mechanics. Protocol security invariant: Receipt-derived withdrawal/message IDs that affect block execution data must only be included for transactions that execute successfully. A reverted transaction may produce receipts during attempted execution, but those receipt message IDs must not be treated as committed withdrawal messages. Verification notes: The patch does not prove a panic, node crash, or generic liveness failure. The evidence does not show the full bridge or withdrawal redemption path, only executor-side message ID inclusion. The patch does not by itself prove remote exploitability mechanics or required transaction admission conditions. The evidence supports duplicate failed-withdrawal message creation risk, not arbitrary asset minting outside this message-receipt path. No storage subsystem vulnerability is shown by the changed code. Primary code path: `crates/services/executor/src/executor.rs` `update_execution_data`. Relevant test path: `crates/fuel-core/src/executor.rs` withdrawal-message inclusion test. Mapper's storage and panic-oriented baseline claims are unsupported by the provided diff. Security classification is retained because the commit message and code both support a failed-transaction withdrawal duplication risk. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `reverted-transaction-withdrawal-message-inclusion`
Final impact type: `duplicate-withdrawal, asset-reuse`
Final tags: `blockchain-core, executor, withdrawal-message, reverted-transaction, consensus-state, asset-duplication`

The supplied commit message and patch evidence strongly support a security fix: withdrawal/message receipt IDs were previously included in execution data even when a transaction reverted, and the commit explicitly states this allowed the same assets to create many withdrawals with failed transactions. The fix gates message ID inclusion on successful execution. However, the original storage/liveness/p2p/database framing is unsupported by the provided diff and should be narrowed to executor handling of reverted withdrawal-message receipts.

## Security Evidence

1. Commit message states withdrawal messages should only be included after successful execution.
2. Commit message states failed transactions could reuse the same assets to create many withdrawals.
3. Executor code changed from unconditional receipt message ID aggregation to `if !reverted` guarded aggregation.
4. Regression test context focuses on withdrawal message inclusion in block/header execution behavior.

## Missing Evidence

1. No full withdrawal redemption or bridge path is shown.
2. No exploit transaction sequence or remote attack preconditions are provided.
3. No evidence supports a storage, p2p, database, or generic liveness vulnerability.
4. No evidence shows arbitrary minting outside this withdrawal/message receipt path.

## Claim Boundaries

1. Validated only as an executor-side reverted-transaction withdrawal/message inclusion fix.
2. Impact should be described as duplicate withdrawal or asset reuse risk, not generic liveness failure.
3. The evidence supports consensus/state correctness security relevance, but not broader storage or networking claims.
4. Do not claim full exploitability mechanics beyond the commit-stated failed-withdrawal asset reuse condition.
