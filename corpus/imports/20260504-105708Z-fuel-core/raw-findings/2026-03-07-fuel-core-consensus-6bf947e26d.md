---
case_id: case_20260307_6bf947e26d
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
bug_class: consensus-safety
impact_type:
  - consensus-failure
confidence: medium
source_quality: high
date: 2026-03-07
source_refs:
  - git:6bf947e26d7cc1713861372fddc2d17d19381285
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:1925"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:534"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:526"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:2120"
tags:
  - blockchain-core
  - consensus
  - consensus-safety
  - consensus-failure
  - redis
  - fail-open
  - error-handling
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The evidence supports a consensus-safety fix in the Redis leader lease reconciliation path. `read_stream_entries_on_node` previously returned an empty vector on Redis connection, timeout, or script-read failure, making unavailable Redis state look the same as an empty stream. The patch changes that read path to return `anyhow::Result` and preserve those failures as errors. The commit message and added test connect this behavior to a fork risk where a new leader could skip committed blocks and produce divergent blocks.

## Observed Patch Facts

1. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `fn redis_url(&self) -> String {` with `fn stop(&mut self) {`.

2. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `.await;` with `.await`.

3. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `) -> Vec<(u32, u64, SealedBlock)> {` with `) -> anyhow::Result<Vec<(u32, u64, SealedBlock)>> {`.

4. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch adds `/// When Redis read calls fail on a quorum of nodes,`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src/service/adapters/consensus_module`, `crates/fuel-core/src/service/adapters`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/tx_receiver.rs`, `crates/fuel-core/src/service/adapters/txpool.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/tx_receiver.rs`, `crates/fuel-core/src/service/adapters/txpool.rs`. The strongest project-level identifiers around this patch are `Vec::new`, `stream_entries`, `child`, and `connection`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the patch, Redis read failures in `read_stream_entries_on_node` were silently converted to `Vec::new()`, the same value used for a successful read with no stream entries. After the patch, the function returns `anyhow::Result<Vec<(u32, u64, SealedBlock)>>`; connection failures propagate, timeouts become explicit timeout errors, and Redis command errors become explicit read errors.

# Root Cause

Fail-open error handling in a consensus reconciliation read path collapsed two distinct states: Redis read failure and a valid empty block stream. That allowed downstream reconciliation logic to potentially proceed with incomplete knowledge of committed blocks.

## Walkthrough

1. A new PoA leader enters Redis leader lease reconciliation and reads stream entries from Redis nodes.

2. Before the fix, failure to obtain a Redis connection returned an empty vector.

3. Before the fix, Redis script timeout or command failure also returned an empty vector after clearing the cached connection.

4. Because an empty vector also represented a successful empty stream, callers could not tell whether no blocks existed or the read failed.

5. The commit message and regression test state that quorum read failures could let reconciliation skip committed blocks and produce divergent blocks.

6. After the fix, the read helper returns `anyhow::Result` and preserves Redis availability/read failures as errors.

