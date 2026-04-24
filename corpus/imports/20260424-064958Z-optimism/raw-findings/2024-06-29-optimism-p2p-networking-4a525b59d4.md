---
case_id: case_20240629_4a525b59d4
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: medium
date: 2024-06-29
source_refs:
  - git:4a525b59d4eba01f34954d9e3aca4607a1916deb
  - "op-node/p2p/sync.go:564"
  - "op-node/p2p/host.go:77"
  - "op-node/p2p/sync.go:305"
  - "op-node/p2p/sync_test.go:357"
bug_class: peer-selection-hardening
impact_type:
  - reduced-attack-surface
confidence: medium
tags:
  - blockchain-core
  - p2p-networking
  - p2p
  - peer-selection
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an optional policy that stops the sync client from issuing outbound sync requests to non-static peers. The code supports a configurable trust-boundary tightening in the req/resp sync path, but the provided evidence does not establish that the previous behavior was a concrete vulnerability.

## Observed Patch Facts

1. In `op-node/p2p/sync.go`, the patch replaces `for {` with `// if onlyReqToStatic is on, ensure that only static peers are dealing with the request`.

2. In `op-node/p2p/host.go`, the patch replaces `func (e *extraHost) Close() error {` with `func (e *extraHost) IsStatic(peerID peer.ID) bool {`.

3. In `op-node/p2p/sync.go`, the patch adds `if extra, ok := host.(ExtraHostFeatures); ok && extra.SyncOnlyReqToStatic() {`.

4. In `op-node/p2p/sync_test.go`, the patch replaces `syncCl := NewSyncClient(log, cfg, hostA.NewStream, func(ctx context.Context, from pee...` with `syncCl := NewSyncClient(log, cfg, hostA, func(ctx context.Context, from peer.ID, payl...`.

## Project Context

The changed code sits primarily in `op-node/p2p`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `op-node/p2p/peer_scores_test.go`, `op-node/p2p/peer_scores.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-node/p2p/node.go`, `op-node/p2p/config.go`. The strongest project-level identifiers around this patch are `extra`, `peer`, `peerRequests`, and `syncOnlyReqToStatic`.

## Before/After Behavior

Before the change, the sync client constructor captured stream-opening behavior and the per-peer sync loop used the shared request channel without any shown static-peer gate. After the change, the constructor detects host support for `SyncOnlyReqToStatic()`, stores that policy, and `peerLoop` replaces its local request channel with `nil` for non-static peers when the policy is enabled, preventing outbound sync requests on that path.

# Root Cause

No host-driven restriction was enforced in the shown req/resp sync loop for limiting outbound sync requests to static peers. The evidence shows missing policy enforcement, not a demonstrated exploit or protocol break.

## Walkthrough

1. `host.go` adds `IsStatic(peerID)` and `SyncOnlyReqToStatic()` so the sync client can query static-peer status and the new policy flag.

2. `sync.go` updates `NewSyncClient` to inspect extra host features and enable `syncOnlyReqToStatic` only when the host exposes that setting.

3. `sync.go` changes `peerLoop` to use a local `peerRequests` variable.

4. If `syncOnlyReqToStatic` is enabled and the peer is not static, `peerRequests` is set to `nil`.

5. The inline comment states the intended effect: the loop will not perform outgoing sync requests for non-static peers.

6. `sync_test.go` passes the host object into `NewSyncClient`, matching the constructor's new need to read host capabilities.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-node/p2p/sync.go | 305 | Sync client setup; wires the host's only-static-peer policy into runtime behavior. |
| op-node/p2p/sync.go | 564 | Per-peer sync loop; blocks outbound sync requests to non-static peers when the policy is enabled. |
| op-node/p2p/host.go | 77 | Host-side peer classification; exposes static-peer membership and the policy flag to the sync client. |

## Code Snippets

## Snippet 1

Context: `op-node/p2p/sync.go:564` (changes a sensitive control or state-update path)

Before
```go
rl := rate.NewLimiter(peerServerBlocksRateLimit, peerServerBlocksBurst)

	for {
		// wait for a global allocation to be available
```
After
```go
rl := rate.NewLimiter(peerServerBlocksRateLimit, peerServerBlocksBurst)

	// if onlyReqToStatic is on, ensure that only static peers are dealing with the request
	peerRequests := s.peerRequests
	if s.syncOnlyReqToStatic && !s.extra.IsStatic(id) {
		// for non-static peers, set peerRequests to nil
		// this will effectively make the peer loop not perform outgoing sync-requests.
		// while sync-requests will block, the loop may still process other events (if added in the future).
```

## Snippet 2

Context: `op-node/p2p/host.go:77` (changes a sensitive control or state-update path)

Before
```go
}

func (e *extraHost) Close() error {
	close(e.quitC)
```
After
```go
}

func (e *extraHost) IsStatic(peerID peer.ID) bool {
	_, exists := e.staticPeerIDs[peerID]
	return exists
}

func (e *extraHost) SyncOnlyReqToStatic() bool {
```

