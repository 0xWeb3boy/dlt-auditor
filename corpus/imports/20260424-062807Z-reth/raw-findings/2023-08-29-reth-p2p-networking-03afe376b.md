---
case_id: case_20230829_03afe376b
project: reth
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: high
date: 2023-08-29
source_refs:
  - git:03afe376b85cb424270a48eb3e5a97db8c5f2af4
  - "crates/transaction-pool/src/pool/mod.rs:517"
  - "crates/transaction-pool/src/pool/mod.rs:749"
  - "crates/transaction-pool/src/pool/mod.rs:891"
  - "crates/transaction-pool/src/pool/mod.rs:775"
bug_class: listener-filter-bypass
impact_type:
  - policy-bypass
confidence: medium
tags:
  - blockchain-core
  - transaction-pool
  - p2p-networking
  - event-listeners
  - propagation-policy
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a txpool listener-filtering bug: the full transaction stream previously attempted to send every new transaction event to every listener, and the patch adds a guard so `PropagateOnly` listeners do not receive events for non-propagable transactions. That is a real behavior fix, but the supplied evidence does not establish a concrete security vulnerability or end-to-end exposure.

## Observed Patch Facts

1. In `crates/transaction-pool/src/pool/mod.rs`, the patch replaces `transaction_listeners.retain_mut(|listener| match listener.try_send(event.clone()) {` with `transaction_listeners.retain_mut(|listener| {`.

2. In `crates/transaction-pool/src/pool/mod.rs`, the patch replaces `kind: PendingTransactionListenerKind,` with `kind: TransactionListenerKind,`.

3. In `crates/transaction-pool/src/pool/mod.rs`, the patch replaces `/// [PendingTransactionListenerKind].` with `/// [TransactionListenerKind].`.

4. In `crates/transaction-pool/src/pool/mod.rs`, the patch replaces `/// [PendingTransactionListenerKind].` with `/// [TransactionListenerKind].`.

## Project Context

The changed code sits primarily in `crates/transaction-pool/src/pool`, `crates/transaction-pool/src`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `crates/transaction-pool/src/pool/listener.rs`, `crates/transaction-pool/src/pool/txpool.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/transaction-pool/src/traits.rs`, `crates/transaction-pool/src/noop.rs`. The strongest project-level identifiers around this patch are `kind`, `transactions`, `that`, and `only`.

## Before/After Behavior

Before the patch, `on_new_transaction` called `try_send(event.clone())` for each listener without first checking `listener.kind` against `event.transaction.propagate`. After the patch, it skips delivery when the listener is `PropagateOnly` and the transaction is marked non-propagable, while retaining the listener if its channel is still open. Related APIs and comments were aligned to `TransactionListenerKind` and explicitly describe `PropagateOnly` as including only propagatable transactions.

# Root Cause

A missing filter at the full transaction event fan-out point allowed the full-stream path to ignore listener-kind propagation restrictions that were already described elsewhere in the subsystem.

## Walkthrough

1. At `crates/transaction-pool/src/pool/mod.rs:517`, the old code iterated listeners and directly attempted `try_send(event.clone())` for each one.

2. The patch wraps that send path in a new conditional: if the listener is `PropagateOnly` and the transaction has `propagate = false`, the event is not sent.

3. The added comment ties this branch to listeners that are only supposed to receive propagatable transactions, including network-style consumers.

4. At `crates/transaction-pool/src/pool/mod.rs:749`, listener metadata uses `TransactionListenerKind`, the type consulted by the new guard.

5. At `crates/transaction-pool/src/pool/mod.rs:775` and `:891`, iterator helpers and comments say `PropagateOnly` returns only transactions allowed to be propagated, reinforcing the intended rule.

