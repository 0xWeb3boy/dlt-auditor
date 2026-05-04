---
case_id: case_20240927_4a55b7de69
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-09-27
source_refs:
  - git:4a55b7de69c235679637b59b7f24e18ffb905892
  - "crates/services/txpool/src/transaction_selector.rs:7"
  - "crates/services/executor/src/executor.rs:580"
  - "crates/services/txpool/src/transaction_selector.rs:221"
  - "crates/services/executor/src/executor.rs:1443"
bug_class: consensus-resource-limit-enforcement
impact_type:
  - resource-control
  - consensus-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - consensus
  - resource-limit
  - block-size-limit
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch wires the new `block_transaction_size_limit` consensus parameter into transaction selection and executor accounting. The evidence supports a missing-enforcement or feature-completion interpretation for a newly introduced resource limit, but it does not establish a concrete vulnerability, exploit path, denial of service, or consensus failure.

## Observed Patch Facts

1. In `crates/services/txpool/src/transaction_selector.rs`, the patch replaces `// Expects sorted by gas price transactions, highest first` with `// Expects sorted by tip, highest first`.

2. In `crates/services/executor/src/executor.rs`, the patch replaces `let mut remaining_gas_limit = block_gas_limit.saturating_sub(data.used_gas);` with `let block_transaction_size_limit = self`.

3. In `crates/services/txpool/src/transaction_selector.rs`, the patch replaces `let selected = make_txs_and_select(&original, selection_limit);` with `let selected =`.

4. In `crates/services/executor/src/executor.rs`, the patch adds `execution_data.used_size = execution_data`.

## Project Context

The changed code sits primarily in `crates/services/txpool/src`, `crates/services/txpool`, `crates/services/executor/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/services/txpool/src/service.rs`, `crates/services/executor/src/ports.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/services/txpool/src/service.rs`, `crates/services/executor/src/ports.rs`. The strongest project-level identifiers around this patch are `u32::MAX`, `selected`, `block`, and `block_transaction_size_limit`. Nearby tests or test-like files include `crates/services/txpool/src/service/update_sender/tests/test_sending.rs`, `crates/services/txpool/src/service/update_sender/tests/test_e2e.rs`.

## Before/After Behavior

Before the patch, `select_transactions` accepted only a gas limit, executor processing used a `remaining_size = u32::MAX` placeholder with a TODO, and execution data updated `used_gas` without the shown `used_size` accounting. After the patch, selection accepts `block_transaction_size_limit`, executor reads the limit from consensus parameters and subtracts `data.used_size`, and execution data accumulates metered transaction byte size with checked overflow handling.

# Root Cause

The newly introduced block transaction byte-size consensus parameter had not yet been threaded through the shown block transaction selection and executor accounting paths. Gas was already tracked, while transaction byte size was either absent from the selector interface or represented by an effectively unlimited placeholder.

## Walkthrough

1. The txpool selector previously selected includable transactions using only `max_gas`.

2. Executor L2 processing read the block gas limit but left transaction-size capacity as `u32::MAX` with a TODO.

3. Execution data in the shown before hunk updated cumulative gas but not cumulative transaction byte size.

4. The patch adds `block_transaction_size_limit` to the selector interface and tracks gas and size separately during selection.

5. The executor now reads `block_transaction_size_limit()` from consensus params and computes remaining capacity from `data.used_size`.

6. The execution data path now adds each transaction's metered byte size and reports `TxSizeOverflow` on checked-add overflow.

7. Tests were updated to cover selection with both gas and size constraints.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/services/txpool/src/transaction_selector.rs | 7 | selects block transactions subject to gas and new transaction byte-size limit |
| crates/services/executor/src/executor.rs | 580 | loads consensus block transaction size limit and computes remaining transaction size capacity during L2 transaction processing |
| crates/services/executor/src/executor.rs | 1443 | updates per-block execution data with metered transaction byte size and reports size overflow |
| crates/services/txpool/src/transaction_selector.rs | 221 | tests transaction selection behavior with both gas and size limits |

## Code Snippets

## Snippet 1

Context: `crates/services/txpool/src/transaction_selector.rs:7` (changes a sensitive control or state-update path)

Before
```rust
// future for block producers to customize block building (e.g. alternative priorities besides gas fees)

// Expects sorted by gas price transactions, highest first
pub fn select_transactions(
    includable_txs: impl Iterator<Item = ArcPoolTx>,
    max_gas: u64,
) -> Vec<ArcPoolTx> {
    // Select all txs that fit into the block, preferring ones with higher gas price.
```
After
```rust
// future for block producers to customize block building (e.g. alternative priorities besides gas fees)

// Expects sorted by tip, highest first
pub fn select_transactions(
    includable_txs: impl Iterator<Item = ArcPoolTx>,
    max_gas: u64,
    block_transaction_size_limit: u32,
) -> impl Iterator<Item = ArcPoolTx> {
```

## Snippet 2

Context: `crates/services/executor/src/executor.rs:580` (changes a consensus- or validator-sensitive branch)

