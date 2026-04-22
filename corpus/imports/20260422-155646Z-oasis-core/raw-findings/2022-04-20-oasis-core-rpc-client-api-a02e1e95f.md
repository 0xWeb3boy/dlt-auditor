---
case_id: case_20220420_a02e1e95f
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
  - git:a02e1e95f8370c08d38496ca81943d1e0ada3f09
  - "go/runtime/host/mock/mock.go:166"
  - "go/worker/compute/executor/committee/node.go:1427"
  - "go/worker/compute/executor/committee/node.go:1378"
  - "go/worker/compute/executor/committee/node.go:1442"
bug_class: improper-trust-verification-gating
impact_type:
  - premature-registration
  - trust-state-exposure
confidence: medium
tags:
  - blockchain-core
  - consensus
  - trust-root
  - registration-gating
  - light-client
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds trust-sync state to the executor readiness path: startup begins runtime trust sync, availability now requires `runtimeTrustSynced`, and shutdown cancels outstanding sync work. That supports a grounded reading of a readiness/registration correctness fix for trust-rooted runtimes. The supplied evidence does not establish a concrete exploitable vulnerability beyond premature registration or failed request handling.

## Observed Patch Facts

1. In `go/runtime/host/mock/mock.go`, the patch adds `case body.RuntimeConsensusSyncRequest != nil:`.

2. In `go/worker/compute/executor/committee/node.go`, the patch adds `// If the runtime has a trust root configured, make sure we are able to successfully...`.

3. In `go/worker/compute/executor/committee/node.go`, the patch replaces `case n.runtimeReady && lastRoundAvailable:` with `case n.runtimeReady && lastRoundAvailable && n.runtimeTrustSynced:`.

4. In `go/worker/compute/executor/committee/node.go`, the patch adds `// Cancel any outstanding runtime light client sync.`.

## Project Context

The changed code sits primarily in `go/runtime/host/mock`, `go/runtime/host`, `go/worker/compute/executor/committee`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `go/worker/compute/executor/committee/p2p.go`, `go/worker/compute/executor/committee/batch.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/compute/executor/worker.go`, `go/runtime/host/protocol/connection.go`. The strongest project-level identifiers around this patch are `runtime`, `runtimeReady`, `case`, and `requests`. Nearby tests or test-like files include `go/runtime/host/tests/tester.go`, `go/worker/compute/executor/tests/tester.go`.

## Before/After Behavior

Before the patch, the shown availability check used `n.runtimeReady && lastRoundAvailable`, and the startup path did not include the added trust-sync call in the provided snippet. After the patch, startup invokes `startRuntimeTrustSyncLocked(rt)`, availability additionally requires `n.runtimeTrustSynced`, stop/failure cancels trust sync, and the mock host accepts `RuntimeConsensusSyncRequest` so the new sync path can complete in tests or mocked environments.

# Root Cause

The pre-patch executor readiness logic did not gate registration/availability on completion of runtime trust sync, so a runtime could be treated as available before its trust-root synchronization finished.

## Walkthrough

1. In `go/worker/compute/executor/committee/node.go`, the runtime start path now resets `runtimeTrustSynced` and calls `startRuntimeTrustSyncLocked(rt)` after runtime feature checks.

2. The same file changes the availability predicate from `n.runtimeReady && lastRoundAvailable` to `n.runtimeReady && lastRoundAvailable && n.runtimeTrustSynced`.

3. The runtime failure/stop path now calls `cancelRuntimeTrustSyncLocked()`, tying trust-sync state to runtime lifecycle.

4. `go/runtime/host/mock/mock.go` adds `RuntimeConsensusSyncRequest` handling and returns success, which looks like support code for the new sync flow.

5. The provided `trust.go` excerpt says the helper syncs the runtime light client to the latest height and is a no-op when no trust root is used, matching the new gate without proving a broader exploit scenario.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/worker/compute/executor/committee/node.go | 1405 | runtime startup path resets trust state and initiates runtime trust-root sync before the node is considered serviceable |
| go/worker/compute/executor/committee/node.go | 1374 | executor availability/registration gate now requires `runtimeTrustSynced` in addition to runtime readiness and round availability |
| go/worker/compute/executor/committee/node.go | 1442 | runtime stop/failure path cancels outstanding trust sync so stale verification state is not retained |
| go/worker/compute/executor/committee/trust.go | 2 | helper responsible for syncing the runtime light client to the latest consensus height when a trust root is configured |
| go/runtime/host/mock/mock.go | 160 | mock host support for `RuntimeConsensusSyncRequest`, enabling regression coverage of the new trust-sync handshake |

## Code Snippets

