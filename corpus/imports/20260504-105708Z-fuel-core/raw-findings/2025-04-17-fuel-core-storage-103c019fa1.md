---
case_id: case_20250417_103c019fa1
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
date: 2025-04-17
source_refs:
  - git:103c019fa1ad41c8bc692b21f5c4066276c29f40
  - "crates/fuel-core/src/executor.rs:4073"
  - "crates/fuel-core/src/executor.rs:4267"
  - "crates/services/executor/src/executor.rs:2071"
  - "crates/fuel-core/src/executor.rs:4302"
bug_class: missing-utxo-consumption
impact_type:
  - double-spend
  - state-integrity
tags:
  - blockchain-core
  - executor
  - storage
  - utxo
  - data-coin
  - double-spend
  - state-consumption
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The supported finding is a data coin UTXO spend-state bug in the executor. The patch adds `Input::DataCoinSigned` and `Input::DataCoinPredicate` to the `spend_input_utxos` match arm that prunes spent UTXOs from storage, and the regression test commits a first data coin spend before asserting that a second spend of the same data coin is skipped.

## Observed Patch Facts

1. In `crates/fuel-core/src/executor.rs`, the patch replaces `let (` with `let ExecutionResult {`.

2. In `crates/fuel-core/src/executor.rs`, the patch replaces `header_to_produce: block_2_header,` with `header_to_produce: PartialBlockHeader::default(),`.

3. In `crates/services/executor/src/executor.rs`, the patch replaces `}) => {` with `})`.

4. In `crates/fuel-core/src/executor.rs`, the patch replaces `.into();` with `.into_result();`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src`, `crates/fuel-core`, `crates/services/executor/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/fuel-core/src/service.rs`, `crates/fuel-core/src/database.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/fuel-core/src/service/adapters.rs`, `crates/fuel-core/src/service.rs`. The strongest project-level identifiers around this patch are `OnceTransactionsSource::new`, `Default::default`, `skipped_transactions`, and `into`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the patch, ordinary coin inputs were handled by the UTXO prune branch, but the supplied diff shows data coin variants were not included there. A data coin spend could therefore complete without the corresponding data coin UTXO being consumed in storage. After the patch, signed and predicate data coin inputs flow through the same prune path as ordinary coins, and the regression test expects a second transaction spending the same data coin to be skipped after the first spend is committed.

# Root Cause

The executor's UTXO spend-state update path omitted `Input::DataCoinSigned` and `Input::DataCoinPredicate` from the branch that removes spent UTXOs from storage. The evidence supports a missing state-consumption case, not an authorization, signature, decoding, or panic issue.

## Walkthrough

1. A transaction spends a data coin input accepted by the executor.

2. Before the fix, `spend_input_utxos` matched ordinary coin inputs for UTXO pruning but did not include data coin input variants in that branch.

3. Because the data coin variants missed the prune path, the spent data coin UTXO could remain available in storage after execution changes were applied.

4. The regression test now commits the first transaction's changes before attempting another transaction using the same data coin.

5. After the fix, data coin inputs are pruned through the same UTXO consumption logic as ordinary coin inputs.

6. The second spend attempt is expected to be skipped, demonstrating enforcement of the no-double-spend state transition.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/services/executor/src/executor.rs | 2048 | Executor UTXO spending path; iterates transaction inputs and removes spent UTXOs from storage. |
| crates/services/executor/src/executor.rs | 2071 | Adds `Input::DataCoinSigned` and `Input::DataCoinPredicate` to the spend/prune handling previously covering ordinary coin inputs. |
| crates/fuel-core/src/executor.rs | 4267 | Regression setup commits the first data coin spend so later validation observes updated state. |
| crates/fuel-core/src/executor.rs | 4302 | Regression assertion expects the attempted second spend to be skipped. |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/executor.rs:4073` (changes an authorization or privilege gate)

Before
```rust
block_2_header.consensus.height = 1u32.into();

        let (
            ExecutionResult {
                block,
                skipped_transactions,
                ..
```
After
```rust
block_2_header.consensus.height = 1u32.into();

        let ExecutionResult {
            skipped_transactions,
            ..
        } = producer
            .produce_without_commit_with_source_direct_resolve(Components {
                header_to_produce: block_2_header,
```

## Snippet 2

Context: `crates/fuel-core/src/executor.rs:4267` (changes a consensus- or validator-sensitive branch)

