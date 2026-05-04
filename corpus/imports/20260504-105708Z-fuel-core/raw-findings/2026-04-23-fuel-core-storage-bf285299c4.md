---
case_id: case_20260423_bf285299c4
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: storage
confidence: medium
source_quality: high
date: 2026-04-23
source_refs:
  - git:bf285299c4085b0e64f5e109b99c43c1e7da21f5
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:1327"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:2016"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:129"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:979"
bug_class: leader-lease-release-delay
impact_type:
  - consensus-availability
  - delayed-failover
tags:
  - blockchain-core
  - consensus
  - validator
  - poa
  - leader-lease
  - availability
  - redis
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes Redis leader-lease lifetime accounting in the Fuel Core PoA adapter. Spawned publish-task clones previously carried the same `drop_release_guard` as logical adapter clones, so in-flight slow-node tasks could keep the guard's `Arc` strong count above one and cause `Drop` on the owning adapter to skip lease release. The fix makes the guard optional, clears it on spawned-task clones, and makes `Drop` ignore those task-only clones. The supported security relevance is limited to consensus availability and failover hardening; the evidence does not support replay, signature-validation, invalid-block, or unauthorized-leader claims.

## Observed Patch Facts

1. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `if std::sync::Arc::strong_count(&self.drop_release_guard) != 1 {` with `// Task-spawned clones (see 'publish_block_on_all_nodes') carry`.

2. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `#[tokio::test(flavor = "multi_thread")]` with `/// Regression test: after 'publish_produced_block' short-circuits on`.

3. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `drop_release_guard: std::sync::Arc<()>,` with `/// 'Some(Arc::new(()))' on logical adapter clones — the strong count`.

4. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `let adapter = self.clone();` with `// Clone the adapter for the spawned task, but null out the`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src/service/adapters/consensus_module`, `crates/fuel-core/src/service/adapters`, which anchors the finding in the `storage` area of the project. Historical context from `crates/fuel-core/src/service/adapters/import_result_provider.rs`, `crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/broadcast.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/fuel-core/src/service/adapters/import_result_provider.rs`, `crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/broadcast.rs`. The strongest project-level identifiers around this patch are `adapter`, `release`, `clone`, and `std::sync::Arc`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the change, `RedisLeaderLeaseAdapter` stored `drop_release_guard: Arc<()>`; every `self.clone()` in `publish_block_on_all_nodes` cloned that guard. Since `Drop` returned early when `Arc::strong_count(&self.drop_release_guard) != 1`, lingering spawned tasks after quorum short-circuit could make the owning adapter skip lease release until those tasks completed or timed out. After the change, `drop_release_guard` is `Option<Arc<()>>`; logical clones keep `Some`, spawned publish-task clones set it to `None`, and `Drop` returns immediately for `None` while preserving the strong-count gate for logical clones.

# Root Cause

Task-spawned adapter clones were treated as logical owners of the Redis leader lease because they cloned the same `drop_release_guard`. This made the strong-count release gate conflate background task lifetime with logical adapter lifetime.

## Walkthrough

1. `RedisLeaderLeaseAdapter` used an `Arc<()>` guard so only the last logical clone would release the Redis leader lease in `Drop`.

2. `publish_block_on_all_nodes` cloned the full adapter for each spawned Redis write task.

3. Those task clones also cloned `drop_release_guard`, increasing the guard's strong count.

4. The publish path could short-circuit after quorum while slow or half-alive node tasks remained in flight.

5. If the owning adapter was dropped during that window, `Drop` saw a strong count greater than one and skipped lease release.

6. The patch changes the guard to `Option<Arc<()>>` and clears it on spawned publish-task clones.

7. `Drop` now ignores task clones with `None` and only uses the strong-count gate for logical clones with `Some`.

8. A regression test covers prompt lease release after quorum publish while a half-alive node task remains in flight.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 129 | RedisLeaderLeaseAdapter stores drop_release_guard as Option<Arc<()>> to distinguish logical clones from task-spawned clones. |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 979 | publish_block_on_all_nodes clones the adapter for spawned Redis write tasks and clears drop_release_guard so in-flight tasks do not extend lease-release lifetime. |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 1327 | Drop ignores task-spawned clones with None and only checks strong_count on logical guards before releasing the lease. |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 2016 | Regression test covers prompt lease release after quorum publish while a half-alive node task remains in flight. |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:1327` (changes a sensitive control or state-update path)

Before
```rust
impl Drop for RedisLeaderLeaseAdapter {
    fn drop(&mut self) {
        if std::sync::Arc::strong_count(&self.drop_release_guard) != 1 {
            return;
        }
```
After
```rust
impl Drop for RedisLeaderLeaseAdapter {
    fn drop(&mut self) {
        // Task-spawned clones (see `publish_block_on_all_nodes`) carry
        // `None` here so they don't extend the logical adapter's
        // lifetime — their drop must not trigger a lease release.
        let Some(guard) = &self.drop_release_guard else {
            return;
        };
```

## Snippet 2

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:2016` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    #[tokio::test(flavor = "multi_thread")]
    async fn drop__when_non_last_clone_is_dropped_then_does_not_release_shared_lease() {
```
After
```rust
}

    /// Regression test: after `publish_produced_block` short-circuits on
    /// quorum, lingering background tasks (spawned by
    /// `publish_block_on_all_nodes` for the slow nodes) used to clone
    /// the entire adapter — including `drop_release_guard`. The strong
    /// count on that guard would stay > 1 until the background tasks
    /// finished, so dropping the owning adapter would skip the lease
```