6. Taken together, the patch brings the full transaction stream into line with the documented filtering semantics used by related txpool notification paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/transaction-pool/src/pool/mod.rs | 517 | Enforces the propagate gate before sending full transaction events to listeners, preventing `PropagateOnly` subscribers from receiving non-propagable transactions. |
| crates/transaction-pool/src/pool/mod.rs | 749 | Stores listener kind metadata used to distinguish propagation-restricted subscribers from broader listeners. |
| crates/transaction-pool/src/pool/mod.rs | 775 | Pending-transaction iterator API documents and applies listener-kind-based filtering for promoted transactions. |
| crates/transaction-pool/src/pool/mod.rs | 891 | Canonical-state outcome iterator API documents and applies the same listener-kind-based propagation filter. |

## Code Snippets

## Snippet 1

Context: `crates/transaction-pool/src/pool/mod.rs:517` (changes a sensitive control or state-update path)

Before
```rust
fn on_new_transaction(&self, event: NewTransactionEvent<T::Transaction>) {
        let mut transaction_listeners = self.transaction_listener.lock();

        transaction_listeners.retain_mut(|listener| match listener.try_send(event.clone()) {
            Ok(()) => true,
            Err(err) => {
                if matches!(err, mpsc::error::TrySendError::Full(_)) {
                    debug!(
```
After
```rust
fn on_new_transaction(&self, event: NewTransactionEvent<T::Transaction>) {
        let mut transaction_listeners = self.transaction_listener.lock();
        transaction_listeners.retain_mut(|listener| {
            if listener.kind.is_propagate_only() && !event.transaction.propagate {
                // only emit this hash to listeners that are only allowed to receive propagate only
                // transactions, such as network
                return !listener.sender.is_closed()
            }
```

## Snippet 2

Context: `crates/transaction-pool/src/pool/mod.rs:749` (changes a sensitive control or state-update path)

Before
```rust
sender: mpsc::Sender<TxHash>,
    /// Whether to include transactions that should not be propagated over the network.
    kind: PendingTransactionListenerKind,
}
```
After
```rust
sender: mpsc::Sender<TxHash>,
    /// Whether to include transactions that should not be propagated over the network.
    kind: TransactionListenerKind,
}

/// An active listener for new pending transactions.
#[derive(Debug)]
struct TransactionListener<T: PoolTransaction> {
```

## Snippet 3

Context: `crates/transaction-pool/src/pool/mod.rs:891` (changes a sensitive control or state-update path)

Before
```rust
impl<T: PoolTransaction> OnNewCanonicalStateOutcome<T> {
    /// Returns all transactions that were promoted to the pending pool and adhere to the given
    /// [PendingTransactionListenerKind].
    ///
    /// If the kind is [PendingTransactionListenerKind::PropagateOnly], then only transactions that
    /// are allowed to be propagated are returned.
    pub(crate) fn pending_transactions(
        &self,
```
After
```rust
impl<T: PoolTransaction> OnNewCanonicalStateOutcome<T> {
    /// Returns all transactions that were promoted to the pending pool and adhere to the given
    /// [TransactionListenerKind].
    ///
    /// If the kind is [TransactionListenerKind::PropagateOnly], then only transactions that
    /// are allowed to be propagated are returned.
    pub(crate) fn pending_transactions(
        &self,
```

## Snippet 4

Context: `crates/transaction-pool/src/pool/mod.rs:775` (changes a sensitive control or state-update path)

Before
```rust
impl<T: PoolTransaction> AddedPendingTransaction<T> {
    /// Returns all transactions that were promoted to the pending pool and adhere to the given
    /// [PendingTransactionListenerKind].
    ///
    /// If the kind is [PendingTransactionListenerKind::PropagateOnly], then only transactions that
    /// are allowed to be propagated are returned.
    pub(crate) fn pending_transactions(
        &self,
```
After
```rust
impl<T: PoolTransaction> AddedPendingTransaction<T> {
    /// Returns all transactions that were promoted to the pending pool and adhere to the given
    /// [TransactionListenerKind].
    ///
    /// If the kind is [TransactionListenerKind::PropagateOnly], then only transactions that
    /// are allowed to be propagated are returned.
    pub(crate) fn pending_transactions(
        &self,
```