Before
```rust
changes,
        ): (ExecutionResult, Changes) = producer
            .produce_without_commit_with_source_direct_resolve(Components {
                header_to_produce: block_2_header,
```
After
```rust
changes,
        ): (ExecutionResult, Changes) = producer
            .produce_without_commit_with_source_direct_resolve(Components {
                header_to_produce: PartialBlockHeader::default(),
                transactions_source: OnceTransactionsSource::new(vec![tx_1.into()]),
                coinbase_recipient: Default::default(),
                gas_price: 1,
            })
```

## Snippet 3

Context: `crates/services/executor/src/executor.rs:2071` (changes an authorization or privilege gate)

Before
```rust
asset_id,
                    ..
                }) => {
                    // prune utxo from db
```
After
```rust
asset_id,
                    ..
                })
                | Input::DataCoinSigned(DataCoinSigned {
                    utxo_id,
                    owner,
                    amount,
                    asset_id,
```

## Snippet 4

Context: `crates/fuel-core/src/executor.rs:4302` (changes the branch that decides whether execution stops or continues)

Before
```rust
})
            .unwrap()
            .into();

        // then
        assert!(skipped_transactions.is_empty());
    }
```
After
```rust
})
            .unwrap()
            .into_result();

        // then
        assert_eq!(skipped_transactions.len(), 1);
    }
```

# Fix Pattern

Extend centralized UTXO spend/prune handling to include all input variants that represent spendable UTXO state.

## How It Was Fixed

`crates/services/executor/src/executor.rs` was updated so `Input::DataCoinSigned` and `Input::DataCoinPredicate` share the existing prune branch with `Input::CoinSigned` and `Input::CoinPredicate`. The test in `crates/fuel-core/src/executor.rs` was adjusted to commit the first spend and then verify that a second spend of the same data coin is skipped.

# Why It Matters

1. Prevents a spent data coin UTXO from remaining available in executor storage.

2. Maintains the core no-double-spend invariant for data coin inputs.

3. Keeps data coin spend behavior consistent with ordinary coin spend behavior.

4. Evidence does not establish remote exploitability or deployed-network impact.

# Evidence Notes

The strongest evidence is the implementation hunk in `crates/services/executor/src/executor.rs` around `spend_input_utxos`, where data coin variants are added to the UTXO prune branch. Supporting evidence is the regression flow in `crates/fuel-core/src/executor.rs`, which commits the first spend and then asserts that a second spend attempt appears in `skipped_transactions`. Claims about panic behavior, malformed decoding, signature bypass, or consensus divergence are unsupported by the provided evidence. Protocol security invariant: Every accepted UTXO-style input, including data coin inputs, must be consumed or pruned from executor storage so the same UTXO cannot remain available for a later transaction after it has been spent. Verification notes: The patch evidence does not prove remote exploitability or an end-to-end network attack path. The patch evidence does not show whether consensus divergence occurred in deployed networks. The patch evidence does not prove ordinary coin inputs were affected. The patch evidence does not show bypass of signature or predicate authorization checks; the issue is mapped to spend-state persistence. Confirmed from supplied diff snippets only; no external files or commands were used. The finding is grounded in executor storage state consumption, not input authorization. The test evidence supports the before/after double-spend prevention behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `missing-utxo-consumption`
Final impact type: `double-spend, state-integrity`
Final tags: `blockchain-core, executor, storage, utxo, data-coin, double-spend, state-consumption`

The supplied patch evidence supports a security fix: data coin input variants were added to the executor path that prunes spent UTXOs, and the regression test now expects a second spend of the same committed data coin to be skipped. The original liveness framing is misleading; the supported issue is a spend-state integrity bug affecting the no-double-spend invariant.

## Security Evidence

1. Implementation adds Input::DataCoinSigned and Input::DataCoinPredicate to the existing UTXO prune branch in spend_input_utxos.
2. Regression flow commits the first data coin spend before attempting a second transaction using the same data coin.
3. Post-fix assertion expects one skipped transaction for the second spend attempt.
4. The changed path is executor storage state handling for spendable inputs in a blockchain core component.

## Missing Evidence

1. No evidence of remote exploit steps or deployed-network exploitation.
2. No evidence of consensus divergence across nodes.
3. No evidence of signature, predicate, or authorization bypass beyond spend-state persistence.
4. No quantified asset loss or chain impact is shown.

## Claim Boundaries

1. Validate as a double-spend prevention fix for data coin UTXO state consumption.
2. Do not classify as a liveness failure based on the supplied patch.
3. Do not claim malformed input handling, panic prevention, or authentication bypass.
4. Do not extend the issue to ordinary coin inputs, which appear to already use the prune path.
