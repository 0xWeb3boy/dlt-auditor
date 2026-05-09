---
case_id: case_20211006_db85d659b9
project: solana
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2021-10-06
source_refs:
  - git:db85d659b9b6bd7947aa07eca32ca0061d5a75fc
  - "ledger-tool/src/main.rs:731"
  - "runtime/src/bank.rs:3653"
  - "core/src/replay_stage.rs:1833"
  - "ledger/src/blockstore.rs:8892"
bug_class: resource-accounting-hardening
impact_type:
  - denial-of-service
confidence: medium
tags:
  - validator
  - resource-control
  - cost-model
  - replay
  - block-limits
  - denial-of-service-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is a broad Solana cost-model rollout across banking, replay, runtime execution, blockstore persistence, and tooling. It appears to add resource accounting and block/transaction cost limits, with some security-relevant motivation, but the supplied evidence does not prove that it fixes a specific vulnerability.

## Observed Patch Facts

1. In `ledger-tool/src/main.rs`, the patch replaces `fn open_genesis_config_by(ledger_path: &Path, matches: &ArgMatches<'_>) -> GenesisCon...` with `fn compute_slot_cost(blockstore: &Blockstore, slot: Slot) -> Result<(), String> {`.

2. In `runtime/src/bank.rs`, the patch replaces `signature_count += u64::from(tx.message().header.num_required_signatures);` with `let feature_set = self.feature_set.clone();`.

3. In `core/src/replay_stage.rs`, the patch replaces `inc_new_counter_info!("replay_stage-replay_transactions", tx_count);` with `// send accumulated excute-timings to cost_update_service`.

4. In `ledger/src/blockstore.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `ledger-tool/src`, `runtime/src`, `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `ledger/src/blockstore_processor.rs`, `ledger/src/blockstore_db.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/leader_schedule_cache.rs`, `ledger/src/blockstore_processor.rs`. The strongest project-level identifiers around this patch are `blockstore`, `slot`, `None`, and `HashMap::new`.

## Before/After Behavior

Before the patch, the provided evidence indicates that cost-model infrastructure, per-block cost tracking, replay feedback of program execution timings, and ProgramCosts persistence were absent or incomplete. After the patch, the system includes transaction/block cost accounting, replay feedback to a cost update service, persisted program cost data, tooling to compute slot cost, and commit-described rejection or deferral of over-limit work.

# Root Cause

The evidence supports an incomplete resource-accounting design before this rollout, not a demonstrated vulnerability root cause. It does not show a specific attacker-controlled input, consensus failure, state corruption, or cryptographic flaw.

## Walkthrough

1. CostModel and CostTracker are introduced to estimate transaction cost and track accumulated block cost.

2. TransactionCost gains account-access costs with different weights for access types.

3. Banking-stage behavior is described as checking transaction cost and buffering transactions that would exceed limits.

4. Replay stage sends per-program execution timings to a cost update service when timing details exist.

5. Runtime bank execution setup changes support execution context and cost-accounting data collection, but the supplied hunk alone does not prove a security fix.

6. The execute-cost table is described as bounded and subject to eviction, with the commit mentioning a security concern for fixed capacity.

7. Blockstore gains ProgramCosts persistence and tests for reading and writing cost-table data.

8. Ledger tooling gains compute_slot_cost and rejects dead slots before loading entries.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/banking_stage.rs | 1 | applies transaction cost checks while selecting transactions for block processing |
| core/src/cost_tracker.rs | 1 | tracks accumulated block transaction cost and determines whether additional transactions fit |
| core/src/cost_model.rs | 1 | estimates transaction and program execution costs used by cost tracking |
| ledger/src/block_cost_limits.rs | 1 | defines maximum cost limits used to bound block processing |
| ledger/src/blockstore_processor.rs | 1 | rejects or processes replayed blocks according to block cost limits |
| runtime/src/bank.rs | 3653 | executes loaded transactions and records execution details used for cost accounting |
| core/src/replay_stage.rs | 1833 | sends accumulated per-program execution timings to the cost update service |
| ledger/src/blockstore.rs | 8892 | tests persisted read/write behavior for the program cost table |
| ledger-tool/src/main.rs | 731 | adds tooling to compute slot cost from blockstore entries |

## Code Snippets

## Snippet 1

Context: `ledger-tool/src/main.rs:731` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

fn open_genesis_config_by(ledger_path: &Path, matches: &ArgMatches<'_>) -> GenesisConfig {
    let max_genesis_archive_unpacked_size =
```
After
```rust
}

