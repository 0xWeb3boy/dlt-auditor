---
case_id: case_20240703_4a3cfc8e4a
project: fuel-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2024-07-03
source_refs:
  - git:4a3cfc8e4abeff7e859dc21c2479480a5b30bc1e
  - "crates/fuel-core/src/service/adapters/consensus_parameters_provider.rs:96"
  - "crates/services/executor/src/executor.rs:704"
  - "crates/services/executor/src/executor.rs:1048"
  - "crates/types/src/services/txpool.rs:61"
bug_class: stale-consensus-parameter-validation
impact_type:
  - consensus-integrity
  - transaction-validation
confidence: medium
tags:
  - consensus
  - txpool
  - executor
  - stale-validation
  - consensus-parameters
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for stale Checked transaction handling across consensus-parameter upgrades in the TxPool-to-executor path. The evidence supports a consensus-validity bug where TxPool could retain checked transactions validated under older parameters and the executor previously lacked version metadata to decide whether cached validation was still valid.

## Observed Patch Facts

1. In `crates/fuel-core/src/service/adapters/consensus_parameters_provider.rs`, the patch replaces `let version = *self.latest_consensus_parameters_version.lock();` with `self.latest_consensus_parameters_with_version().1`.

2. In `crates/services/executor/src/executor.rs`, the patch replaces `for transaction in relayed_tx_iter {` with `let consensus_parameters_version = block_header.consensus_parameters_version;`.

3. In `crates/services/executor/src/executor.rs`, the patch replaces `MaybeCheckedTransaction::CheckedTransaction(checked_tx) => checked_tx,` with `let actual_version = header.consensus_parameters_version;`.

4. In `crates/types/src/services/txpool.rs`, the patch replaces `Script(Checked<Script>),` with `Script(Checked<Script>, ConsensusParametersVersion),`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src/service/adapters`, `crates/fuel-core/src/service`, `crates/services/executor/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/services/executor/src/ports.rs`, `crates/types/src/services/executor.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/services/executor/src/ports.rs`, `crates/fuel-core/src/service/genesis.rs`. The strongest project-level identifiers around this patch are `MaybeCheckedTransaction::CheckedTransaction`, `Checked`, `checked_tx`, and `Script`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/tx_pool_gas_price_tests.rs`, `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the patch, PoolTransaction and MaybeCheckedTransaction::CheckedTransaction carried checked transaction values without the ConsensusParametersVersion used to validate them, and executor conversion accepted checked transactions directly. After the patch, checked pool transactions carry the validation version, version-aware consensus parameter access is available, and executor conversion compares the checked version with the block header consensus_parameters_version, revalidating the underlying transaction when they differ.

# Root Cause

The TxPool could preserve Checked transactions across a consensus-parameter upgrade without recording which ConsensusParametersVersion produced the checked state. The executor then could not distinguish cached validation produced under the block's parameters from cached validation produced under stale parameters.

## Walkthrough

1. A transaction was checked for TxPool using the consensus parameters current at that time.

2. The old PoolTransaction representation stored the Checked transaction but not the parameters version used for validation.

3. After a network consensus-parameter upgrade, TxPool could still hold the earlier Checked transaction.

4. Before the fix, executor conversion returned MaybeCheckedTransaction::CheckedTransaction directly as already checked.

5. The patch adds ConsensusParametersVersion metadata to checked pool transactions and propagates it through the checked transaction path.

6. During execution, the executor compares the checked transaction's version with the block header consensus_parameters_version.

7. If the versions differ, the executor unwraps the checked transaction and reruns basic checking under the executor's consensus parameters.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/types/src/services/txpool.rs | 61 | stores the consensus parameters version alongside each checked pool transaction |
| crates/services/executor/src/executor.rs | 704 | wraps relayed checked transactions with the block header consensus parameters version during execution |
| crates/services/executor/src/executor.rs | 1048 | compares checked transaction validation version against the block header version and revalidates on mismatch |
| crates/fuel-core/src/service/adapters/consensus_parameters_provider.rs | 96 | exposes latest consensus parameters together with their version for callers that need version-aware validation |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/service/adapters/consensus_parameters_provider.rs:96` (changes a consensus- or validator-sensitive branch)

Before
```rust
pub fn latest_consensus_parameters(&self) -> Arc<ConsensusParameters> {
        let version = *self.latest_consensus_parameters_version.lock();
        self.get_consensus_parameters(&version)
            .expect("The latest consensus parameters always are available unless this function was called before regenesis.")
    }
}
```
After
```rust
pub fn latest_consensus_parameters(&self) -> Arc<ConsensusParameters> {
        self.latest_consensus_parameters_with_version().1
    }

    pub fn latest_consensus_parameters_with_version(
        &self,
    ) -> (ConsensusParametersVersion, Arc<ConsensusParameters>) {
```

## Snippet 2

Context: `crates/services/executor/src/executor.rs:704` (changes a consensus- or validator-sensitive branch)

Before
```rust
let block_header = partial_block.header;
        let block_height = block_header.height();
        let relayed_tx_iter = forced_transactions.into_iter();
        for transaction in relayed_tx_iter {
            let maybe_checked_transaction =
                MaybeCheckedTransaction::CheckedTransaction(transaction);
            let tx_id = maybe_checked_transaction.id(&self.consensus_params.chain_id());
            match self.execute_transaction_and_commit(
```
After
```rust
let block_header = partial_block.header;
        let block_height = block_header.height();
        let consensus_parameters_version = block_header.consensus_parameters_version;
        let relayed_tx_iter = forced_transactions.into_iter();
        for checked in relayed_tx_iter {
            let maybe_checked_transaction = MaybeCheckedTransaction::CheckedTransaction(
                checked,
                consensus_parameters_version,
```

