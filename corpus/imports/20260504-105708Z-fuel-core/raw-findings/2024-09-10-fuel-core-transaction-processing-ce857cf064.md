---
case_id: case_20240910_ce857cf064
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2024-09-10
source_refs:
  - git:ce857cf0640548403f70a7d1140e52088b3ba444
  - "crates/fuel-core/src/schema/tx.rs:287"
  - "crates/services/executor/src/executor.rs:950"
  - "crates/services/executor/src/ports.rs:67"
  - "crates/services/executor/src/executor.rs:574"
bug_class: resource-limit-enforcement
impact_type:
  - resource-exhaustion
tags:
  - blockchain-core
  - transaction-processing
  - gas-limit
  - resource-control
  - graphql
  - executor
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds consensus-parameter-aware max_gas checks to the GraphQL dry_run path and the executor regular L2 transaction loop. The evidence supports a resource-limit hardening finding: over-budget transactions are rejected from dry_run or skipped during executor processing. The evidence does not establish a concrete exploit, remote denial of service, consensus divergence, funds loss, authorization bypass, or panic path.

## Observed Patch Facts

1. In `crates/fuel-core/src/schema/tx.rs`, the patch replaces `for transaction in &mut transactions {` with `transactions.iter_mut().try_fold::<_, _, async_graphql::Result<u64>>(0u64, |acc, tx| {`.

2. In `crates/services/executor/src/executor.rs`, the patch replaces `let gas_costs = consensus_params.gas_costs();` with `let actual_max_gas = tx`.

3. In `crates/services/executor/src/ports.rs`, the patch replaces `pub trait TransactionsSource {` with `pub trait TransactionExt {`.

4. In `crates/services/executor/src/executor.rs`, the patch replaces `block,` with `if transaction.max_gas(&self.consensus_params)? > remaining_gas_limit {`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src/schema`, `crates/fuel-core/src`, `crates/services/executor/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/fuel-core/src/schema/dap.rs`, `crates/fuel-core/src/schema/chain.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/fuel-core/src/schema/dap.rs`, `crates/fuel-core/src/executor.rs`. The strongest project-level identifiers around this patch are `max_gas`, `consensus_params`, `gas_costs`, and `fee_params`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/tx_pool_gas_price_tests.rs`, `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the patch, the shown dry_run path decoded and precomputed submitted transactions without an observed check that their summed max_gas stayed within consensus_params.block_gas_limit(). After the patch, dry_run sums each transaction's max_gas using consensus parameters, rejects the request if the total exceeds block_gas_limit, and then precomputes each transaction. Before the patch, the shown executor loop proceeded from transaction id derivation to execute_transaction_and_commit. After the patch, it checks max_gas against remaining_gas_limit and records ExecutorError::GasOverflow instead of executing an over-budget transaction. The relayed transaction change centralizes max_gas calculation through a shared helper and is support code unless tied to the gas-limit checks.

# Root Cause

The prior code lacked explicit max_gas budget enforcement at the GraphQL dry_run boundary and in the executor's regular L2 transaction selection loop. This allowed transactions to reach simulation or execution selection without the shown code first proving they fit within the relevant consensus block gas budget.

## Walkthrough

1. GraphQL dry_run receives HexString transactions, decodes them, and obtains latest consensus parameters plus block_gas_limit.

2. Previously, the shown dry_run code precomputed decoded transactions without an accumulated max_gas check against block_gas_limit.

3. The patched dry_run code computes tx.max_gas(&consensus_params), accumulates it with saturating_add, and returns an async_graphql error if the sum exceeds the block gas limit.

4. Executor process_l2_txs computes remaining_gas_limit from block_gas_limit minus data.used_gas.

5. Previously, the shown executor loop moved from tx_id derivation directly toward execute_transaction_and_commit.

6. The patched executor loop skips transactions whose max_gas exceeds remaining_gas_limit and records ExecutorError::GasOverflow.

7. A shared TransactionExt::max_gas helper was added to compute max gas from ConsensusParameters across supported transaction variants and return an error for invalid types.

8. Relayed transaction validation now uses the shared helper rather than duplicating variant-specific max_gas calculation inline.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/fuel-core/src/schema/tx.rs | 287 | GraphQL dry_run now accumulates transaction max_gas and rejects batches above consensus block_gas_limit before precompute/execution simulation. |
| crates/services/executor/src/executor.rs | 574 | Executor regular L2 transaction processing now skips transactions whose max_gas exceeds remaining_gas_limit and records GasOverflow. |
| crates/services/executor/src/ports.rs | 67 | Shared TransactionExt::max_gas helper computes max gas from consensus parameters for supported transaction types and rejects invalid types. |
| crates/services/executor/src/executor.rs | 950 | Relayed transaction max-gas validation now uses the shared consensus-parameter-aware max_gas helper. |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/schema/tx.rs:287` (changes bounds, limits, or capacity handling)

