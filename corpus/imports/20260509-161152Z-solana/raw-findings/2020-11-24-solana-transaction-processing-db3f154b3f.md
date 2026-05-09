---
case_id: case_20201124_db3f154b3f
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2020-11-24
source_refs:
  - git:db3f154b3fa452414ee734f8e32c69f877b82d9e
  - "runtime/src/accounts.rs:863"
  - "core/src/transaction_status_service.rs:73"
  - "runtime/src/accounts.rs:320"
  - "runtime/src/accounts.rs:832"
bug_class: durable-nonce-failed-transaction-state-persistence
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - durable-nonce
  - failed-transaction-atomicity
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a likely Solana runtime state-integrity fix in durable nonce transaction handling. The strongest evidence is the change in `Accounts::collect_accounts_to_store` from storing any writable account to storing writable accounts only on successful execution, or on failed durable-nonce execution when the account is the nonce account or fee payer. Related fee-calculator changes appear to support consistent durable-nonce metadata handling rather than establish a separate vulnerability.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch replaces `if message.is_writable(i) {` with `let is_fee_payer = i == 0;`.

2. In `core/src/transaction_status_service.rs`, the patch replaces `let fee_calculator = match hash_age_kind {` with `let fee_calculator = hash_age_kind`.

3. In `runtime/src/accounts.rs`, the patch replaces `let fee_calculator = match hash_age_kind.as_ref() {` with `let fee_calculator = hash_age_kind`.

4. In `runtime/src/accounts.rs`, the patch replaces `(Ok(_), Some(HashAgeKind::DurableNonce(pubkey, acc))) => Some((pubkey, acc)),` with `(Ok(_), Some(HashAgeKind::DurableNonceFull(pubkey, acc, maybe_fee_account))) => {`.

## Project Context

The changed code sits primarily in `runtime/src`, `core/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/bank.rs`, `core/src/pubkey_references.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `core/src/banking_stage.rs`. The strongest project-level identifiers around this patch are `HashAgeKind::DurableNonce`, `Some`, `hash_age_kind`, and `pubkey`.

## Before/After Behavior

Before the patch, the account collection path used `message.is_writable(i)` as the store eligibility guard, including paths where durable nonce metadata was present for an `InstructionError`. After the patch, the guard requires either successful transaction execution or a durable nonce failure involving the nonce account or fee payer. The patch also changes durable nonce metadata from the older `DurableNonce(pubkey, acc)` handling to `DurableNonceFull(pubkey, acc, maybe_fee_account)` in the collection path, and centralizes fee-calculator lookup through `HashAgeKind::fee_calculator()` with fallback to the recent blockhash fee calculator.

# Root Cause

The grounded root cause is an overly broad account persistence condition in the durable nonce failure path. The prior writable-account guard did not explicitly distinguish normal successful execution from failed durable-nonce execution, so the collection path could consider all writable accounts for storage instead of limiting the failure exception to nonce and fee-payer state.

## Walkthrough

1. A transaction enters account loading, where fee calculation may come from durable nonce hash-age metadata or the recent blockhash queue.

2. For durable nonce transactions, the patched collection path recognizes `HashAgeKind::DurableNonceFull(pubkey, acc, maybe_fee_account)` for both successful execution and `InstructionError` failure.

3. `Accounts::collect_accounts_to_store` computes whether the current account is the nonce account and whether it is the fee payer.

4. Before the patch, a writable account could pass the store guard without the new success-or-durable-nonce-failure restriction.

5. After the patch, a writable account is eligible for storage only if execution succeeded, or if durable nonce metadata exists and the account is the nonce account or fee payer.

6. The transaction status service and account loading paths now retrieve durable-nonce fee calculators through `HashAgeKind::fee_calculator()`, keeping fee lookup aligned with the changed metadata shape.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts.rs | 298 | loads transaction accounts and chooses the fee calculator for recent-blockhash or durable-nonce transactions |
| runtime/src/accounts.rs | 812 | collects accounts to persist after transaction processing, including special failed durable-nonce handling |
| runtime/src/accounts.rs | 863 | guards which writable accounts are stored on success versus failed durable-nonce execution |
| core/src/transaction_status_service.rs | 44 | records transaction status using the fee calculator associated with normal or durable-nonce hash age |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts.rs:863` (changes a sensitive control or state-update path)

Before
```rust
fix_recent_blockhashes_sysvar_delay,
                );
                if message.is_writable(i) {
                    if account.rent_epoch == 0 {
                        acc.2 += rent_collector.collect_from_created_account(
```
After
```rust
fix_recent_blockhashes_sysvar_delay,
                );
                let is_fee_payer = i == 0;
                if message.is_writable(i)
                    && (res.is_ok()
                        || (maybe_nonce.is_some() && (is_nonce_account || is_fee_payer)))
                {
                    if res.is_err() {
```

## Snippet 2

Context: `core/src/transaction_status_service.rs:73` (changes signature or replay validation logic)

Before
```rust
) {
            if Bank::can_commit(&status) && !transaction.signatures.is_empty() {
                let fee_calculator = match hash_age_kind {
                    Some(HashAgeKind::DurableNonce(_, account)) => {
                        nonce::utils::fee_calculator_of(&account)
                    }
                    _ => bank.get_fee_calculator(&transaction.message().recent_blockhash),
                }
```
After
```rust
) {
            if Bank::can_commit(&status) && !transaction.signatures.is_empty() {
                let fee_calculator = hash_age_kind
                    .and_then(|hash_age_kind| hash_age_kind.fee_calculator())
                    .unwrap_or_else(|| {
                        bank.get_fee_calculator(&transaction.message().recent_blockhash)
                    })
                    .expect("FeeCalculator must exist");
```

## Snippet 3

