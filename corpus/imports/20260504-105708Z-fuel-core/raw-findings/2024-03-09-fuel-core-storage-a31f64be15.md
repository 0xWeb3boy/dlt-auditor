---
case_id: case_20240309_a31f64be15
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2024-03-09
source_refs:
  - git:a31f64be154dedeb4dbd5e5f3dbeb0adf59ef297
  - "crates/services/txpool/src/txpool.rs:402"
  - "crates/services/txpool/src/txpool/tests.rs:95"
  - "crates/services/txpool/src/txpool.rs:262"
  - "crates/services/txpool/src/txpool.rs:281"
bug_class: txpool-blacklist-enforcement
impact_type:
  - mempool-policy-enforcement
confidence: medium
tags:
  - blockchain-core
  - txpool
  - blacklist
  - mempool-policy
  - transaction-admission
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds TxPool blacklist checking for coin-input UTXO ids and updates insertion error reporting. The evidence supports a node-local mempool policy enforcement change, but it does not prove a vulnerability, consensus impact, remote exploitability, privilege escalation, or state corruption.

## Observed Patch Facts

1. In `crates/services/txpool/src/txpool.rs`, the patch adds `fn check_blacklisting(&self, tx: &PoolTransaction) -> anyhow::Result<()> {`.

2. In `crates/services/txpool/src/txpool/tests.rs`, the patch replaces `async fn insert_simple_tx_dependency_chain_succeeds() {` with `async fn insert_simple_tx_with_blacklisted_utxo_id_fails() {`.

3. In `crates/services/txpool/src/txpool.rs`, the patch replaces `res.push(self.insert_inner(tx));` with `let tx_id = tx.id();`.

4. In `crates/services/txpool/src/txpool.rs`, the patch replaces `Err(_) => {` with `Err(err) => {`.

## Project Context

The changed code sits primarily in `crates/services/txpool/src`, `crates/services/txpool`, `crates/services/txpool/src/txpool`, which anchors the finding in the `storage` area of the project. Historical context from `crates/services/txpool/src/service.rs`, `crates/services/txpool/src/ports.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/services/txpool/src/containers/dependency.rs`, `crates/services/txpool/src/service.rs`. The strongest project-level identifiers around this patch are `tokio::test`, `result`, `anyhow::Result`, and `Input::CoinSigned`. Nearby tests or test-like files include `crates/services/txpool/src/service/update_sender/tests/test_sending.rs`, `crates/services/txpool/src/service/update_sender/tests/test_permits.rs`.

## Before/After Behavior

Before the patch, the provided TxPool snippet does not show blacklist checks during insertion, and insertion errors were not reported to subscribers. After the patch, TxPool has a `check_blacklisting` helper that scans transaction inputs and returns an error when a signed or predicate coin input references a blacklisted UTXO id. The insertion loop now captures the transaction id and sends a squeezed-out status on insertion failure.

# Root Cause

The grounded root cause is missing or newly added TxPool admission handling for configured blacklist entries on coin-input UTXO ids. It is not established that this was a security bug rather than a new policy feature or hardening change.

## Walkthrough

1. A checked transaction is passed into the TxPool insertion path.

2. The patch adds a helper that iterates over `PoolTransaction` inputs.

3. For `Input::CoinSigned` and `Input::CoinPredicate`, the helper checks whether the input UTXO id is present in `self.config.blacklist`.

4. If the UTXO id is blacklisted, insertion can fail with an error indicating the UTXO is blacklisted.

5. A regression test covers rejection of a simple transaction using a blacklisted UTXO id.

6. The insertion loop now reports failed insertions as squeezed-out status updates using the captured transaction id.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/services/txpool/src/txpool.rs | 402 | Adds blacklist validation over `PoolTransaction` inputs before TxPool acceptance. |
| crates/services/txpool/src/txpool.rs | 254 | Runs insertion through `insert_inner` per transaction and captures the transaction id for status reporting. |
| crates/services/txpool/src/txpool.rs | 281 | Reports failed insertions as squeezed-out transaction status errors. |
| crates/services/txpool/src/txpool/tests.rs | 95 | Regression coverage that a transaction using a blacklisted UTXO is rejected. |

## Code Snippets

## Snippet 1

Context: `crates/services/txpool/src/txpool.rs:402` (changes an authorization or privilege gate)

Before
```rust
result
    }
}
```
After
```rust
result
    }

    fn check_blacklisting(&self, tx: &PoolTransaction) -> anyhow::Result<()> {
        for input in tx.inputs() {
            match input {
                Input::CoinSigned(CoinSigned { utxo_id, owner, .. })
                | Input::CoinPredicate(CoinPredicate { utxo_id, owner, .. }) => {
```

## Snippet 2

Context: `crates/services/txpool/src/txpool/tests.rs:95` (changes an authorization or privilege gate)