Before
```rust
.map(|tx| FuelTx::from_bytes(&tx.0))
            .collect::<Result<Vec<FuelTx>, _>>()?;
        for transaction in &mut transactions {
            transaction.precompute(&params.chain_id())?;
        }

        let tx_statuses = block_producer
```
After
```rust
.map(|tx| FuelTx::from_bytes(&tx.0))
            .collect::<Result<Vec<FuelTx>, _>>()?;
        transactions.iter_mut().try_fold::<_, _, async_graphql::Result<u64>>(0u64, |acc, tx| {
            let gas = tx.max_gas(&consensus_params)?;
            let gas = gas.saturating_add(acc);
            if gas > block_gas_limit {
                return Err(anyhow::anyhow!("The sum of the gas usable by the transactions is greater than the block gas limit").into());
            }
```

## Snippet 2

Context: `crates/services/executor/src/executor.rs:950` (changes a consensus- or validator-sensitive branch)

Before
```rust
) -> Result<(), ForcedTransactionFailure> {
        let claimed_max_gas = relayed_tx.max_gas();
        let gas_costs = consensus_params.gas_costs();
        let fee_params = consensus_params.fee_params();
        let actual_max_gas = match tx {
            Transaction::Script(tx) => tx.max_gas(gas_costs, fee_params),
            Transaction::Create(tx) => tx.max_gas(gas_costs, fee_params),
            Transaction::Mint(_) => {
```
After
```rust
) -> Result<(), ForcedTransactionFailure> {
        let claimed_max_gas = relayed_tx.max_gas();
        let actual_max_gas = tx
            .max_gas(consensus_params)
            .map_err(|_| ForcedTransactionFailure::InvalidTransactionType)?;
        if actual_max_gas > claimed_max_gas {
            return Err(ForcedTransactionFailure::InsufficientMaxGas {
```

## Snippet 3

Context: `crates/services/executor/src/ports.rs:67` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

pub trait TransactionsSource {
    /// Returns the next batch of transactions to satisfy the `gas_limit`.
```
After
```rust
}

pub trait TransactionExt {
    fn max_gas(&self, consensus_params: &ConsensusParameters) -> ExecutorResult<u64>;
}

