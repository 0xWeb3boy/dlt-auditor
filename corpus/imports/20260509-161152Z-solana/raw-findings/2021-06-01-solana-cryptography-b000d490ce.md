---
case_id: case_20210601_b000d490ce
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2021-06-01
source_refs:
  - git:b000d490ce3b798bdf32410985cd121b4e768d8b
  - "core/src/banking_stage.rs:1068"
  - "core/src/banking_stage.rs:1046"
  - "core/src/banking_stage.rs:1179"
  - "core/src/cost_tracker.rs:1"
bug_class: resource-exhaustion-mitigation
impact_type:
  - denial-of-service
confidence: medium
tags:
  - blockchain-core
  - validator
  - resource-control
  - transaction-admission
  - cost-model
  - denial-of-service
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch introduces cost-based transaction admission and accounting in Solana's banking stage. It adds CostModel/CostTracker plumbing, filters over-limit transactions into a retryable/unprocessed path, and accounts cost only for processed transactions. The evidence supports resource-management hardening, not a confirmed vulnerability fix, signature-validation fix, or replay fix.

## Observed Patch Facts

1. In `core/src/banking_stage.rs`, the patch replaces `let message_bytes = Self::packet_message(p)?;` with `// Get transaction cost via immutable cost_model; try to add cost to`.

2. In `core/src/banking_stage.rs`, the patch replaces `) -> (Vec<HashedTransaction<'static>>, Vec<usize>) {` with `// Also returned is packet indexes for transaction should be retried due to cost limits.`.

3. In `core/src/banking_stage.rs`, the patch replaces `let mut filter_pending_packets_time = Measure::start("filter_pending_packets_time");` with `// applying cost of processed transactions to shared cost_tracker`.

4. In `core/src/cost_tracker.rs`, the patch adds `//! 'cost_tracker' keeps tracking tranasction cost per chained accounts as well as fo...`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/src/cost_model.rs`, `core/src/transaction_status_service.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/lib.rs`, `core/src/cost_model.rs`. The strongest project-level identifiers around this patch are `cost_tracker`, `cost`, `transaction`, and `cost_model`.

## Before/After Behavior

Before the change, the supplied snippets show packet deserialization, optional secp256k1 precompile verification, message hashing, and return of valid transactions plus packet indexes, without an observed cost-model admission check. After the change, transactions_from_packets receives a CostModel and shared CostTracker, clones the tracker, calculates transaction cost, and rejects/defer transactions when try_add fails. After bank processing, only transactions not returned as unprocessed are charged to the shared CostTracker.

# Root Cause

The grounded issue is the absence, in the provided banking-stage evidence, of admission-time cost tracking tied to estimated transaction cost and shared block/account limits. The evidence does not prove that this absence was exploitable as a denial-of-service vulnerability.

## Walkthrough

1. transactions_from_packets converts packet data into Transaction values.

2. Existing secp256k1 precompile verification remains present when enabled; the patch does not show a signature or replay-validation semantic change.

3. The patched function clones the shared CostTracker for local admission filtering.

4. For each transaction, the banking stage calls cost_model.calculate_cost(&tx).

5. The local tracker attempts cost_tracker.try_add(tx_cost).

6. If the addition would exceed limits, the packet index is recorded as retryable and the transaction is omitted from the valid list for that pass.

7. Remaining transactions proceed to bank processing.

8. After processing, only transactions not returned as unprocessed have their cost applied to the shared CostTracker under a mutex.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/banking_stage.rs | 1046 | transactions_from_packets now receives cost model/tracker, clones shared tracker, and returns retryable packet indexes for cost-limited transactions |
| core/src/banking_stage.rs | 1068 | per-transaction admission check calculates estimated cost and rejects/defer transactions whose addition would exceed local cost limits |
| core/src/banking_stage.rs | 1179 | post-bank-processing accounting applies calculated cost to the shared cost tracker only for transactions not returned as unprocessed |
| core/src/cost_tracker.rs | 1 | new cost-tracking subsystem records per-account and per-block transaction costs and exposes try_add as the limit-enforcement primitive |
| core/src/cost_model.rs | 1 | cost estimation subsystem computes transaction cost from account access and instruction execution characteristics |

## Code Snippets

## Snippet 1

Context: `core/src/banking_stage.rs:1068` (changes bounds, limits, or capacity handling)

Before
```rust
tx.verify_precompiles().ok()?;
                }
                let message_bytes = Self::packet_message(p)?;
                let message_hash = Message::hash_raw_message(message_bytes);
```
After
```rust
tx.verify_precompiles().ok()?;
                }

                // Get transaction cost via immutable cost_model; try to add cost to
                // local copy of cost_tracker, if suceeded, local copy is updated
                // and transaction added to valid list; otherwise, transaction is
                // added to retry list. No locking here.
                let tx_cost = cost_model.calculate_cost(&tx);