Before
```rust
}

#[tokio::test]
async fn insert_simple_tx_dependency_chain_succeeds() {
```
After
```rust
}

#[tokio::test]
async fn insert_simple_tx_with_blacklisted_utxo_id_fails() {
    let mut rng = StdRng::seed_from_u64(0);
    let db = MockDb::default();
    let mut txpool = TxPool::new(Default::default(), db.clone());
```

## Snippet 3

Context: `crates/services/txpool/src/txpool.rs:262` (changes a sensitive control or state-update path)

Before
```rust
for tx in txs.into_iter() {
            res.push(self.insert_inner(tx));
        }

        // announce to subscribers
        for ret in res.iter() {
            match ret {
```
After
```rust
for tx in txs.into_iter() {
            let tx_id = tx.id();
            let result = self.insert_inner(tx);

            match &result {
                Ok(InsertionResult {
                    removed,
```

## Snippet 4

Context: `crates/services/txpool/src/txpool.rs:281` (changes a sensitive control or state-update path)

Before
```rust
);
                }
                Err(_) => {
                    // @dev should not broadcast tx if error occurred
                }
            }
        }
        res
```
After
```rust
);
                }
                Err(err) => {
                    tx_status_sender
                        .send_squeezed_out(tx_id, Error::SqueezedOut(err.to_string()));
                }
            }
```

# Fix Pattern

Add explicit admission-time policy validation and propagate rejection errors to transaction status subscribers.

## How It Was Fixed

The patch added `check_blacklisting` in `crates/services/txpool/src/txpool.rs`, checking signed and predicate coin inputs against `self.config.blacklist.contains_coin(utxo_id)`. It added a regression test for blacklisted UTXO rejection and adjusted insertion handling so failures are reported with `send_squeezed_out`.

# Why It Matters

1. Prevents configured blacklisted UTXO ids from being accepted through the shown TxPool path.

2. Improves caller or subscriber visibility into rejected insertions.

3. Evidence does not show a protocol-level vulnerability or exploit path.

# Evidence Notes

Primary support comes from `txpool.rs` adding `check_blacklisting`, `txpool/tests.rs` adding `insert_simple_tx_with_blacklisted_utxo_id_fails`, and insertion-loop changes that report errors. Claims about consensus failure, block inclusion, privilege escalation, state corruption, or remote exploitability are unsupported by the supplied evidence. The evidence also does not prove behavior for all input kinds or owner-based blacklist enforcement beyond the visible UTXO-id check. Protocol security invariant: If a node is configured with a TxPool blacklist, TxPool admission should reject transactions whose coin inputs match that blacklist. The supplied evidence shows UTXO-id checks for signed and predicate coin inputs, but does not establish that this was an existing protocol security invariant or that the prior behavior enabled a concrete vulnerability. Verification notes: The patch does not prove a consensus vulnerability. The patch does not prove accepted blacklisted transactions could be included in blocks. The patch does not prove remote exploitability or privilege escalation. The patch does not prove state corruption; the observed invariant is TxPool admission policy. The evidence only directly shows UTXO blacklist enforcement for signed and predicate coin inputs. No external verification was performed because only the provided input may be used. Security relevance remains unclear from the patch evidence alone. Do not keep in a vulnerability-fix corpus without additional evidence that the prior behavior violated an existing security requirement. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `txpool-blacklist-enforcement`
Final impact type: `mempool-policy-enforcement`
Final confidence: `medium`
Final tags: `blockchain-core, txpool, blacklist, mempool-policy, transaction-admission`

The supplied patch evidence supports a security-hardening classification, not a concrete security-fix. The code adds TxPool admission-time rejection for transactions whose signed or predicate coin inputs reference configured blacklisted UTXO ids, with regression coverage. That is a security-sensitive policy enforcement change, but the evidence does not prove prior exploitability, consensus impact, state corruption, or a vulnerability being fixed.

## Security Evidence

1. Adds check_blacklisting over PoolTransaction inputs during TxPool handling.
2. Rejects Input::CoinSigned and Input::CoinPredicate when config.blacklist contains the input UTXO id.
3. Adds a test named insert_simple_tx_with_blacklisted_utxo_id_fails.
4. Insertion errors are now propagated to transaction status subscribers as squeezed-out errors.

## Missing Evidence

1. No evidence that prior behavior allowed consensus-invalid block production or state corruption.
2. No evidence that blacklisted transactions could bypass a required protocol security invariant.
3. No evidence of remote exploitability, privilege escalation, or fund loss.
4. No evidence that blacklist enforcement applies beyond the shown coin signed and coin predicate UTXO-id checks.

## Claim Boundaries

1. Classify as TxPool/mempool blacklist hardening, not storage state corruption.
2. Do not claim a consensus-layer vulnerability from the supplied patch alone.
3. Do not claim a concrete exploit path or security incident.
4. The supported behavior is configured blacklist enforcement during transaction admission.