Context: `runtime/src/accounts.rs:320` (changes signature or replay validation logic)

Before
```rust
.map(|etx| match etx {
                ((_, tx), (Ok(()), hash_age_kind)) => {
                    let fee_calculator = match hash_age_kind.as_ref() {
                        Some(HashAgeKind::DurableNonce(_, account)) => {
                            nonce::utils::fee_calculator_of(account)
                        }
                        _ => hash_queue
                            .get_fee_calculator(&tx.message().recent_blockhash)
```
After
```rust
.map(|etx| match etx {
                ((_, tx), (Ok(()), hash_age_kind)) => {
                    let fee_calculator = hash_age_kind
                        .as_ref()
                        .and_then(|hash_age_kind| hash_age_kind.fee_calculator())
                        .unwrap_or_else(|| {
                            hash_queue
                                .get_fee_calculator(&tx.message().recent_blockhash)
```

## Snippet 4

Context: `runtime/src/accounts.rs:832` (changes the branch that decides whether execution stops or continues)

Before
```rust
let (res, hash_age_kind) = &res[i];
            let maybe_nonce = match (res, hash_age_kind) {
                (Ok(_), Some(HashAgeKind::DurableNonce(pubkey, acc))) => Some((pubkey, acc)),
                (
                    Err(TransactionError::InstructionError(_, _)),
                    Some(HashAgeKind::DurableNonce(pubkey, acc)),
                ) => Some((pubkey, acc)),
                (Ok(_), _hash_age_kind) => None,
```
After
```rust
let (res, hash_age_kind) = &res[i];
            let maybe_nonce = match (res, hash_age_kind) {
                (Ok(_), Some(HashAgeKind::DurableNonceFull(pubkey, acc, maybe_fee_account))) => {
                    Some((pubkey, acc, maybe_fee_account))
                }
                (
                    Err(TransactionError::InstructionError(_, _)),
                    Some(HashAgeKind::DurableNonceFull(pubkey, acc, maybe_fee_account)),
```

# Fix Pattern

Narrow failed-transaction persistence exceptions by making the durable nonce special case explicit: keep the ordinary success path, but on durable nonce instruction failure only allow nonce and fee-payer state to be stored.

## How It Was Fixed

The patch added explicit `is_fee_payer` handling and replaced the broad writable-account condition with `message.is_writable(i) && (res.is_ok() || (maybe_nonce.is_some() && (is_nonce_account || is_fee_payer)))`. It also updated durable nonce matching to use `DurableNonceFull` metadata in the collection path and replaced direct durable nonce fee-calculator matching with `HashAgeKind::fee_calculator()` fallback logic.

# Why It Matters

1. Preserves failed-transaction atomicity for durable nonce transactions.

2. Keeps nonce advancement and fee payment as the explicit failure-path exception.

3. Reduces risk that unrelated writable accounts are stored after failed durable-nonce execution.

4. Aligns durable-nonce fee lookup across runtime and transaction status handling.

# Evidence Notes

Supported by the supplied hunks in `runtime/src/accounts.rs` around account loading and `collect_accounts_to_store`, plus `core/src/transaction_status_service.rs` fee-calculator handling. The evidence does not support the earlier panic/conversion denial-of-service theory. It also does not include tests, advisory text, the full `HashAgeKind` definition, complete nonce preparation logic, or proof of remote exploitability or severity. Protocol security invariant: Durable nonce transaction handling should preserve failed-transaction atomicity while still committing the nonce and fee-payer state required by nonce consumption and fee charging on instruction failure. Verification notes: The patch does not by itself prove remote exploitability. The evidence does not show the full definition of `HashAgeKind` or all nonce preparation logic. The evidence does not prove arbitrary account mutation beyond the failed durable-nonce commit path. The transaction status fee-calculator cleanup may be supporting consistency rather than independently security-relevant. No tests or advisory text are provided to confirm severity. Verified only against the provided excerpts and draft text. No external files, commands, tests, or advisory context were used. Claims about arbitrary account mutation, crash behavior, or exploitability were removed or softened. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `durable-nonce-failed-transaction-state-persistence`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, durable-nonce, failed-transaction-atomicity, state-integrity`

The supplied patch evidence supports a conservative security-hardening classification, not a fully confirmed security-fix. The strongest hunk narrows account storage after failed durable-nonce transactions so only successful transactions, or the nonce account and fee payer in the durable-nonce failure case, can be persisted. In a blockchain runtime, this is security-sensitive state handling because failed transaction atomicity and nonce/fee exceptions affect ledger state correctness, but the provided evidence does not prove exploitability, consensus impact, or a concrete vulnerability report.

## Security Evidence

1. Account persistence changed from all writable accounts to writable accounts gated by success or durable-nonce failure involving the nonce account or fee payer.
2. The changed path is in runtime account collection after transaction processing, a state-update boundary.
3. Durable nonce metadata was expanded to DurableNonceFull with fee-account awareness, supporting more precise failure-path handling.
4. Fee-calculator lookup was centralized through HashAgeKind::fee_calculator(), aligning nonce metadata handling across runtime and transaction status code.

## Missing Evidence

1. No advisory, issue discussion, test case, or exploit scenario is provided.
2. The evidence does not show that arbitrary attacker-controlled account mutation was possible.
3. The evidence does not prove consensus failure, fund loss, replay, or denial-of-service impact.
4. The full HashAgeKind definition and nonce preparation logic are not included.

## Claim Boundaries

1. Keep the claim to durable-nonce failed-transaction state persistence hardening.
2. Do not claim a confirmed exploitable vulnerability from the supplied patch alone.
3. Do not classify this primarily as liveness; the evidenced concern is state integrity and failed-transaction atomicity.
4. Treat transaction-status fee-calculator changes as supporting consistency unless stronger evidence links them to a separate security bug.
