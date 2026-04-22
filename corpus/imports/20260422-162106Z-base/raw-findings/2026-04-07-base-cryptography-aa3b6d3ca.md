---
case_id: case_20260407_aa3b6d3ca
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2026-04-07
source_refs:
  - git:aa3b6d3ca0f6485a06a4f1efd20dae63d978f22d
  - "crates/builder/publish/src/listener.rs:80"
  - "crates/builder/publish/src/listener.rs:49"
  - "crates/builder/publish/src/listener.rs:418"
  - "crates/builder/publish/src/listener.rs:200"
bug_class: resource-exhaustion
impact_type:
  - denial-of-service
  - availability
confidence: medium
tags:
  - network-facing
  - connection-limit
  - admission-control
  - async-runtime
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit admission control to the publish listener so only a bounded number of connection-handling tasks can proceed at once. The supplied evidence supports an availability-focused hardening change against resource exhaustion in the WebSocket publisher path.

## Observed Patch Facts

1. In `crates/builder/publish/src/listener.rs`, the patch replaces `let cancel = cancel.clone();` with `let permit = match Arc::clone(&semaphore).try_acquire_owned() {`.

2. In `crates/builder/publish/src/listener.rs`, the patch replaces `Self { listener, metrics, receiver, ring_buffer, cancel }` with `Self { listener, metrics, receiver, ring_buffer, cancel, max_connections: DEFAULT_MAX...`.

3. In `crates/builder/publish/src/listener.rs`, the patch adds `#[tokio::test]`.

4. In `crates/builder/publish/src/listener.rs`, the patch replaces `Self { opened: AtomicU64::new(0), closed: AtomicU64::new(0), sent: AtomicU64::new(0) }` with `rejected: AtomicU64,`.

## Project Context

The changed code sits primarily in `crates/builder/publish/src`, `crates/builder/publish`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/builder/publish/src/broadcast.rs`, `crates/builder/publish/src/publisher.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/builder/publish/src/broadcast.rs`, `crates/builder/publish/src/publisher.rs`. The strongest project-level identifiers around this patch are `AtomicU64::new`, `AtomicU64`, `cancel`, and `metrics`.

## Before/After Behavior

Before the change, the accept path shown in `listener.rs` moved from `accept()` into per-connection setup with no visible concurrency gate, so each accepted connection could proceed into handshake and broadcast-related work. After the change, `Listener` carries a `max_connections` setting, `run()` creates a semaphore from that limit, and each accepted connection must acquire a permit immediately; if no permit is available, the connection is dropped, a rejection metric is recorded, and processing does not continue for that socket.

# Root Cause

Missing admission control in the listener accept loop allowed connection pressure to create too many concurrent handshake and broadcast tasks before existing timeout mechanisms reclaimed resources.

## Walkthrough

1. `Listener::new` was changed to store a `max_connections` field with a documented default, making the cap part of listener configuration.

2. `Listener::run` now creates a `tokio::sync::Semaphore` from that limit before entering the accept loop.

3. Immediately after `listener.accept()` succeeds, the code calls `try_acquire_owned()` on the shared semaphore.

4. If permit acquisition fails, the code calls `metrics.on_connection_rejected()`, logs that the connection limit was reached, and skips further per-connection work.

5. A new test, `listener_rejects_connections_beyond_limit`, was added to verify that excess connections are rejected rather than allowed to continue.

6. Test metrics were extended with a `rejected` counter to observe the new rejection path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/builder/publish/src/listener.rs | 63 | primary listener accept loop where inbound connections are admitted or rejected before handshake/broadcast work proceeds |
| crates/builder/publish/src/listener.rs | 42 | listener configuration path adding a default and overridable maximum concurrent connection limit |
| crates/builder/publish/src/listener.rs | 418 | regression test asserting connections beyond the configured cap are rejected |
| crates/builder/publish/src/metrics.rs | 1 | publisher metrics interface used to observe connection rejection events for the new admission-control path |

## Code Snippets

## Snippet 1

Context: `crates/builder/publish/src/listener.rs:80` (changes bounds, limits, or capacity handling)

Before
```rust
};

                    let cancel = cancel.clone();
                    let receiver = receiver.resubscribe();
