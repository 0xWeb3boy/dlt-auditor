---
case_id: case_20230803_3f63a0887
project: reth
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-08-03
source_refs:
  - git:3f63a0887a2f52b2fc7541a3e4903ace94c2da91
  - "crates/transaction-pool/src/pool/mod.rs:392"
  - "crates/transaction-pool/src/pool/mod.rs:623"
  - "crates/transaction-pool/src/pool/mod.rs:635"
  - "crates/transaction-pool/src/pool/mod.rs:323"
bug_class: policy-enforcement
impact_type:
  - network-policy-bypass
confidence: medium
tags:
  - blockchain-core
  - transaction-pool
  - propagation-policy
  - network-facing
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence shows a real policy-data-flow fix in the transaction pool: the pending-listener notification path stopped accepting only a transaction hash and now receives the full `AddedTransaction`, from which it derives `propagate_allowed`. That supports a narrow conclusion that the old API dropped propagation-policy context before listener notification. However, the provided snippets do not show the full post-patch filtering logic or demonstrate that a network-facing listener actually leaked non-propagatable transactions, so the security thesis should be treated as unproven from this evidence alone.

## Observed Patch Facts

1. In `crates/transaction-pool/src/pool/mod.rs`, the patch replaces `fn on_new_pending_transaction(&self, ready: &TxHash) {` with `fn on_new_pending_transaction(&self, pending: &AddedTransaction<T::Transaction>) {`.

2. In `crates/transaction-pool/src/pool/mod.rs`, the patch replaces `/// Returns the hash of the transaction if it's pending` with `/// Returns whether the transaction is pending`.

3. In `crates/transaction-pool/src/pool/mod.rs`, the patch replaces `/// Converts this type into the event type for listeners` with `/// Returns if the transaction should be propagated.`.

4. In `crates/transaction-pool/src/pool/mod.rs`, the patch replaces `if let Some(pending_hash) = added.as_pending() {` with `if added.is_pending() {`.

## Project Context

The changed code sits primarily in `crates/transaction-pool/src/pool`, `crates/transaction-pool/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/transaction-pool/src/pool/txpool.rs`, `crates/transaction-pool/src/pool/pending.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/transaction-pool/src/pool/txpool.rs`, `crates/transaction-pool/src/test_utils/pool.rs`. The strongest project-level identifiers around this patch are `transaction`, `AddedTransaction::Pending`, `pending`, and `AddedTransaction`.

## Before/After Behavior

Before the patch, `add_transaction` called `added.as_pending()` and passed only a `TxHash` into `on_new_pending_transaction`, so the notification path had no visible access to the transaction's propagation flag. After the patch, the call site checks `added.is_pending()` and passes `&AddedTransaction` into `on_new_pending_transaction`, which now extracts both the hash and `is_propagate_allowed()`. This clearly preserves more policy context at the listener boundary, but the supplied evidence does not include the rest of the function body to prove how that flag is enforced.

# Root Cause

The notification API collapsed an added pending transaction into a bare hash too early, which removed propagation-policy metadata before the listener handoff. That made the listener path unable, or at least not obviously able, to distinguish transactions that should be propagated from those that should not.

## Walkthrough

1. `add_transaction` constructs a `ValidPoolTransaction` that includes a `propagate` field and receives an `AddedTransaction` result from pool insertion.

2. In the pre-patch code, pending notification used `added.as_pending()` and passed only `&TxHash` into `on_new_pending_transaction`.

3. The pre-patch `on_new_pending_transaction` body shown in evidence only tries to send that hash to listeners, with no policy bit available in its signature.

4. The type `PendingTransactionListener` has a `kind` field documented as controlling inclusion of transactions that should not be propagated, which indicates this boundary is policy-sensitive.

5. The patch changes the call site to pass `&AddedTransaction` instead of only the hash.

6. The patched notification function derives `tx_hash` and `propagate_allowed` from `AddedTransaction`, and `AddedTransaction` gains `is_propagate_allowed()` to expose that flag explicitly.