## Snippet 3

Context: `crates/services/executor/src/executor.rs:1048` (changes a consensus- or validator-sensitive branch)

Before
```rust
) -> ExecutorResult<CheckedTransaction> {
        let block_height = *header.height();
        let checked_tx = match tx {
            MaybeCheckedTransaction::Transaction(tx) => tx
                .into_checked_basic(block_height, &self.consensus_params)?
                .into(),
            MaybeCheckedTransaction::CheckedTransaction(checked_tx) => checked_tx,
        };
```
After
```rust
) -> ExecutorResult<CheckedTransaction> {
        let block_height = *header.height();
        let actual_version = header.consensus_parameters_version;
        let checked_tx = match tx {
            MaybeCheckedTransaction::Transaction(tx) => tx
                .into_checked_basic(block_height, &self.consensus_params)?
                .into(),
            MaybeCheckedTransaction::CheckedTransaction(checked_tx, checked_version) => {
```

## Snippet 4

Context: `crates/types/src/services/txpool.rs:61` (changes a consensus- or validator-sensitive branch)

Before
```rust
pub enum PoolTransaction {
    /// Script
    Script(Checked<Script>),
    /// Create
    Create(Checked<Create>),
    /// Upgrade
    Upgrade(Checked<Upgrade>),
    /// Upload
```
After
```rust
pub enum PoolTransaction {
    /// Script
    Script(Checked<Script>, ConsensusParametersVersion),
    /// Create
    Create(Checked<Create>, ConsensusParametersVersion),
    /// Upgrade
    Upgrade(Checked<Upgrade>, ConsensusParametersVersion),
    /// Upload
```

# Fix Pattern

Carry version metadata with cached validation artifacts and enforce a version match before reusing them across subsystem boundaries.

## How It Was Fixed

PoolTransaction variants were changed to store ConsensusParametersVersion alongside each Checked transaction. MaybeCheckedTransaction::CheckedTransaction handling was updated so checked transactions include a version. The executor now compares that version to the block header consensus_parameters_version and revalidates on mismatch. The consensus parameters provider also exposes a method returning latest parameters together with their version.

# Why It Matters

1. Checked transactions are validation artifacts tied to consensus parameters.

2. Consensus-parameter upgrades can make cached TxPool checked entries stale.

3. The fix prevents stale checked state from being reused silently during execution.

4. The provided evidence does not prove remote exploitability or finalized invalid block acceptance.

# Evidence Notes

Grounded evidence includes PoolTransaction version storage in crates/types/src/services/txpool.rs, executor wrapping of checked transactions with consensus parameter versions in crates/services/executor/src/executor.rs, executor mismatch revalidation in convert_maybe_checked_tx_to_checked_tx, and latest_consensus_parameters_with_version in the consensus parameters provider. The commit message explicitly states TxPool could store invalid Checked transactions after a consensus-parameter upgrade. The evidence does not establish fund theft, signature bypass, permission bypass, or a demonstrated finalized-block exploit. Protocol security invariant: A cached Checked transaction is only safe to trust for the ConsensusParametersVersion used when it was checked. If block execution uses a different consensus parameters version, the transaction must be revalidated before execution. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show that invalid transactions were accepted into finalized blocks before the fix. The patch does not establish fund theft, signature bypass, or permission bypass. The patch is specific to stale Checked transactions across consensus-parameter upgrades, not a general TxPool validation failure. Code evidence supports a stale validation bug specific to consensus-parameter upgrades. The stronger generic storage/state-corruption classification is not supported and was downgraded. Security verdict remains likely rather than confirmed because exploitability and finalized-chain impact are not demonstrated in the provided input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `stale-consensus-parameter-validation`
Final impact type: `consensus-integrity, transaction-validation`
Final confidence: `medium`
Final tags: `consensus, txpool, executor, stale-validation, consensus-parameters`

The supplied evidence supports retaining this as security hardening rather than a confirmed security fix. The patch adds consensus-parameter version metadata to checked transactions and forces revalidation when a cached checked transaction was validated under a different consensus-parameter version than the block being executed. That is clearly security-sensitive consensus-validation hardening, but the evidence does not prove exploitability, finalized invalid block acceptance, state corruption, or a concrete attacker impact.

## Security Evidence

1. Commit message states TxPool could store invalid Checked transactions after a consensus-parameter upgrade.
2. PoolTransaction now stores ConsensusParametersVersion alongside Checked transactions.
3. Executor now compares the checked transaction version against the block header consensus_parameters_version.
4. Executor revalidates the underlying transaction when the checked version differs from the block version.
5. The changed path is consensus and block-execution sensitive.

## Missing Evidence

1. No proof that stale checked transactions could be included in finalized blocks before the fix.
2. No demonstrated attacker-controlled exploit path.
3. No evidence of fund loss, signature bypass, authorization bypass, or durable state corruption.
4. No test or patch evidence showing a concrete consensus split or invalid state transition.

## Claim Boundaries

1. Classify as consensus-validation hardening, not generic storage or database state corruption.
2. Do not claim confirmed exploitability from the provided evidence.
3. Do not claim finalized-chain impact or fund impact.
4. The supported issue is stale cached validation across consensus-parameter upgrades.