## Snippet 3

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:129` (changes a sensitive control or state-update path)

Before
```rust
block_stream_key: String,
    lease_owner_token: String,
    drop_release_guard: std::sync::Arc<()>,
    current_epoch_token: std::sync::Arc<std::sync::Mutex<Option<u64>>>,
    lease_ttl_millis: u64,
```
After
```rust
block_stream_key: String,
    lease_owner_token: String,
    /// `Some(Arc::new(()))` on logical adapter clones — the strong count
    /// gates the lease-release path in `Drop` (only the last clone
    /// triggers release). `None` on adapter clones spawned into short-
    /// lived background tasks (see `publish_block_on_all_nodes`) so they
    /// don't extend that count and delay release after the owning
    /// adapter is dropped.
```

## Snippet 4

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:979` (changes a sensitive control or state-update path)

Before
```rust
)>();
        for idx in 0..n {
            let adapter = self.clone();
            let tx = tx.clone();
            let block = block.clone();
```
After
```rust
)>();
        for idx in 0..n {
            // Clone the adapter for the spawned task, but null out the
            // drop guard so this clone doesn't pin the logical adapter
            // lifetime. Without this, a lingering background task after
            // quorum short-circuit would keep `Arc::strong_count(...) > 1`
            // and the owning adapter's `Drop` would skip lease release.
            let mut adapter = self.clone();
```

# Fix Pattern

Separate logical ownership guards from background task handles so short-lived or lingering async work does not pin shutdown, release, or failover behavior unless it is intentionally part of the ownership model.

## How It Was Fixed

The patch changed `drop_release_guard` from `std::sync::Arc<()>` to `Option<std::sync::Arc<()>>`. In `publish_block_on_all_nodes`, spawned-task adapter clones are made mutable and assigned `adapter.drop_release_guard = None;` before being moved into tasks. In `Drop`, `None` causes an immediate return, while `Some(guard)` continues to use `Arc::strong_count(guard)` to release only from the last logical clone.

# Why It Matters

1. Preserves prompt Redis leader-lease release when the owning PoA adapter is dropped.

2. Avoids tying leader failover timing to slow or half-alive publish tasks after quorum has completed.

3. Hardens crash, panic, or shutdown behavior in the PoA leader-lease path.

4. Does not establish invalid block acceptance, replay, signature-validation failure, or unauthorized block production.

# Evidence Notes

Evidence is limited to `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`: the guard field changes to `Option<Arc<()>>`, spawned publish-task clones clear the guard, `Drop` handles `None` task clones and checks strong count on `Some`, and a regression test describes quorum short-circuit with lingering background tasks delaying release before the fix. The commit message describes delayed failover in crash/panic scenarios, but provides no evidence of an external attacker trigger or consensus safety violation. Protocol security invariant: In the PoA Redis leader-lease path, only logical adapter ownership should gate lease release. Background publish tasks that may outlive quorum completion should not keep the release guard alive, because dropping the owning adapter should promptly release the Redis lease for failover. Verification notes: No evidence of replay or signature-validation impact. No evidence of unauthorized block production or consensus safety failure. No proof that an external attacker can trigger or amplify the delayed release. No proof of permanent leader lockout; described delay is bounded by node_timeout per slow or dead node. No evidence of state corruption or accepted invalid blocks. Regression test documents prompt release with three healthy nodes and one half-alive in-flight task. Claims about replay, signature validation, unauthorized leadership, state corruption, or accepted invalid blocks are unsupported. Security classification is availability hardening, not a confirmed exploitable vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `leader-lease-release-delay`
Final impact type: `consensus-availability, delayed-failover`
Final tags: `blockchain-core, consensus, validator, poa, leader-lease, availability, redis`

The patch clearly hardens a consensus-sensitive PoA leader-lease path by ensuring spawned background publish tasks do not keep the Redis lease-release guard alive after the owning adapter is dropped. The supported impact is delayed failover or availability degradation in crash, panic, or shutdown scenarios, not replay, signature validation, or invalid block acceptance. Evidence is sufficient for security-hardening, but not for a concrete exploitable security-fix claim.

## Security Evidence

1. Changed `RedisLeaderLeaseAdapter` lease-release guard from `Arc<()>` to `Option<Arc<()>>` to distinguish logical adapter ownership from task-spawned clones.
2. Spawned publish-task clones now set `adapter.drop_release_guard = None`, preventing in-flight slow-node tasks from pinning lease lifetime.
3. `Drop` now ignores task-only clones and checks `Arc::strong_count` only for logical guard holders before releasing the lease.
4. Regression test documents quorum short-circuit with a half-alive node where old behavior delayed lease release until background task timeout.
5. Commit message explicitly ties the bug to delayed leader failover in crash or panic scenarios.

## Missing Evidence

1. No proof of external attacker control over the slow or half-alive task condition.
2. No evidence of replay, signature-validation bypass, invalid block acceptance, or unauthorized block production.
3. No demonstrated permanent lockout; described delay appears bounded by node timeout per slow or dead node.
4. No exploit scenario showing direct compromise of consensus safety.

## Claim Boundaries

1. Classify as consensus availability hardening, not replay or signature validation.
2. Do not claim accepted invalid blocks or state corruption.
3. Do not claim unauthorized leadership or lease theft.
4. Do not claim a confirmed exploitable vulnerability from the patch alone.