7. This establishes that the fix preserves propagation-policy context up to the listener-notification boundary, but the provided excerpt stops before showing the actual filtering decision.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/transaction-pool/src/pool/mod.rs | 296 | add-transaction path that decides when to notify pending-transaction listeners |
| crates/transaction-pool/src/pool/mod.rs | 364 | pool-to-listener notification boundary for new pending transactions |
| crates/transaction-pool/src/pool/mod.rs | 581 | listener metadata showing some listeners distinguish whether non-propagatable transactions are included |
| crates/transaction-pool/src/pool/mod.rs | 624 | `AddedTransaction` helpers exposing pending-state and propagation-allowance policy |

## Code Snippets

## Snippet 1

Context: `crates/transaction-pool/src/pool/mod.rs:392` (changes signature or replay validation logic)

Before
```rust
/// Notify all listeners about a new pending transaction.
    fn on_new_pending_transaction(&self, ready: &TxHash) {
        let mut transaction_listeners = self.pending_transaction_listener.lock();
        transaction_listeners.retain_mut(|listener| match listener.try_send(*ready) {
            Ok(()) => true,
            Err(err) => {
                if matches!(err, mpsc::error::TrySendError::Full(_)) {
```
After
```rust
/// Notify all listeners about a new pending transaction.
    fn on_new_pending_transaction(&self, pending: &AddedTransaction<T::Transaction>) {
        let tx_hash = *pending.hash();
        let propagate_allowed = pending.is_propagate_allowed();

        let mut transaction_listeners = self.pending_transaction_listener.lock();
        transaction_listeners.retain_mut(|listener| {
```

## Snippet 2

Context: `crates/transaction-pool/src/pool/mod.rs:623` (changes signature or replay validation logic)

Before
```rust
impl<T: PoolTransaction> AddedTransaction<T> {
    /// Returns the hash of the transaction if it's pending
    pub(crate) fn as_pending(&self) -> Option<&TxHash> {
        if let AddedTransaction::Pending(tx) = self {
            Some(tx.transaction.hash())
        } else {
            None
```
After
```rust
impl<T: PoolTransaction> AddedTransaction<T> {
    /// Returns whether the transaction is pending
    pub(crate) fn is_pending(&self) -> bool {
        matches!(self, AddedTransaction::Pending(_))
    }
```

## Snippet 3

Context: `crates/transaction-pool/src/pool/mod.rs:635` (changes a sensitive control or state-update path)

Before
```rust
}
    }

    /// Converts this type into the event type for listeners
```
After
```rust
}
    }
    /// Returns if the transaction should be propagated.
    pub(crate) fn is_propagate_allowed(&self) -> bool {
        match self {
            AddedTransaction::Pending(transaction) => transaction.transaction.propagate,
            AddedTransaction::Parked { transaction, .. } => transaction.propagate,
        }
```

## Snippet 4

Context: `crates/transaction-pool/src/pool/mod.rs:323` (changes a sensitive control or state-update path)

Before
```rust
// Notify about new pending transactions
                if let Some(pending_hash) = added.as_pending() {
                    self.on_new_pending_transaction(pending_hash);
                }
```
After
```rust
// Notify about new pending transactions
                if added.is_pending() {
                    self.on_new_pending_transaction(&added);
                }
```

# Fix Pattern

Preserve security- or policy-relevant metadata across an internal API boundary instead of reducing an object to an identifier before downstream filtering decisions are made.

## How It Was Fixed

The patch changes the notification interface from hash-only to `AddedTransaction`-aware. `add_transaction` now passes the full added transaction to `on_new_pending_transaction`, and `AddedTransaction` gains helpers for `is_pending()` and `is_propagate_allowed()`. That gives the notification path access to the propagation flag that was previously lost when only the hash was forwarded.

# Why It Matters

1. It removes an API shape that discarded propagation-policy information before a policy-sensitive listener boundary.

2. It aligns the notification path with the listener type's documented distinction between ordinary listeners and those that may include non-propagatable transactions.