Before
```rust
} = components;
        let block_gas_limit = self.consensus_params.block_gas_limit();

        let mut remaining_gas_limit = block_gas_limit.saturating_sub(data.used_gas);
        // TODO: Handle `remaining_size` https://github.com/FuelLabs/fuel-core/issues/2133
        let remaining_size = u32::MAX;

        // We allow at most u16::MAX transactions in a block, including the mint transaction.
```
After
```rust
} = components;
        let block_gas_limit = self.consensus_params.block_gas_limit();
        let block_transaction_size_limit = self
            .consensus_params
            .block_transaction_size_limit()
            .try_into()
            .unwrap_or(u32::MAX);
```

## Snippet 3

Context: `crates/services/txpool/src/transaction_selector.rs:221` (changes a sensitive control or state-update path)

Before
```rust
];

        let selected = make_txs_and_select(&original, selection_limit);
        assert_eq!(
            expected_txs, selected,
            "Wrong txs selected for max_gas: {selection_limit}"
        );
    }
```
After
```rust
];

        let selected =
            make_txs_and_select(&original, selection_gas_limit, selection_size_limit);
        assert_eq!(
            expected_txs, selected,
            "Wrong txs selected for max_gas: {selection_gas_limit}"
        );
```

## Snippet 4

Context: `crates/services/executor/src/executor.rs:1443` (changes a sensitive control or state-update path)

Before
```rust
.checked_add(used_gas)
            .ok_or(ExecutorError::GasOverflow)?;

        if !reverted {
```
After
```rust
.checked_add(used_gas)
            .ok_or(ExecutorError::GasOverflow)?;
        execution_data.used_size = execution_data
            .used_size
            .checked_add(used_size)
            .ok_or(ExecutorError::TxSizeOverflow)?;

        if !reverted {
```

# Fix Pattern

Propagate the consensus resource parameter through all block construction layers, track cumulative resource usage in execution state, and use checked arithmetic for counter updates.

## How It Was Fixed

The patch adds the transaction byte-size limit to transaction selection, replaces the executor's unlimited-size placeholder with the configured consensus value minus already-used size, and extends `ExecutionData` accounting to record metered transaction byte size with overflow handling.

# Why It Matters

1. Consensus resource limits should be applied consistently.

2. A configured byte-size limit is ineffective if selection only checks gas.

3. Cumulative `used_size` accounting lets later transactions be evaluated against remaining capacity.

4. Checked accounting avoids silent counter overflow.

5. The evidence does not prove a concrete security impact.

# Evidence Notes

Grounded evidence comes from `crates/services/txpool/src/transaction_selector.rs` and `crates/services/executor/src/executor.rs`. The draft correctly rejects the unsupported malformed-decoding and panic narrative from the heuristic baseline. However, the mapper's `likely` security verdict and decision to keep this in the security corpus are stronger than the supplied evidence supports. The commit description frames the work as handling and enforcing a new consensus parameter, and no exploitability or pre-existing vulnerability thesis is demonstrated. Protocol security invariant: Block construction and execution accounting should apply the consensus `block_transaction_size_limit` consistently alongside gas limits, tracking cumulative transaction byte size for included L2 transactions. Verification notes: No evidence proves malformed transaction decoding could trigger a panic. No direct exploit path or remote denial-of-service mechanism is shown by the provided patch evidence. No consensus split is proven, only that a consensus resource parameter was previously not enforced in these paths. The change appears tied to handling a newly introduced consensus parameter, so it may be hardening or feature completion rather than a confirmed vulnerability fix. No evidence shows malformed input reaching a panic path. No direct remote denial-of-service mechanism is shown. No consensus split or invalid block acceptance is proven by the supplied evidence. This may be security-relevant resource-control hardening, but the vulnerability claim remains unestablished. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-resource-limit-enforcement`
Final impact type: `resource-control, consensus-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, consensus, resource-limit, block-size-limit, security-hardening`

The supplied patch evidence shows enforcement of a consensus-controlled block transaction byte-size limit across transaction selection and executor accounting, replacing an effectively unlimited placeholder and adding checked cumulative size accounting. This is security-relevant hardening of blockchain resource and consensus behavior, but the evidence does not prove a concrete exploitable vulnerability, denial-of-service path, or prior invalid block acceptance bug, so it should not be labeled as a confirmed security fix.

## Security Evidence

1. Transaction selection now accepts and applies block_transaction_size_limit in addition to max_gas.
2. Executor now reads block_transaction_size_limit from consensus parameters instead of using remaining_size = u32::MAX.
3. ExecutionData now accumulates used_size with checked_add and returns TxSizeOverflow on overflow.
4. Tests were updated to exercise selection under both gas and size limits.

## Missing Evidence

1. No direct exploit path is shown.
2. No evidence proves remote denial of service or consensus split.
3. No evidence shows malformed or oversized transactions were accepted into valid blocks before this patch.
4. No linked advisory or security issue is provided.

## Claim Boundaries

1. Classify as security hardening, not a confirmed vulnerability fix.
2. Do not claim malformed decoding, panic, or memory corruption.
3. Do not claim a proven liveness failure beyond conservative resource-control risk.
4. Do not claim consensus failure unless additional evidence shows invalid block production or acceptance.
