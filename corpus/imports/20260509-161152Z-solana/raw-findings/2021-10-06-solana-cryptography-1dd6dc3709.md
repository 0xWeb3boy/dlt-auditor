---
case_id: case_20211006_1dd6dc3709
project: solana
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2021-10-06
source_refs:
  - git:1dd6dc3709b9676b99bedec36db51c0c95731972
  - "ledger-tool/src/main.rs:731"
  - "runtime/src/bank.rs:3653"
  - "core/src/replay_stage.rs:1833"
  - "ledger/src/blockstore.rs:8892"
bug_class: resource-accounting-hardening
impact_type:
  - availability
  - resource-exhaustion
confidence: medium
tags:
  - validator
  - resource-control
  - cost-model
  - block-cost-limit
  - replay
  - blockstore
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a conservative security-hardening classification for Solana's cost-model/resource-accounting subsystem. The commit broadly introduces and wires cost tracking, execution-cost feedback, bounded cost-table state, persistence, and block cost rejection. It does not establish a specific exploit, cryptographic flaw, or proven prior consensus violation.

## Observed Patch Facts

1. In `ledger-tool/src/main.rs`, the patch replaces `fn open_genesis_config_by(ledger_path: &Path, matches: &ArgMatches<'_>) -> GenesisCon...` with `fn compute_slot_cost(blockstore: &Blockstore, slot: Slot) -> Result<(), String> {`.

2. In `runtime/src/bank.rs`, the patch replaces `signature_count += u64::from(tx.message().header.num_required_signatures);` with `let feature_set = self.feature_set.clone();`.

3. In `core/src/replay_stage.rs`, the patch replaces `inc_new_counter_info!("replay_stage-replay_transactions", tx_count);` with `// send accumulated excute-timings to cost_update_service`.

4. In `ledger/src/blockstore.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `ledger-tool/src`, `runtime/src`, `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `ledger/src/blockstore_processor.rs`, `ledger/src/blockstore_db.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/leader_schedule_cache.rs`, `ledger/src/blockstore_processor.rs`. The strongest project-level identifiers around this patch are `blockstore`, `slot`, `None`, and `HashMap::new`.

## Before/After Behavior

Before the change, the provided evidence does not show this cost-model plumbing in the selected locations. After the change, ledger tooling can compute slot cost and reject dead slots for that operation; runtime/replay paths collect and forward execution timing data; blockstore gains cost-table persistence test coverage; and the commit body describes transaction cost checks, bounded execution-cost table capacity, cost-table persistence/restoration, and rejection of blocks above the max block cost.

# Root Cause

The supported root cause is incomplete or newly introduced resource-accounting coverage across transaction packing, execution timing feedback, learned program-cost state, and block cost enforcement. The evidence does not prove a concrete vulnerability trigger or exploit path.

## Walkthrough

1. The commit body adds a CostModel and CostTracker for estimating and tracking transaction costs per block.

2. TransactionCost is expanded to include account-access cost with different weights for read/write and signed/non-signed access.

3. The commit body describes checking transaction cost against a cost tracker and returning over-limit transactions as unprocessed instead of adding them to the block.

4. Replay sends non-empty per-program execution timings to a cost update service, with warning logging if the send fails.

5. The execution cost table is described as fixed-capacity for a security concern, evicting old and low-occurrence programs when full.

6. Program cost data is persisted to and restored from blockstore, with test coverage for cost-table read/write behavior.

7. The ledger-tool path adds compute_slot_cost() and rejects dead slots for that computation.

8. The commit body states that blocks above the max block cost are rejected.

9. The evidence supports resource-control hardening, but not a confirmed exploit or cryptography fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 3653 | transaction execution path where compute budget, feature set, loaded accounts, and execution timing collection are integrated |
| core/src/replay_stage.rs | 1833 | replay path sends accumulated per-program execution timings to the cost update service |
| ledger/src/blockstore.rs | 8892 | blockstore persistence test coverage for reading and writing the program cost table |
| ledger-tool/src/main.rs | 731 | tooling path computes slot cost from blockstore entries and rejects dead slots for that operation |

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

Add explicit bounded resource accounting and cost enforcement across banking, runtime, replay, and storage paths.

## How It Was Fixed

The change added transaction and block cost tracking, account-access and execution-cost components, replay feedback into a cost update service, fixed-capacity learned program-cost storage, blockstore persistence/restoration for cost data, and max-block-cost rejection behavior described in the commit body.

# Why It Matters

1. Bounds resource consumption during transaction packing and block processing.

2. Limits growth of learned per-program cost state.

3. Feeds observed execution cost back into future accounting.

4. Can reject blocks that exceed configured cost limits.

5. Evidence supports hardening, not a confirmed vulnerability fix.

# Evidence Notes

Grounded evidence comes mainly from the commit body plus selected hunks in runtime/src/bank.rs, core/src/replay_stage.rs, ledger/src/blockstore.rs, and ledger-tool/src/main.rs. The earlier cryptography/state-corruption framing is unsupported. Claims of remote exploitability, consensus breakage, or a specific attack are not supported by the supplied evidence. Protocol security invariant: Validators should apply bounded resource accounting to transaction and block processing so transaction packing and block acceptance respect configured cost limits, and learned per-program execution-cost state does not grow without bound. Verification notes: The patch does not prove a remotely exploitable denial of service on its own. The evidence does not show a cryptographic invariant being repaired. The evidence does not prove prior accepted blocks could violate consensus without the new checks. Many changes are feature introduction, persistence, metrics, refactor, and performance work rather than a targeted vulnerability fix. The dead-slot guard in ledger-tool appears ancillary tooling behavior, not the core security invariant. No external files or commands were used. No exploitability proof is present in the provided evidence. Classification is based on explicit resource-control and security-concern language in the commit body. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-accounting-hardening`
Final impact type: `availability, resource-exhaustion`
Final confidence: `medium`
Final tags: `validator, resource-control, cost-model, block-cost-limit, replay, blockstore`

The supplied evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The commit introduces broad cost-model/resource-accounting controls, bounded execution-cost-table state, persistence, replay feedback, and block cost rejection. That is security-relevant for validator resource control, especially with explicit commit-body language about fixed capacity for a security concern, but the patch evidence does not prove a concrete exploit, cryptographic flaw, state corruption bug, or prior consensus violation.

## Security Evidence

1. Commit body says the cost model limits transactions that are not parallelizeable.
2. Commit body describes a fixed-capacity ExecuteCostTable added for a security concern.
3. Commit body states blocks above the max block cost are rejected.
4. Replay path forwards per-program execution timings to update cost accounting.
5. Blockstore gains persistence coverage for cost-table state.
6. Changes touch validator/runtime/replay/blockstore paths involved in transaction and block processing.

## Missing Evidence

1. No concrete exploit scenario is shown.
2. No proof that previous behavior allowed accepted invalid blocks or consensus divergence.
3. No cryptographic code or cryptographic invariant repair is evidenced.
4. Selected hunks mostly show plumbing, tooling, persistence tests, and feedback paths rather than a targeted vulnerability fix.
5. The broad commit includes performance, metrics, refactor, feature introduction, and maintenance work.

## Claim Boundaries

1. Classify as resource-control hardening, not cryptography.
2. Do not claim state corruption from the supplied evidence.
3. Do not claim a confirmed denial-of-service vulnerability, only resource-exhaustion hardening.
4. Do not claim exploitability or consensus safety impact beyond max-cost enforcement described in the commit body.
5. Dead-slot handling in ledger-tool is ancillary and not the core security evidence.