fn compute_slot_cost(blockstore: &Blockstore, slot: Slot) -> Result<(), String> {
    if blockstore.is_dead(slot) {
        return Err("Dead slot".to_string());
    }

    let (entries, _num_shreds, _is_full) = blockstore
```

## Snippet 2

Context: `runtime/src/bank.rs:3653` (changes a sensitive control or state-update path)

Before
```rust
.map(|(accs, tx)| match accs {
                (Err(e), _nonce_rollback) => {
                    inner_instructions.push(None);
                    transaction_log_messages.push(None);
                    (Err(e.clone()), None)
                }
                (Ok(loaded_transaction), nonce_rollback) => {
                    signature_count += u64::from(tx.message().header.num_required_signatures);
```
After
```rust
.map(|(accs, tx)| match accs {
                (Err(e), _nonce_rollback) => {
                    transaction_log_messages.push(None);
                    inner_instructions.push(None);
                    (Err(e.clone()), None)
                }
                (Ok(loaded_transaction), nonce_rollback) => {
                    let feature_set = self.feature_set.clone();
```

## Snippet 3

Context: `core/src/replay_stage.rs:1833` (changes a sensitive control or state-update path)

Before
```rust
}
        }
        inc_new_counter_info!("replay_stage-replay_transactions", tx_count);
        did_complete_bank
```
After
```rust
}
        }

        // send accumulated excute-timings to cost_update_service
        if !execute_timings.details.per_program_timings.is_empty() {
            cost_update_sender
                .send(execute_timings)
                .unwrap_or_else(|err| warn!("cost_update_sender failed: {:?}", err));
```

## Snippet 4

Context: `ledger/src/blockstore.rs:8892` (changes persisted or aggregate state handling)

Before
```rust
Blockstore::destroy(&blockstore_path).expect("Expected successful database destruction");
    }
}
```
After
```rust
Blockstore::destroy(&blockstore_path).expect("Expected successful database destruction");
    }

    #[test]
    fn test_read_write_cost_table() {
        let blockstore_path = get_tmp_ledger_path!();
        {
            let blockstore = Blockstore::open(&blockstore_path).unwrap();
```

# Fix Pattern

Introduce resource accounting and bounded metadata: estimate transaction costs, track accumulated block costs, reject or defer over-limit work, bound learned program-cost data, and persist cost data across restart.

## How It Was Fixed

The patch wires cost-model components through banking, replay, runtime, ledger storage, and tooling. It adds cost tracking, program execution timing feedback, bounded cost-table behavior, ProgramCosts persistence, and tests around cost-table storage.

# Why It Matters

1. May reduce validator exposure to expensive or poorly parallelizable workloads.

2. May improve consistency of resource accounting across banking and replay.

3. Bounds learned cost metadata growth.

4. Does not establish a concrete vulnerability from the provided evidence.

# Evidence Notes

The mapper correctly downgrades away from cryptography and state corruption. However, the draft still overstates security certainty. The commit body contains resource-control and one explicit security-concern phrase, but the selected hunks and context do not prove exploitability, prior consensus acceptance of invalid blocks, or a concrete denial-of-service bug. This should not be treated as a confirmed or likely vulnerability fix on the supplied evidence alone. Protocol security invariant: Validator transaction and block processing should account for execution and account-access costs and avoid admitting work above configured cost limits. The provided evidence supports resource-control functionality and possible hardening, but does not establish a concrete vulnerability or exploit path. Verification notes: The patch does not prove a remotely exploitable denial-of-service vulnerability by itself. The patch does not show cryptographic verification logic being fixed. The patch does not prove prior accepted blocks could violate consensus across honest validators. The patch includes substantial feature, persistence, metrics, and performance work beyond any security-relevant change. The selected evidence does not identify a specific attacker-controlled input that corrupts state. No direct exploit scenario is shown. No attacker-controlled input path is demonstrated. No cryptographic verification fix is shown. No consensus break is proven. Classification is limited to possible resource-control hardening. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-accounting-hardening`
Final impact type: `denial-of-service`
Final confidence: `medium`
Final tags: `validator, resource-control, cost-model, replay, block-limits, denial-of-service-hardening`

The evidence does not support the original cryptography/state-corruption framing or a concrete security-fix claim, but it does support retaining this as security hardening. The commit explicitly introduces validator cost accounting, transaction/block cost limits, rejection or buffering of over-limit work, and a bounded execute-cost table described as addressing a security concern. That is resource-control hardening for a security-sensitive validator path, even though exploitability and a specific prior vulnerability are not proven.

## Security Evidence

1. Commit body says the cost model limits transactions that are not parallelizable.
2. Commit body describes returning transactions that exceed limits as unprocessed and only applying processed transaction costs to the tracker.
3. Commit body includes rejecting blocks whose cost exceeds the maximum block cost.
4. Commit body explicitly says ExecuteCostTable has fixed capacity for a security concern.
5. Changed files span banking, replay, runtime, block cost limits, and blockstore persistence, which are validator-critical execution paths.

## Missing Evidence

1. No concrete attacker-controlled transaction or block input is demonstrated.
2. No exploit scenario or measured denial-of-service condition is shown.
3. Selected hunks do not directly show the block-cost rejection logic.
4. No cryptographic verification fix or state-corruption repair is evidenced.
5. No proof that honest validators previously accepted invalid consensus state is provided.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed vulnerability fix.
2. Do not describe this as cryptography-related.
3. Do not claim state corruption or state-integrity impact from the supplied evidence.
4. Limit impact to possible denial-of-service/resource exhaustion mitigation.
5. Treat the broad patch as a cost-model/resource-control rollout with security-relevant hardening elements.