impl TransactionExt for Transaction {
    fn max_gas(&self, consensus_params: &ConsensusParameters) -> ExecutorResult<u64> {
```

## Snippet 4

Context: `crates/services/executor/src/executor.rs:574` (changes a consensus- or validator-sensitive branch)

Before
```rust
for transaction in regular_tx_iter {
                let tx_id = transaction.id(&self.consensus_params.chain_id());
                match self.execute_transaction_and_commit(
                    block,
```
After
```rust
for transaction in regular_tx_iter {
                let tx_id = transaction.id(&self.consensus_params.chain_id());
                if transaction.max_gas(&self.consensus_params)? > remaining_gas_limit {
                    data.skipped_transactions
                        .push((tx_id, ExecutorError::GasOverflow));
                    continue;
                }
                match self.execute_transaction_and_commit(
```

# Fix Pattern

Add explicit resource-budget checks at transaction intake and executor selection boundaries, using consensus parameters to compute max_gas and rejecting or skipping transactions that exceed the applicable block gas budget. Centralize max_gas calculation to reduce inconsistent handling across executor paths.

## How It Was Fixed

dry_run now sums max_gas for all submitted transactions and errors when the total is greater than the consensus block gas limit. process_l2_txs now compares each regular transaction's max_gas with remaining_gas_limit and skips over-budget transactions with GasOverflow. TransactionExt::max_gas centralizes consensus-parameter-aware max gas calculation for supported transaction types.

# Why It Matters

1. Adds explicit gas-budget enforcement to GraphQL dry_run.

2. Adds executor-side skipping for transactions that cannot fit in the remaining block gas budget.

3. Reduces inconsistent max_gas handling across executor code paths.

4. Security impact is plausible as resource-limit hardening, but the supplied evidence does not prove an exploit.

# Evidence Notes

Grounded evidence comes from crates/fuel-core/src/schema/tx.rs line 287, crates/services/executor/src/executor.rs lines 574 and 950, and crates/services/executor/src/ports.rs line 67. The commit message directly describes adding checks so dry_run transactions do not spend too much gas and adding the check at executor level. Unsupported claims from the heuristic baseline about malformed decoded values, panic-prone conversion, process crashes, or broader node interruption are not supported by the provided hunks. Protocol security invariant: Transactions submitted for dry_run or selected for executor processing should be bounded by the consensus block gas budget: dry_run batches should not have summed max_gas above block_gas_limit, and executor processing should not execute a regular transaction whose max_gas exceeds the remaining block gas budget. Verification notes: The patch does not prove remote exploitability of the GraphQL dry_run endpoint. The patch does not show funds loss, authorization bypass, or signature validation failure. The patch does not prove a consensus divergence; it enforces local block gas budgeting before or during execution. The patch does not prove a panic path despite the heuristic baseline mentioning panic-prone conversion. The relayed transaction hunk appears mostly helper consolidation unless tied to max_gas validation semantics. No evidence proves remote exploitability of the dry_run endpoint. No evidence proves funds loss, authorization bypass, signature validation failure, or consensus divergence. No evidence proves a panic or crash path. Helper-file changes appear to support shared max_gas calculation, not to be the root cause by themselves. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-limit-enforcement`
Final impact type: `resource-exhaustion`
Final tags: `blockchain-core, transaction-processing, gas-limit, resource-control, graphql, executor`

The supplied patch evidence supports security hardening around gas-budget enforcement, not a proven exploitable vulnerability. The change adds explicit max_gas checks at the GraphQL dry_run boundary and executor transaction-processing path, preventing over-budget transaction batches or transactions from being simulated or executed past the block gas budget. The original finding is directionally valid, but its liveness-failure framing and unrelated tags such as signature and database are too strong for the evidence shown.

## Security Evidence

1. GraphQL dry_run now sums transaction max_gas using consensus parameters and rejects batches above block_gas_limit.
2. Executor regular L2 transaction processing now skips transactions whose max_gas exceeds remaining_gas_limit and records GasOverflow.
3. The commit message explicitly says the change prevents dry_run transactions from spending too much gas and adds the check at executor level.
4. The helper centralizes consensus-parameter-aware max_gas calculation across transaction variants.

## Missing Evidence

1. No proof that the prior behavior was remotely exploitable for denial of service.
2. No evidence of consensus divergence, funds loss, authorization bypass, signature failure, panic, or crash.
3. No demonstrated attack scenario showing that over-budget dry_run or executor processing caused node-wide liveness loss.
4. The relayed transaction hunk appears primarily to consolidate max_gas calculation unless additional semantic impact is shown.

## Claim Boundaries

1. Keep as resource-control security hardening, not as a confirmed vulnerability fix.
2. Do not claim funds loss, signature validation failure, database corruption, or authorization bypass.
3. Do not claim consensus divergence from the supplied patch alone.
4. Impact should be limited to preventing excessive gas/resource use in dry_run and executor transaction selection.
