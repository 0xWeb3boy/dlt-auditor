---
case_id: case_20260227_48d0a9bce8
project: sui
domain: blockchain-core
render_mode: heuristic
context_depth: deep
phase3_security_verdict: not-reviewed
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-02-27
source_refs:
  - git:48d0a9bce8d79caea13a8e6e899c5c538c32e18b
  - "crates/sui-core/src/authority.rs:2423"
  - "crates/sui-core/src/authority.rs:2458"
  - "crates/sui-core/src/authority.rs:985"
  - "crates/sui-core/src/authority.rs:2494"
bug_class: malformed-transaction-panic
impact_type:
  - availability
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - fullnode
  - simulation
  - denial-of-service
  - panic
  - input-validation
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Consolidate tx checking in signing and simulate (#25624) appears to strengthen state integrity in the transaction-processing path of sui. The strongest evidence spans `crates/sui-core/src/authority.rs` and `crates/sui-core/src/authority.rs`. The affected state likely includes `transaction`, `Object::new_move`, and `MoveObject::new_gas_coin`. The selected hunks suggest persisted or derived state could previously become inconsistent with the live runtime state. Additional project context from `crates/sui-core/src/transaction_signing_filter.rs`, `crates/sui-core/src/transaction_outputs.rs` was used to anchor the surrounding module behavior. Commit context: ## Description `simulate_transaction` duplicated validation logic from the signing path but had diverged: it called `process_funds_withdrawals_for_execution` (which uses `.unwrap()`) instead of the safe `process_funds_withdrawals_for_signing` (which returns `Result`), meaning a malformed transaction could panic a fullnode during simulation. This extracts the shared pre-object-load validation — deny checks, funds withdrawal parsing, and balance availability checks — into `pre_object_load_checks`, called by both `handle_transaction_deny_checks` and `simulate_transaction`, fixing the panic and ensuring the two paths stay in sync. ## Test plan - `cargo check -p sui-core` — compiles cleanly - `SUI_SKIP_SIMTESTS=1 cargo nextest run -p sui-core` — all tests pass - `cargo xclippy` — no warnings --- ## Release notes Check each box that your changes affect. If none of the boxes relate to your changes, release notes aren't required. For each box you select, include information after the relevant heading that describes the impact of your changes that a user might notice and any actions they must take to implement updates. - [ ] Protocol: - [x] Nodes (Validators and Full nodes): Fixes a potential fullnode panic when simulating a malformed transaction with invalid funds withdrawals. - [ ] gRPC: - [ ] JSON-RPC: - [ ] GraphQL: - [ ] CLI: - [ ] Rust SDK: - [ ] Indexing Framework:.

## Observed Patch Facts

1. In `crates/sui-core/src/authority.rs`, the patch replaces `sui_transaction_checks::deny::check_transaction_for_signing(` with `// Create and inject mock gas coin before pre_object_load_checks so that`.

2. In `crates/sui-core/src/authority.rs`, the patch replaces `// mock a gas object if one was not provided` with `// Add mock gas to input objects after loading (it doesn't exist in the store).`.

3. In `crates/sui-core/src/authority.rs`, the patch replaces `fn handle_transaction_deny_checks(` with `/// Runs deny list checks and processes funds withdrawals. Called before loading input`.

4. In `crates/sui-core/src/authority.rs`, the patch replaces `let declared_withdrawals =` with `let (kind, signer, gas_data) = transaction.execution_parts();`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-core/src/transaction_signing_filter.rs`, `crates/sui-core/src/transaction_outputs.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/rpc_index.rs`, `crates/sui-core/src/jsonrpc_index.rs`. The strongest project-level identifiers around this patch are `transaction`, `Object::new_move`, `MoveObject::new_gas_coin`, and `ObjectID::MAX`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/authority_tests.rs`, `crates/sui-core/src/unit_tests/transaction_tests.rs`.

## Before/After Behavior

1. Before the patch, `crates/sui-core/src/authority.rs` relied on `sui_transaction_checks::deny::check_transaction_for_signing(`. After the patch, it instead uses `// Create and inject mock gas coin before pre_object_load_checks so that`.

2. Before the patch, `crates/sui-core/src/authority.rs` relied on `// mock a gas object if one was not provided`. After the patch, it instead uses `// Add mock gas to input objects after loading (it doesn't exist in the store).`.

3. Before the patch, `crates/sui-core/src/authority.rs` relied on `fn handle_transaction_deny_checks(`. After the patch, it instead uses `/// Runs deny list checks and processes funds withdrawals. Called before loading input`.

4. In deep mode, the generator also traced related identifiers into `crates/sui-core/src/rpc_index.rs`, `crates/sui-core/src/jsonrpc_index.rs` to verify how the changed path fits into the wider subsystem behavior.

# Root Cause

The issue appears to sit at the boundary between `crates/sui-core/src/authority.rs` and `crates/sui-core/src/authority.rs`. The likely root cause was inconsistent state mutation across related storage or accounting paths.

## Walkthrough

1. In `crates/sui-core/src/authority.rs:2423`, the selected hunk changes an authorization or privilege gate. Notable identifiers in this step include `sui_transaction_checks::deny::check_transaction_for_signing`, `Object::new_move`, and `MoveObject::new_gas_coin`. The hunk matched touches a critical implementation path, diff changes access control or privilege checks.

2. In `crates/sui-core/src/authority.rs:2458`, the selected hunk changes an authorization or privilege gate. Notable identifiers in this step include `Object::new_move`, `MoveObject::new_gas_coin`, and `ObjectID::MAX`. The hunk matched touches a critical implementation path, diff changes access control or privilege checks.

3. In `crates/sui-core/src/authority.rs:985`, the selected hunk changes a consensus- or validator-sensitive branch. Notable identifiers in this step include `transaction`, `checks`, and `tx_data`. The hunk matched touches a critical implementation path, diff changes consensus or validator logic.

4. In `crates/sui-core/src/authority.rs:2494`, the selected hunk changes a consensus- or validator-sensitive branch. Notable identifiers in this step include `declared_withdrawals`, `transaction`, and `expect`. The hunk matched touches a critical implementation path, diff changes consensus or validator logic. Taken together, the hunks suggest the fix spans more than one control path rather than a single isolated check.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority.rs | 2423 | changes an authorization or privilege gate |
| crates/sui-core/src/authority.rs | 2458 | changes an authorization or privilege gate |
| crates/sui-core/src/authority.rs | 985 | changes a consensus- or validator-sensitive branch |
| crates/sui-core/src/authority.rs | 2494 | changes a consensus- or validator-sensitive branch |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/authority.rs:2423` (changes an authorization or privilege gate)

Before
```rust
let receiving_object_refs = transaction.receiving_objects();

        sui_transaction_checks::deny::check_transaction_for_signing(
            &transaction,
            &[],
            &input_object_kinds,
            &receiving_object_refs,
            &self.config.transaction_deny_config,
```
After
```rust
let receiving_object_refs = transaction.receiving_objects();

        // Create and inject mock gas coin before pre_object_load_checks so that
        // funds withdrawal processing sees non-empty payment and doesn't incorrectly
        // create an address balance withdrawal for gas.
        let mock_gas_object = if allow_mock_gas_coin && transaction.gas().is_empty() {
            let obj = Object::new_move(
                MoveObject::new_gas_coin(
```

## Snippet 2

Context: `crates/sui-core/src/authority.rs:2458` (changes an authorization or privilege gate)

Before
```rust
)?;

        // mock a gas object if one was not provided
        let mock_gas_id = if allow_mock_gas_coin && transaction.gas().is_empty() {
            let mock_gas_object = Object::new_move(
                MoveObject::new_gas_coin(
                    OBJECT_START_VERSION,
                    ObjectID::MAX,
```
After
```rust
)?;

        // Add mock gas to input objects after loading (it doesn't exist in the store).
        let mock_gas_id = mock_gas_object.map(|obj| {
            let id = obj.id();
            input_objects.push(ObjectReadResult::new_from_gas_object(&obj));
            id
        });
```

## Snippet 3

Context: `crates/sui-core/src/authority.rs:985` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    fn handle_transaction_deny_checks(
        &self,
        transaction: &VerifiedTransaction,
        epoch_store: &Arc<AuthorityPerEpochStore>,
    ) -> SuiResult<CheckedInputObjects> {
        let tx_digest = transaction.digest();
```
After
```rust
}

    /// Runs deny list checks and processes funds withdrawals. Called before loading input
    /// objects, since these checks don't depend on object state.
    fn pre_object_load_checks(
        &self,
        tx_data: &TransactionData,
        tx_signatures: &[GenericSignature],
```

## Snippet 4

Context: `crates/sui-core/src/authority.rs:2494` (changes a consensus- or validator-sensitive branch)

Before
```rust
.expect("Creating an executor should not fail here");

        let declared_withdrawals =
            transaction.process_funds_withdrawals_for_execution(epoch_store.get_chain_identifier());
        let address_funds: BTreeSet<_> = declared_withdrawals.keys().cloned().collect();

        self.execution_cache_trait_pointers
            .account_funds_read
```
After
```rust
.expect("Creating an executor should not fail here");

        let (kind, signer, gas_data) = transaction.execution_parts();
        let early_execution_error = get_early_execution_error(
```

# Fix Pattern

The fix pattern is to tighten the sensitive transaction-processing control path so the key invariant is enforced before downstream work continues.

## How It Was Fixed

The patch appears to tighten the critical transaction-processing path so the relevant invariant is enforced before downstream work continues.

# Why It Matters

1. The selected hunks affect a sensitive transaction-processing path, so even a small invariant mistake can have wider operational consequences.

2. The exact exploitability is not fully explicit from the patch alone, but the control path is important enough to justify follow-up review.

# Evidence Notes

This finding is grounded in `crates/sui-core/src/authority.rs`, `crates/sui-core/src/authority.rs`, `crates/sui-core/src/authority.rs`, `crates/sui-core/src/authority.rs`. The selected hunks were prioritized because they matched: touches a critical implementation path, diff changes access control or privilege checks, diff changes consensus or validator logic. Nearby test changes increase confidence that the patch targeted a real behavior change. Phase 3 also reviewed nearby historical project context from `crates/sui-core/src/transaction_signing_filter.rs`, `crates/sui-core/src/transaction_outputs.rs`. Agent-backed phase 3 failed and the report fell back to heuristic rendering: agent did not return a JSON object.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `malformed-transaction-panic`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, fullnode, simulation, denial-of-service, panic, input-validation`

The evidence supports a security-relevant availability fix, not the original state-corruption/state-integrity framing. The commit explicitly describes malformed transaction simulation reaching a funds-withdrawal execution path that can unwrap and panic a fullnode, and the patch removes that simulation-local processing in favor of shared pre-object-load validation that returns errors. This is best kept as a likely fullnode denial-of-service fix, with conservative confidence because the supplied patch does not fully show the unwrap implementation or external API exposure path.

## Security Evidence

1. Commit states malformed transaction simulation could panic a fullnode due to `process_funds_withdrawals_for_execution` using `.unwrap()`.
2. Patch removes the direct `process_funds_withdrawals_for_execution` call from `simulate_transaction`.
3. New shared `pre_object_load_checks` runs deny checks, funds withdrawal parsing, and balance availability checks before object loading.
4. Release notes explicitly describe fixing a potential fullnode panic when simulating malformed transactions with invalid funds withdrawals.

## Missing Evidence

1. The supplied hunks do not show the exact `.unwrap()` inside `process_funds_withdrawals_for_execution`.
2. The supplied evidence does not prove whether unauthenticated remote callers can trigger `simulate_transaction`.
3. No regression test excerpt is included showing the malformed transaction no longer panics.

## Claim Boundaries

1. This should not be classified as state corruption or state-integrity impact based on the provided evidence.
2. The supported impact is fullnode availability via panic prevention during transaction simulation.
3. Do not claim consensus compromise, fund loss, authorization bypass, or signature validation failure from this patch alone.