# Fix Pattern

Add an explicit eligibility check at event dispatch time so restricted listeners do not receive events outside their declared scope, then align related types and API documentation to the same rule.

## How It Was Fixed

The fix inserts a pre-send guard in `on_new_transaction` that suppresses delivery of non-propagable transactions to `PropagateOnly` listeners. The patch also standardizes related listener and iterator interfaces on `TransactionListenerKind` and updates comments to state the same propagate-only filtering semantics across paths.

# Why It Matters

1. It removes a concrete mismatch between documented listener semantics and actual full-stream behavior.

2. It reduces the chance that network-oriented or otherwise restricted listeners observe transactions they were not supposed to receive.

3. The available diff does not prove remote exploitability, broadcast to peers, or broader protocol compromise.

# Evidence Notes

The strongest evidence is the added branch in `crates/transaction-pool/src/pool/mod.rs:517` checking `listener.kind.is_propagate_only()` together with `!event.transaction.propagate` before sending. Supporting hunks at `:749`, `:775`, and `:891` show terminology and API alignment to `TransactionListenerKind` and repeat the documented `PropagateOnly` filtering rule. This is enough to support a listener-policy bypass in the full-stream path. It is not enough to prove a security incident, external attacker control, peer broadcast, confidentiality impact, or consensus effect. Protocol security invariant: `PropagateOnly` listeners should not receive transaction events for entries marked `propagate = false`. The diff shows this rule was enforced for related iterator paths and was added to the full transaction event stream in this patch. Verification notes: The patch does not prove that an external attacker could directly trigger or observe the incorrect stream behavior. It is not proven that non-propagable transactions were actually broadcast to remote peers, only that network-class listeners could receive them. No consensus failure, signature bypass, or state-corruption impact is shown by this diff. The evidence supports a propagation-policy enforcement fix, not a demonstrated end-to-end exploit. No test diff was provided, so regression coverage cannot be evaluated beyond the fact that a test file was touched in the commit metadata. The evidence supports a behavioral fix in listener filtering, but not a confirmed security exploit chain. Security classification is therefore downgraded to `unclear` and excluded from the security corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `listener-filter-bypass`
Final impact type: `policy-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-pool, p2p-networking, event-listeners, propagation-policy`

The patch shows a concrete enforcement gap in a security-sensitive path: the full transaction event stream previously delivered all events to all listeners, and the fix adds an explicit guard so `PropagateOnly` listeners do not receive transactions marked `propagate = false`. Because the code comment ties these listeners to network-style consumers, the change clearly tightens propagation-policy handling and removes an exposed risky condition. However, the supplied evidence does not prove an end-to-end exploit, actual external broadcast, or broader integrity impact, so this is better classified as security hardening rather than a confirmed security vulnerability fix.

## Security Evidence

1. `on_new_transaction` now checks `listener.kind.is_propagate_only()` together with `!event.transaction.propagate` before sending.
2. The added comment explicitly says these restricted listeners include network-style consumers.
3. Related APIs and iterator helpers were aligned to `TransactionListenerKind` and document that `PropagateOnly` should return only propagatable transactions.
4. The fix addresses a mismatch between documented propagation restrictions and actual event fan-out behavior.

## Missing Evidence

1. No proof that non-propagable transactions were actually broadcast to remote peers.
2. No proof of attacker control over the affected listener path or a practical exploit chain.
3. No evidence of confidentiality breach, consensus failure, or state corruption from this bug.
4. No test diff is provided to show the exact failure mode or externally observable impact.

## Claim Boundaries

1. The patch supports a listener-policy enforcement flaw in the full transaction stream.
2. The patch supports security-hardening because it tightens handling of non-propagable transactions for restricted listeners.
3. The patch does not support the original `state-corruption` classification.
4. The patch does not prove a concrete exploitable security bug, remote compromise, or protocol-integrity failure.
