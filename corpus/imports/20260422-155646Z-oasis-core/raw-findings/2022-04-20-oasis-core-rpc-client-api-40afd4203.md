---
case_id: case_20220420_40afd4203
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: medium
date: 2022-04-20
source_refs:
  - git:40afd420339488f1dfbc8f2ba24c281484a84006
  - "go/worker/compute/executor/committee/node.go:1565"
  - "go/runtime/host/mock/mock.go:146"
  - "go/worker/compute/executor/committee/node.go:1527"
  - "go/worker/compute/executor/committee/node.go:1590"
bug_class: trust-root-verification
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - consensus
  - trust-root
  - registration-gating
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes executor startup and availability gating so registration depends on a trust-sync condition in addition to ordinary runtime readiness. The evidence supports a readiness/initialization fix around trust-root synchronization, but it does not establish a demonstrated vulnerability or exploit path.

## Observed Patch Facts

1. In `go/worker/compute/executor/committee/node.go`, the patch replaces `// We are now able to service requests for this runtime.` with `// Make sure the runtime supports all the required features.`.

2. In `go/runtime/host/mock/mock.go`, the patch adds `case body.RuntimeConsensusSyncRequest != nil:`.

3. In `go/worker/compute/executor/committee/node.go`, the patch replaces `case n.runtimeReady && lastRoundAvailable:` with `case n.runtimeReady && lastRoundAvailable && n.runtimeTrustSynced:`.

4. In `go/worker/compute/executor/committee/node.go`, the patch adds `// Cancel any outstanding runtime light client sync.`.

## Project Context

The changed code sits primarily in `go/worker/compute/executor/committee`, `go/worker/compute/executor`, `go/runtime/host/mock`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `go/worker/compute/executor/committee/p2p.go`, `go/worker/compute/executor/committee/batch.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/compute/executor/worker.go`, `go/runtime/host/protocol/connection.go`. The strongest project-level identifiers around this patch are `runtimeReady`, `case`, `runtime`, and `requests`. Nearby tests or test-like files include `go/runtime/host/tests/tester.go`, `go/worker/compute/executor/tests/tester.go`.

## Before/After Behavior

Before the patch, the start handler marked the runtime ready immediately and availability only required `runtimeReady` plus last-round availability. After the patch, startup clears `runtimeTrustSynced`, starts a runtime trust-sync flow, and availability additionally requires `runtimeTrustSynced`; stop/failure also cancels outstanding trust-sync work.

# Root Cause

The availability state machine did not include completion of runtime trust synchronization as a prerequisite for registration or advertised availability.

## Walkthrough

1. In `HandleRuntimeHostEvent`, the old `ev.Started` path set `n.runtimeReady = true` immediately.

2. The patched start path first sets `n.runtimeReady = false` and `n.runtimeTrustSynced = false`, retrieves the hosted runtime, and calls `startRuntimeTrustSyncLocked(rt)` with a comment that request processing will fail if required trust sync is not completed.

3. The same patched start handler still later sets `n.runtimeReady = true`, so the new behavior separates runtime startup from trust-sync completion.

4. In `nudgeAvailability`, the gate changes from `n.runtimeReady && lastRoundAvailable` to `n.runtimeReady && lastRoundAvailable && n.runtimeTrustSynced`.

5. In the stop/failure path, the patch adds `n.cancelRuntimeTrustSyncLocked()` to clean up outstanding sync work.

6. `go/runtime/host/mock/mock.go` adds `RuntimeConsensusSyncRequest` handling, which supports the new trust-sync interaction in mocked execution.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/worker/compute/executor/committee/node.go | 1564 | runtime start handler now initiates trust sync and resets trust-synced state before the executor is considered ready |
| go/worker/compute/executor/committee/node.go | 1523 | availability/registration gate now requires `runtimeTrustSynced` in addition to runtime readiness and last-round availability |
| go/worker/compute/executor/committee/node.go | 1590 | runtime stop/failure path now cancels outstanding trust-sync work to avoid stale verified state |
| go/worker/compute/executor/committee/trust.go | 2 | helper path that drives runtime light-client synchronization to the latest consensus height when a trust root is configured |
| go/runtime/host/mock/mock.go | 140 | host protocol mock gains `RuntimeConsensusSyncRequest` support for the trust-sync flow |

## Code Snippets

## Snippet 1