7. The added test documents that quorum Redis read failures must make `unreconciled_blocks` return an error rather than an empty list.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 525 | Redis leader lease reconciliation read path now returns anyhow::Result instead of Vec, preserving read failures as failures. |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 534 | Redis stream read timeout and command errors are mapped to explicit errors instead of silently clearing the connection and returning an empty list. |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 2111 | Regression test documents that quorum Redis read failures must return an error rather than allowing divergent block production. |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 1918 | Test Redis server lifecycle helper supports failure-scenario coverage by stopping Redis nodes. |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:1925` (changes a sensitive control or state-update path)

Before
```rust
}

        fn redis_url(&self) -> String {
            self.redis_url.clone()
```
After
```rust
}

        fn stop(&mut self) {
            if let Some(child) = self.child.as_mut() {
                let _ = child.kill();
                let _ = child.wait();
            }
            self.child = None;
```

## Snippet 2

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:534` (changes a sensitive control or state-update path)

Before
```rust
.invoke_async::<Vec<(u32, u64, Vec<u8>)>>(&mut connection),
        )
        .await;
        let stream_entries = match stream_entries {
            Ok(Ok(stream_entries)) => stream_entries,
            Ok(Err(_)) | Err(_) => {
                self.clear_cached_connection(redis_node).await;
                return Vec::new();
```
After
```rust
.invoke_async::<Vec<(u32, u64, Vec<u8>)>>(&mut connection),
        )
        .await
        .map_err(|_| {
            anyhow!("Timed out reading stream entries from Redis node")
        })?
        .map_err(|e| {
            anyhow!("Failed to read stream entries from Redis node: {e}")
```

## Snippet 3

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:526` (changes a sensitive control or state-update path)

Before
```rust
&self,
        redis_node: &RedisNode,
    ) -> Vec<(u32, u64, SealedBlock)> {
        let mut connection = match self.multiplexed_connection(redis_node).await {
            Ok(connection) => connection,
            Err(_) => return Vec::new(),
        };
        let stream_entries = timeout(
```
After
```rust
&self,
        redis_node: &RedisNode,
    ) -> anyhow::Result<Vec<(u32, u64, SealedBlock)>> {
        let mut connection = self.multiplexed_connection(redis_node).await?;
        let stream_entries = timeout(
            self.node_timeout,
```

## Snippet 4

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:2120` (changes a consensus- or validator-sensitive branch)

Before
```rust
.expect("stream length query should succeed")
    }
}
```
After
```rust
.expect("stream length query should succeed")
    }

    /// When Redis read calls fail on a quorum of nodes,
    /// `unreconciled_blocks` must return an error — not silently
    /// return an empty list that would let the caller produce
    /// a divergent block.
    #[tokio::test(flavor = "multi_thread")]
```

# Fix Pattern

Preserve storage-read failures as errors at the consensus reconciliation boundary instead of encoding them as successful empty results.

## How It Was Fixed

The observed implementation changes `read_stream_entries_on_node` from returning a bare vector to returning `anyhow::Result`. It removes the connection-failure branch that returned `Vec::new()`, uses `?` for connection acquisition, and maps timeout and Redis command failures into explicit errors. Test support adds a Redis server stop helper, and the regression test asserts that quorum read failures must not be treated as no unreconciled blocks.

# Why It Matters

1. Consensus failover must not confuse unavailable storage with an empty committed-block history.

2. The stated impact is divergent block production, which is a consensus-safety risk.

3. The supplied evidence does not establish arbitrary block forgery, transaction theft, confidentiality loss, or a remotely triggerable exploit path.

4. The supplied hunks do not fully prove the quorum-read, lock-expansion, or epoch-adoption implementation details mentioned in the commit body.

# Evidence Notes

Strongest code evidence is in `crates/fuel-core/src/service/adapters/consensus_module/poa.rs` around `read_stream_entries_on_node`, where Redis connection and stream-read failures stop returning `Vec::new()` and become explicit errors. Test evidence states that quorum Redis read failures must return an error because silently returning an empty list could let a caller produce a divergent block. Claims about expanded lock coverage and higher epoch adoption are present in the commit message but are not fully shown by the supplied hunks. Protocol security invariant: During PoA leader failover reconciliation, Redis read failures must remain distinguishable from a successful read of an empty block stream before a new leader decides that no committed blocks need replay. Verification notes: The patch does not prove a remote attacker can cause the Redis read failures. The patch does not show arbitrary block forgery, transaction theft, or signature bypass. The provided hunks do not fully show the quorum-read implementation, expanded lock coverage, or epoch adoption logic. The evidence supports a consensus fork risk, not a confidentiality issue. Deployment exposure and whether the faulty Redis leader lease mode is enabled in production are not established by the patch evidence. Verified from supplied input only; no repository inspection was performed. Security classification is downgraded from confirmed to likely because the evidence supports fork risk but does not show exploitability or production exposure. Confidence is medium because the critical helper and test are shown, but the full caller-side quorum behavior is not included. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final tags: `blockchain-core, consensus, consensus-safety, consensus-failure, redis, fail-open, error-handling`

The supplied patch evidence supports retaining this as a security-relevant consensus safety fix. A Redis leader lease reconciliation helper previously collapsed connection, timeout, and command failures into an empty block list, and the patch changes that path to propagate errors. The commit message and added regression test directly tie the fail-open behavior to a fork risk where a new leader could skip committed blocks and produce divergent blocks. The evidence does not prove remote exploitability or broader claims such as signature issues, so the classification should remain conservative and the misleading signature tag should be removed.

## Security Evidence

1. Consensus reconciliation read path changed from returning Vec to anyhow::Result, preserving Redis read failures as errors.
2. Previous code returned Vec::new() on Redis connection/read/timeout failure, making failure indistinguishable from an empty stream.
3. Added test states quorum Redis read failures must return an error rather than allowing divergent block production.
4. Commit metadata explicitly describes skipped committed blocks and divergent block production during leader failover.

## Missing Evidence

1. No supplied evidence shows a remote attacker can trigger the Redis read failures.
2. No supplied hunk fully shows the caller-side quorum-read logic, expanded lock coverage, or epoch adoption implementation.
3. No evidence supports arbitrary block forgery, signature bypass, theft, or confidentiality impact.
4. No deployment context proves the faulty Redis leader lease mode is enabled in production.

## Claim Boundaries

1. Validated impact is consensus safety/fork risk, not signature compromise.
2. Validated bug is fail-open error handling in Redis-backed consensus reconciliation.
3. Keep claims limited to leader failover/reconciliation behavior shown by the patch and tests.
4. Do not claim remote exploitability from the supplied evidence alone.