```
After
```rust
};

                    let permit = match Arc::clone(&semaphore).try_acquire_owned() {
                        Ok(permit) => permit,
                        Err(_) => {
                            metrics.on_connection_rejected();
                            debug!(peer_addr = %peer_addr, "connection limit reached, dropping new connection");
                            continue;
```

## Snippet 2

Context: `crates/builder/publish/src/listener.rs:49` (changes a sensitive control or state-update path)

Before
```rust
cancel: CancellationToken,
    ) -> Self {
        Self { listener, metrics, receiver, ring_buffer, cancel }
    }

    /// Runs the listener loop, accepting connections until cancelled.
    pub async fn run(self) {
        let Self { listener, metrics, receiver, ring_buffer, cancel } = self;
```
After
```rust
cancel: CancellationToken,
    ) -> Self {
        Self { listener, metrics, receiver, ring_buffer, cancel, max_connections: DEFAULT_MAX_CONNECTIONS }
    }

    /// Overrides the maximum number of concurrent connections.
    ///
    /// Defaults to [`DEFAULT_MAX_CONNECTIONS`] (8192).
```

## Snippet 3

Context: `crates/builder/publish/src/listener.rs:418` (changes bounds, limits, or capacity handling)

Before
```rust
let _ = handle.await;
    }
}
```
After
```rust
let _ = handle.await;
    }

    #[tokio::test]
    async fn listener_rejects_connections_beyond_limit() {
        let (listener, addr) = bind_listener().await;
        let (_tx, rx) = broadcast::channel::<PositionedPayload>(16);
        let cancel = CancellationToken::new();
```

## Snippet 4

Context: `crates/builder/publish/src/listener.rs:200` (changes a sensitive control or state-update path)

Before
```rust
closed: AtomicU64,
        sent: AtomicU64,
    }

    impl MockMetrics {
        fn new() -> Self {
            Self { opened: AtomicU64::new(0), closed: AtomicU64::new(0), sent: AtomicU64::new(0) }
        }
```
After
```rust
closed: AtomicU64,
        sent: AtomicU64,
        rejected: AtomicU64,
    }

    impl MockMetrics {
        fn new() -> Self {
            Self {
```

# Fix Pattern

Add an early resource-admission check at the network entry point, backed by a bounded-concurrency primitive and explicit rejection telemetry.

## How It Was Fixed

The listener now enforces a maximum number of concurrent connections with a semaphore. Excess connections are rejected immediately in the accept loop instead of being allowed to proceed into handshake and broadcast handling, and the new behavior is covered by a targeted test and metric.

# Why It Matters

1. Bounds peak resource consumption from incoming connection pressure.

2. Rejects excess work before handshake and broadcast processing can allocate more memory or scheduler capacity.

3. Improves availability posture of a network-facing service path.

4. The evidence supports an availability issue only; it does not support confidentiality, integrity, or auth-bypass claims.

# Evidence Notes

This assessment is grounded in the provided snippets from `crates/builder/publish/src/listener.rs`: the new semaphore acquisition and rejection branch in the accept loop, the added `max_connections` configuration with default `DEFAULT_MAX_CONNECTIONS`, and the test `listener_rejects_connections_beyond_limit`. The commit message explicitly states the motivation was preventing memory and task-scheduler exhaustion under heavy connection pressure. That is sufficient to support a security-relevant availability hardening claim, but not a stronger claim about proven exploitability in all deployments. Protocol security invariant: The network-facing publish listener must bound in-flight connection setup and broadcast work so new unauthenticated connections cannot drive unbounded memory or executor consumption before timeout-based cleanup occurs. Verification notes: The patch shows availability protection, not confidentiality or integrity impact. It does not prove a previously exploitable internet-reachable denial of service in a specific deployment. It does not show authentication bypass, handshake logic corruption, or message spoofing. It does not establish that the chosen default limit of 8192 is sufficient under all workloads. It does not prove that handshake timeouts alone were bypassable; only that they were insufficient to bound peak concurrent work. The supplied test evidence confirms the intended rejection behavior when the cap is exceeded. The provided material does not quantify exploitability or demonstrate impact beyond resource exhaustion. No evidence shows confidentiality, integrity, authentication, or protocol-correctness compromise. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion`
Final impact type: `denial-of-service, availability`
Final confidence: `medium`
Final tags: `network-facing, connection-limit, admission-control, async-runtime`

The patch adds explicit admission control on a network-facing listener to prevent unbounded concurrent handshake and broadcast work from exhausting memory and executor resources. That is security-relevant availability hardening, and the commit message directly describes the risky condition being addressed. However, the supplied evidence does not prove a demonstrated exploitable vulnerability in real deployments, so the conservative validation is security-hardening rather than a fully confirmed security-fix.

## Security Evidence

1. Commit message states that heavy connection pressure could exhaust memory and task-scheduler resources before handshake timeouts reclaimed them.
2. Listener::run now creates a semaphore from max_connections and requires each accepted connection to acquire a permit before proceeding.
3. If no permit is available, the code immediately drops the connection and records an on_connection_rejected metric.
4. A targeted test was added to verify that connections beyond the configured limit are rejected.
5. The changed path is the inbound connection accept loop for a WebSocket publisher, which is a security-sensitive availability boundary.

## Missing Evidence

1. No proof is provided that the listener is exposed to untrusted attackers in deployed configurations.
2. No exploit, incident, CVE, or reproduction details show concrete denial-of-service impact beyond the described risk.
3. The patch does not quantify how severe the prior exhaustion was or whether it was reliably triggerable under realistic conditions.
4. No evidence shows confidentiality, integrity, authentication, or authorization impact.

## Claim Boundaries

1. Supported claim: the patch hardens a network entry point against resource exhaustion from excessive concurrent connections.
2. Supported claim: the security relevance is availability-focused denial-of-service resistance.
3. Not supported: cryptography, replay, or other protocol-security classifications from the earlier finding metadata.
4. Not supported: a proven exploitable vulnerability across deployments or any confidentiality/integrity compromise.