## Snippet 3

Context: `op-node/p2p/sync.go:305` (changes a sensitive control or state-update path)

Before
```go
receivePayload:      rcv,
	}

	// never errors with positive LRU cache size
```
After
```go
receivePayload:      rcv,
	}
	if extra, ok := host.(ExtraHostFeatures); ok && extra.SyncOnlyReqToStatic() {
		c.extra = extra
		c.syncOnlyReqToStatic = true
	}

	// never errors with positive LRU cache size
```

## Snippet 4

Context: `op-node/p2p/sync_test.go:357` (changes a sensitive control or state-update path)

Before
```go
defer hostB.Close()

	syncCl := NewSyncClient(log, cfg, hostA.NewStream, func(ctx context.Context, from peer.ID, payload *eth.ExecutionPayloadEnvelope) error {
		return nil
	}, metrics.NoopMetrics, &NoopApplicationScorer{})
```
After
```go
defer hostB.Close()

	syncCl := NewSyncClient(log, cfg, hostA, func(ctx context.Context, from peer.ID, payload *eth.ExecutionPayloadEnvelope) error {
		return nil
	}, metrics.NoopMetrics, &NoopApplicationScorer{})
```

# Fix Pattern

Add an optional runtime policy gate in a sensitive path and suppress work for peers outside the allowed set.

## How It Was Fixed

The change wires a host-exposed configuration flag and static-peer lookup into the sync client, then enforces that policy inside each per-peer sync loop by disabling the outbound request channel for non-static peers. This narrows who can be used for outbound req/resp synchronization when the flag is turned on.

# Why It Matters

1. Lets operators constrain outbound sync requests to a curated peer set.

2. Reduces trust placed in dynamically discovered peers when the option is enabled.

3. Shows hardening of peer selection, not proof of a pre-existing exploitable flaw.

# Evidence Notes

The strongest evidence is limited to conditional behavior in `op-node/p2p/sync.go` and supporting accessors in `op-node/p2p/host.go`. The excerpts do not show the flag's default, whether it is broadly deployed, or any concrete attack enabled by the old behavior. The test change appears to support constructor plumbing rather than demonstrate a security bug. Protocol security invariant: When the optional `p2p.sync.onlyreqtostatic` policy is enabled, outbound req/resp sync requests should be initiated only for static peers. Verification notes: The patch does not prove the new flag is enabled by default or deployed everywhere. The diff does not demonstrate a remotely exploitable denial-of-service, integrity break, or auth bypass in prior behavior. Non-static peers are only excluded from outbound sync requests here; the patch does not show they are barred from all P2P participation. The evidence does not show a consensus-rule change or that prior syncing from non-static peers was inherently unsafe in all deployments. The code clearly enforces the restriction only when `SyncOnlyReqToStatic()` is true. The provided snippets do not show that non-static peers were otherwise malicious or unsafe. No evidence here shows denial-of-service, integrity loss, authentication bypass, or consensus impact. This is best classified as optional security-relevant hardening with unproven vulnerability status. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `peer-selection-hardening`
Final impact type: `reduced-attack-surface`
Final confidence: `medium`
Final tags: `blockchain-core, p2p-networking, p2p, peer-selection, security-hardening`

The patch adds and wires an optional policy that restricts outbound req/resp sync requests to static peers only. That is a real security-relevant tightening of trust boundaries in a network-facing path, but the supplied evidence does not show that the prior behavior was exploitable, default-enabled, or directly caused denial of service. The original resource-exhaustion and remote-DoS framing is stronger than the patch supports; this is better retained as security hardening.

## Security Evidence

1. `sync.go` disables outbound peer request handling for non-static peers when `syncOnlyReqToStatic` is enabled.
2. `host.go` adds `IsStatic(peerID)` and exposes `SyncOnlyReqToStatic()` so the sync client can enforce the policy.
3. `NewSyncClient` now reads the host capability and activates the restriction only when the policy flag is set.
4. The change affects the P2P sync request path, which is a security-sensitive network trust boundary.

## Missing Evidence

1. No evidence shows the old behavior enabled a concrete attack or exploitable bug.
2. No evidence shows the new flag is enabled by default or broadly deployed.
3. No evidence ties the change to resource exhaustion, remote DoS, integrity loss, or auth bypass.
4. No test or commit text demonstrates an adversarial scenario against non-static peers.

## Claim Boundaries

1. Supported claim: the patch hardens peer selection for outbound sync requests when an optional flag is enabled.
2. Supported claim: non-static peers are excluded from this specific outbound sync-request path under that policy.
3. Not supported: prior behavior was a confirmed vulnerability.
4. Not supported: the fix addresses resource exhaustion or remote DoS specifically.
5. Not supported: non-static peers are blocked from all P2P interactions.