```

## Snippet 2

Context: `core/src/banking_stage.rs:1046` (changes the branch that decides whether execution stops or continues)

Before
```rust
// and verifies secp256k1 instructions. A list of valid transactions are returned with their message hashes
    // and packet indexes.
    fn transactions_from_packets(
        msgs: &Packets,
        transaction_indexes: &[usize],
        secp256k1_program_enabled: bool,
    ) -> (Vec<HashedTransaction<'static>>, Vec<usize>) {
        transaction_indexes
```
After
```rust
// and verifies secp256k1 instructions. A list of valid transactions are returned with their message hashes
    // and packet indexes.
    // Also returned is packet indexes for transaction should be retried due to cost limits.
    fn transactions_from_packets(
        msgs: &Packets,
        transaction_indexes: &[usize],
        secp256k1_program_enabled: bool,
        cost_model: &Arc<CostModel>,
```

## Snippet 3

Context: `core/src/banking_stage.rs:1179` (changes the branch that decides whether execution stops or continues)

Before
```rust
);
        process_tx_time.stop();

        let unprocessed_tx_count = unprocessed_tx_indexes.len();

        let mut filter_pending_packets_time = Measure::start("filter_pending_packets_time");
        let filtered_unprocessed_packet_indexes = Self::filter_pending_packets_from_pending_txs(
            bank,
```
After
```rust
);
        process_tx_time.stop();
        let unprocessed_tx_count = unprocessed_tx_indexes.len();

        // applying cost of processed transactions to shared cost_tracker
        transactions.iter().enumerate().for_each(|(index, tx)| {
            if !unprocessed_tx_indexes.iter().any(|&i| i == index) {
                let tx_cost = cost_model.calculate_cost(&tx.transaction());
```

## Snippet 4

Context: `core/src/cost_tracker.rs:1` (changes signature or replay validation logic)

Before
```rust
(no before snippet captured)
```
After
```rust
//! `cost_tracker` keeps tracking tranasction cost per chained accounts as well as for entire block
//! The main entry function is 'try_add', if success, it returns new block cost.
//!
use crate::cost_model::TransactionCost;
use solana_sdk::{clock::Slot, pubkey::Pubkey};
use std::collections::HashMap;

#[derive(Debug, Clone)]
```

# Fix Pattern

Introduce resource-budget admission control before transaction processing, defer over-limit transactions, and update shared budget state only for transactions actually processed.

## How It Was Fixed

The patch adds CostModel and CostTracker to the banking-stage path. CostModel estimates transaction cost from account access and instruction execution characteristics. CostTracker tracks writable-account and block cost through try_add. transactions_from_packets returns an additional retryable packet-index vector, and process_packets_transactions applies cost to the shared tracker only for processed transactions.

# Why It Matters

1. Adds explicit banking-stage resource control.

2. Prevents over-limit transactions from entering the current processing pass.

3. Keeps shared cost accounting aligned with processed transactions.

4. Does not demonstrate forged signatures, replay acceptance, or a concrete denial-of-service exploit.

# Evidence Notes

Primary evidence is in core/src/banking_stage.rs around lines 1046 and 1068, where cost_model and cost_tracker are introduced and try_add failures become retryable packet indexes. Additional evidence is around line 1179, where processed transactions update the shared CostTracker only when not present in unprocessed_tx_indexes. core/src/cost_tracker.rs introduces per-account and block cost tracking, and core/src/cost_model.rs describes cost estimation. The supplied evidence does not establish practical exploitability, exact limits, consensus impact, or a known vulnerability being fixed. Protocol security invariant: The banking stage should avoid admitting transactions beyond configured per-block and per-account cost limits, and shared cost accounting should reflect only transactions actually processed by the bank. The supplied evidence supports a resource-control invariant, but does not establish a concrete security vulnerability or exploit path. Verification notes: The patch does not prove a signature-verification or replay-validation bug. The evidence does not show that invalid transactions could be forged or replayed before this change. The evidence does not prove practical exploitability or a specific denial-of-service attack scenario. The patch may be introducing a new resource-management feature rather than fixing a known deployed vulnerability. The exact configured cost limits and consensus effects are not shown in the provided context. Downgraded from likely security-hardening to unclear because the provided evidence shows resource-control feature work but not a demonstrated vulnerability thesis. Rejected cryptography, replay, and signature-validation classifications as unsupported. Excluded from security corpus due to lack of established security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion-mitigation`
Final impact type: `denial-of-service`
Final confidence: `medium`
Final tags: `blockchain-core, validator, resource-control, transaction-admission, cost-model, denial-of-service`

The supplied evidence does not support the original cryptography, replay, or signature-validation framing, and it does not prove a concrete exploitable vulnerability. However, the patch clearly adds cost-based admission control and shared cost accounting in Solana's banking stage, limiting over-budget transactions before processing and tracking only processed transaction cost. In a validator transaction-processing path, that is sufficiently security-relevant resource-control hardening to retain as a security-hardening case, with conservative DoS/resource-exhaustion framing.

## Security Evidence

1. Adds CostModel and CostTracker to the banking-stage transaction conversion path.
2. Calculates transaction cost before admitting transactions for processing.
3. Defers transactions when CostTracker.try_add indicates cost limits would be exceeded.
4. Tracks per-account and per-block transaction cost in a new CostTracker subsystem.
5. Applies cost to the shared tracker only for transactions actually processed by the bank.

## Missing Evidence

1. No explicit vulnerability, CVE, advisory, or exploit scenario is provided.
2. No proof that the prior behavior enabled practical validator denial of service.
3. No evidence that consensus safety, signature validation, or replay protection was incorrect.
4. Exact production limits and attacker-controlled cost amplification are not shown.

## Claim Boundaries

1. Classify as resource-control hardening, not a confirmed vulnerability fix.
2. Do not retain the replay-or-signature-validation bug class.
3. Do not claim request forgery, replay acceptance, or cryptographic validation bypass.
4. Do not claim consensus compromise from the supplied patch alone.