Context: `go/worker/compute/executor/committee/node.go:1565` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
switch {
	case ev.Started != nil:
		// We are now able to service requests for this runtime.
		n.runtimeReady = true
```
After
```go
switch {
	case ev.Started != nil:
		// Make sure the runtime supports all the required features.
		n.runtimeReady = false
		n.runtimeTrustSynced = false

		rt := n.commonNode.GetHostedRuntime()
		if rt == nil {
```

## Snippet 2

Context: `go/runtime/host/mock/mock.go:146` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}}, nil
		}
	default:
		return nil, fmt.Errorf("(mock) method not supported")
```
After
```go
}}, nil
		}
	case body.RuntimeConsensusSyncRequest != nil:
		// Nothing to be done, but we need to indicate success.
		return &protocol.Body{RuntimeConsensusSyncResponse: &protocol.Empty{}}, nil
	default:
		return nil, fmt.Errorf("(mock) method not supported")
```

## Snippet 3

Context: `go/worker/compute/executor/committee/node.go:1527` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
switch {
	case n.runtimeReady && lastRoundAvailable:
		// Executor is ready to process requests.
		if n.roleProvider.IsAvailable() && !force {
```
After
```go
switch {
	case n.runtimeReady && lastRoundAvailable && n.runtimeTrustSynced:
		// Executor is ready to process requests.
		if n.roleProvider.IsAvailable() && !force {
```

## Snippet 4

Context: `go/worker/compute/executor/committee/node.go:1590` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// Runtime failed to start or was stopped -- we can no longer service requests.
		n.runtimeReady = false
	default:
		// Unknown event.
```
After
```go
// Runtime failed to start or was stopped -- we can no longer service requests.
		n.runtimeReady = false

		// Cancel any outstanding runtime light client sync.
		n.cancelRuntimeTrustSyncLocked()
	default:
		// Unknown event.
```

# Fix Pattern

Add an explicit trust-sync completion state to the lifecycle and require it in availability or registration decisions.

## How It Was Fixed

The change introduces `runtimeTrustSynced` into the availability condition, resets that state on runtime start, initiates trust synchronization, and cancels outstanding sync work on stop or failure. Supporting mock code was updated to accept `RuntimeConsensusSyncRequest`.

# Why It Matters

1. It avoids registering a runtime before the new trust-sync condition is met.

2. It reduces startup-state mismatches between 'runtime started' and 'runtime available'.

3. The visible evidence points to correctness or hardening around startup and request handling, not a proven compromise.

# Evidence Notes

Direct evidence is limited to readiness gating, a trust-sync start call and comment, cleanup on stop, and mock protocol support. The excerpts do not show where `runtimeTrustSynced` becomes true, whether unverified state was previously consumed, or any concrete attacker-driven impact. Protocol security invariant: If a runtime is configured with a trust root, the executor should not register as available until trust synchronization has completed. Verification notes: The patch does not prove a remote exploit path or attacker-controlled trigger. The evidence does not show that unverified consensus state was ever accepted and used for successful execution. The visible comments point to request-processing failure/incorrect readiness, not confirmed consensus compromise. No confidentiality or privilege-escalation impact is demonstrated by the provided diff alone. The diff directly adds `runtimeTrustSynced` to `nudgeAvailability`. The lifecycle handlers directly add trust-sync initialization and cancellation. `trust.go` is only represented by a brief excerpt/comment, so full sync semantics are not shown. No provided evidence demonstrates unauthorized execution, consensus compromise, privilege escalation, or data exposure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `trust-root-verification`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, trust-root, registration-gating`

The patch is security-relevant hardening because it explicitly prevents an executor from registering as available until runtime trust synchronization has completed when a trust root is configured. That is a trust-verification gate in a consensus-sensitive path, not just generic cleanup. However, the provided diff does not prove that the prior behavior enabled a concrete exploit or that unverified state was actually accepted and used, so this is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. Commit subject and code both center on verifying a configured trust root before registration.
2. Startup behavior changes from immediately setting `runtimeReady = true` to clearing readiness and `runtimeTrustSynced` first.
3. Availability gating now requires `n.runtimeTrustSynced` before the executor is considered ready to process requests.
4. The comment says trust sync must succeed when a trust root is configured, tying the change to a verification invariant rather than ordinary feature readiness.
5. Stop/failure handling now cancels outstanding trust-sync work, reducing stale or inconsistent verified-state handling.

## Missing Evidence

1. No provided snippet shows where `runtimeTrustSynced` becomes true or what exact checks constitute successful verification.
2. No evidence demonstrates that unverified consensus/runtime state was previously consumed for successful execution.
3. No exploit narrative, attacker trigger, or concrete integrity violation is shown in the patch alone.

## Claim Boundaries

1. Supported claim: the patch tightens registration/readiness so trust-root synchronization must complete first.
2. Supported claim: this hardens a consensus-sensitive trust-verification path.
3. Not supported: a proven exploitable vulnerability existed before this change.
4. Not supported: confidentiality, privilege escalation, or confirmed consensus compromise impact.