## Snippet 1

Context: `go/runtime/host/mock/mock.go:166` (changes how canonical state is encoded, returned, or reconstructed)

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

## Snippet 2

Context: `go/worker/compute/executor/committee/node.go:1427` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

		// We are now able to service requests for this runtime.
		n.runtimeReady = true
```
After
```go
}

		// If the runtime has a trust root configured, make sure we are able to successfully sync
		// the runtime up to the latest height as otherwise request processing will fail.
		n.startRuntimeTrustSyncLocked(rt)

		// We are now able to service requests for this runtime.
		n.runtimeReady = true
```

## Snippet 3

Context: `go/worker/compute/executor/committee/node.go:1378` (changes how canonical state is encoded, returned, or reconstructed)

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

Context: `go/worker/compute/executor/committee/node.go:1442` (changes how canonical state is encoded, returned, or reconstructed)

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

Add an explicit trust-sync completion flag to readiness/registration checks and manage the associated sync operation during component startup and shutdown.

## How It Was Fixed

The executor now starts runtime trust sync during runtime startup, requires `runtimeTrustSynced` before advertising availability, and cancels outstanding sync work when the runtime stops or fails. Mock runtime support was extended so the new consensus-sync request path can succeed in non-production coverage.

# Why It Matters

1. Prevents the node from advertising availability before trust sync finishes for trust-rooted runtimes.

2. Aligns registration/readiness with the runtime light client's sync state.

3. Reduces premature request handling in a state the new code treats as not yet ready.

4. The evidence shows hardening of lifecycle gating, not a demonstrated cryptographic bypass or attacker exploit.

# Evidence Notes

The strongest evidence is in `go/worker/compute/executor/committee/node.go`: the new startup call, the added `runtimeTrustSynced` readiness condition, and trust-sync cancellation on stop/failure. The comment says request processing would otherwise fail, which supports an operational correctness problem. `go/runtime/host/mock/mock.go` is support code for the new sync handshake, not evidence of root cause by itself. The supplied material does not show prior acceptance of invalid consensus data, remote attacker control, or a confirmed security breach. Protocol security invariant: When a runtime is configured with a trust root, executor availability/registration should wait until runtime trust sync has completed; generic runtime readiness and last-round availability alone are not sufficient. Verification notes: The patch does not prove that unverified consensus data was previously accepted as valid; it proves readiness could be signaled too early. The patch does not show a remote exploit path or attacker-controlled registration abuse. No cryptographic break or trust-root bypass is demonstrated by the diff alone. The observable impact may have been failed request processing or incorrect availability signaling rather than direct state corruption. The visible diff supports a readiness/registration gating change tied to trust sync. The mock change supports test or harness compatibility for the new sync request. No test results, exploit reproduction, or incident evidence were provided. Security relevance is plausible, but the vulnerability thesis is not established by the supplied evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-trust-verification-gating`
Final impact type: `premature-registration, trust-state-exposure`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, trust-root, registration-gating, light-client`

The patch is best treated as security hardening. The code now starts trust-root synchronization on runtime startup, requires `runtimeTrustSynced` before the executor is considered available, and cancels trust-sync state on stop/failure. That is a clear tightening of security-sensitive behavior around trust-root verification and registration. However, the supplied diff does not prove a concrete exploitable vulnerability, prior acceptance of invalid data, or attacker-driven compromise, so this should not be labeled a confirmed security fix.

## Security Evidence

1. Commit subject explicitly says trust root must be verified before registering.
2. Availability gating changed from `runtimeReady && lastRoundAvailable` to also require `runtimeTrustSynced`.
3. Startup path now invokes `startRuntimeTrustSyncLocked(rt)` before the node is treated as ready to service requests.
4. Stop/failure path now cancels outstanding runtime trust sync, preventing stale trust-sync lifecycle state.
5. Project context says the helper syncs the runtime light client to the latest height when a trust root is configured, which is a security-sensitive verification step.

## Missing Evidence

1. No proof that invalid or malicious consensus data was previously accepted.
2. No demonstrated remote attacker path or concrete exploit scenario.
3. No test result, incident report, or reproduction showing security impact beyond premature readiness/registration.
4. Commentary in the patch points to request-processing failure, which also fits correctness/reliability.

## Claim Boundaries

1. Supported claim: registration/availability is now blocked until trust-root sync completes.
2. Supported claim: the patch hardens trust-sensitive lifecycle handling for trust-rooted runtimes.
3. Not supported: a confirmed bypass of consensus verification or trust-root checks.
4. Not supported: direct state corruption, privilege escalation, or attacker-controlled compromise from the pre-patch behavior.