3. It supports a narrow propagation-policy enforcement narrative, but not stronger claims like memory corruption, consensus failure, or a proven confidentiality breach.

# Evidence Notes

Grounded evidence is limited to `crates/transaction-pool/src/pool/mod.rs`. The strongest facts are: the call site changed from `added.as_pending()` plus `on_new_pending_transaction(pending_hash)` to `added.is_pending()` plus `on_new_pending_transaction(&added)`; the notification function signature changed from `&TxHash` to `&AddedTransaction<T::Transaction>`; and the patched function now derives `let tx_hash = *pending.hash();` and `let propagate_allowed = pending.is_propagate_allowed();`. `PendingTransactionListener` also has a `kind` field documented as controlling whether non-propagatable transactions are included. What is not shown is the full post-patch body that uses `propagate_allowed`, any listener implementation proving network propagation, or a regression test demonstrating that non-propagatable transactions were previously emitted. Those gaps warrant downgrading the verdict from likely to unclear. Protocol security invariant: Pending-transaction notifications that feed propagation-sensitive listeners should preserve and honor each transaction's `propagate` policy instead of treating every pending transaction as equally propagatable. Verification notes: The patch does not prove remote code execution, denial of service, or memory-safety impact. The patch does not show that an external attacker can arbitrarily set the `propagate` flag on accepted transactions. The patch does not prove consensus divergence or chain-state corruption. The patch does not establish how widely the leaked notifications were consumed beyond registered listeners. The patch supports a propagation-policy violation, but not a stronger claim about guaranteed confidentiality breach. Inspect the rest of `on_new_pending_transaction` to confirm `propagate_allowed` is actually used to suppress delivery to propagation-facing listeners. Check tests for a case where a non-propagatable pending transaction is withheld from ordinary pending-transaction listeners. Verify whether these listeners directly drive network dissemination or also serve purely local/internal consumers. Confirm whether the bug was externally triggerable in practice or was mainly an internal correctness hardening change. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `policy-enforcement`
Final impact type: `network-policy-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-pool, propagation-policy, network-facing`

The patch is best treated as security hardening. The commit explicitly restricts propagation to transactions marked as allowed for propagation, and the code change preserves the `propagate` policy bit across the listener-notification boundary in a path documented as controlling whether transactions are propagated over the network. That is a security-sensitive exposure/control decision, but the supplied snippets do not prove a concrete exploitable vulnerability or show the full post-patch filtering logic, so this should not be upgraded to a confirmed security fix.

## Security Evidence

1. Commit subject states the intent: only propagate transactions that are allowed to be propagated.
2. `add_transaction` carries a `propagate` field from validation into `ValidPoolTransaction`, showing propagation is an explicit policy decision.
3. `on_new_pending_transaction` changed from taking only `&TxHash` to the full `&AddedTransaction`, preserving policy context instead of collapsing it to a hash.
4. The patch adds `is_propagate_allowed()` and extracts `propagate_allowed` in the notification path.
5. `PendingTransactionListener.kind` is documented as deciding whether to include transactions that should not be propagated over the network, making this listener boundary network-sensitive.

## Missing Evidence

1. The provided excerpt does not show the rest of `on_new_pending_transaction`, so actual enforcement using `propagate_allowed` is not visible.
2. No regression test is shown proving that non-propagatable transactions were previously delivered to ordinary propagation-facing listeners.
3. The evidence does not prove that these listeners directly drove external peer propagation rather than purely local subscribers.
4. The patch does not show attacker control, exploitability, or observed confidentiality/integrity impact.

## Claim Boundaries

1. Supported claim: the patch preserves and likely enforces propagation-policy metadata at a network-sensitive listener boundary.
2. Not supported: a proven externally exploitable vulnerability with demonstrated unauthorized network dissemination.
3. Not supported: state corruption, consensus failure, replay issues, memory safety, or denial of service.
4. If retained in the corpus, it should be framed as propagation-policy hardening, not as a state-integrity bug.
