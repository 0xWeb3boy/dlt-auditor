---
case_id: case_20240704_8e2f08bb2
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: medium
source_quality: medium
date: 2024-07-04
source_refs:
  - git:8e2f08bb287598e945a2b750144082dc3db05859
  - "go/worker/keymanager/churp.go:149"
  - "go/consensus/cometbft/apps/keymanager/churp/txs.go:557"
  - "go/consensus/cometbft/apps/keymanager/churp/txs.go:132"
  - "go/consensus/cometbft/apps/keymanager/churp/txs.go:21"
tags:
  - cryptography
  - access-control
  - consensus
  - rpc
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a security-relevant authorization tightening in the CHURP key-share query path, but it does not fully prove a concrete exploitable vulnerability. The patch replaces a placeholder-style node authorization check with runtime-aware logic and adds consensus validation that rejects non-empty `MayQuery` before feature version `24.2`.

## Observed Patch Facts

1. In `go/worker/keymanager/churp.go`, the patch replaces `func (w *churpWorker) authorizeNode(_ context.Context, peerID core.PeerID) error {` with `func (w *churpWorker) authorizeNode(ctx context.Context, peerID core.PeerID) error {`.

2. In `go/consensus/cometbft/apps/keymanager/churp/txs.go`, the patch adds `func verifyPolicy(ctx *tmapi.Context, policy *churp.SignedPolicySGX) error {`.

3. In `go/consensus/cometbft/apps/keymanager/churp/txs.go`, the patch replaces `state := churpState.NewMutableState(ctx.State())` with `// Make sure the 'MayQuery' field is empty until the next breaking upgrade.`.

4. In `go/consensus/cometbft/apps/keymanager/churp/txs.go`, the patch replaces `state := churpState.NewMutableState(ctx.State())` with `// Make sure the 'MayQuery' field is empty until the next breaking upgrade.`.

## Project Context

The changed code sits primarily in `go/worker/keymanager`, `go/worker`, `go/consensus/cometbft/apps/keymanager/churp`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/worker/keymanager/secrets.go`, `go/worker/keymanager/worker.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/keymanager/secrets.go`, `go/worker/keymanager/worker.go`. The strongest project-level identifiers around this patch are `error`, `MayQuery`, `peerID`, and `verifyPolicy`. Nearby tests or test-like files include `go/worker/compute/executor/tests/tester.go`, `go/worker/storage/tests/tester.go`.

## Before/After Behavior

Before the patch, `RPCMethodKeyShare` authorization in `go/worker/keymanager/churp.go` used a minimal `accessList.Runtimes(peerID).Empty()` check and included a TODO asking which nodes should be allowed to query key shares. `create` and `update` in `go/consensus/cometbft/apps/keymanager/churp/txs.go` also had no shown validation preventing early use of `Policy.MayQuery`. After the patch, key-share authorization consults the runtime descriptor and branches on `rt.TEEHardware`, while `create` and `update` now call `verifyPolicy`, which rejects non-empty `MayQuery` unless feature version `24.2` is enabled.

# Root Cause

The shown code indicates an under-specified authorization boundary for key-share queries and missing admission-time validation for a policy field related to query authorization semantics.

## Walkthrough

1. `go/worker/keymanager/churp.go` routes `churp.RPCMethodKeyShare` to `authorizeNode`, so that function gates key-share query handling.

2. In the pre-patch code, `authorizeNode` ignored `ctx`, relied only on whether `accessList.Runtimes(peerID)` was empty, and carried a TODO indicating the intended authorization rule was unresolved.

3. In the patched code, `authorizeNode` first loads the runtime descriptor and then switches on `rt.TEEHardware`, showing that authorization now depends on runtime context rather than only a broad access-list presence test.

4. In `go/consensus/cometbft/apps/keymanager/churp/txs.go`, both `create` and `update` now call `verifyPolicy` before state preparation.

5. `verifyPolicy` rejects non-empty `policy.Policy.MayQuery` unless feature version `24.2` is enabled, preventing premature use of that field.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/worker/keymanager/churp.go | 122 | Authorizes inbound CHURP enclave RPC methods; routes key-share requests into node authorization. |
| go/worker/keymanager/churp.go | 149 | Node-level authorization logic for `RPCMethodKeyShare`, changed from a generic access-list gate to runtime-aware checks. |
| go/consensus/cometbft/apps/keymanager/churp/txs.go | 132 | Consensus-side validation for CHURP create/update transactions, now rejecting premature `MayQuery` usage. |
| go/consensus/cometbft/apps/keymanager/churp/txs.go | 554 | Feature-gated policy validation that keeps `MayQuery` empty until the protocol version that supports it. |

## Code Snippets

## Snippet 1

Context: `go/worker/keymanager/churp.go:149` (changes a sensitive control or state-update path)

Before
```go
}

func (w *churpWorker) authorizeNode(_ context.Context, peerID core.PeerID) error {
	// TODO: Which nodes are allowed to query key shares?
	if w.kmWorker.accessList.Runtimes(peerID).Empty() {
		return fmt.Errorf("request not allowed")
	}
	return nil
```
After
```go
}

func (w *churpWorker) authorizeNode(ctx context.Context, peerID core.PeerID) error {
	rt, err := w.kmWorker.runtime.RegistryDescriptor(ctx)
	if err != nil {
		return err
	}
```

## Snippet 2

Context: `go/consensus/cometbft/apps/keymanager/churp/txs.go:557` (changes a sensitive control or state-update path)

Before
```go
status.Applications = nil
}
```
After
```go
status.Applications = nil
}

func verifyPolicy(ctx *tmapi.Context, policy *churp.SignedPolicySGX) error {
	// Allow non-empty `MayQuery` field with the 24.2 release.
	enabled, err := features.IsFeatureVersion(ctx, "24.2")
	if err != nil {
		return err
```

## Snippet 3

Context: `go/consensus/cometbft/apps/keymanager/churp/txs.go:132` (changes a sensitive control or state-update path)

Before
```go
func (ext *churpExt) update(ctx *tmapi.Context, req *churp.UpdateRequest) error {
	// Prepare state.
	state := churpState.NewMutableState(ctx.State())
```
After
```go
func (ext *churpExt) update(ctx *tmapi.Context, req *churp.UpdateRequest) error {
	// Make sure the `MayQuery` field is empty until the next breaking upgrade.
	if err := verifyPolicy(ctx, req.Policy); err != nil {
		return err
	}

	// Prepare state.
```

## Snippet 4

Context: `go/consensus/cometbft/apps/keymanager/churp/txs.go:21` (changes a sensitive control or state-update path)

Before
```go
func (ext *churpExt) create(ctx *tmapi.Context, req *churp.CreateRequest) error {
	// Prepare state.
	state := churpState.NewMutableState(ctx.State())
```
After
```go
func (ext *churpExt) create(ctx *tmapi.Context, req *churp.CreateRequest) error {
	// Make sure the `MayQuery` field is empty until the next breaking upgrade.
	if err := verifyPolicy(ctx, &req.Policy); err != nil {
		return err
	}

	// Prepare state.
```

# Fix Pattern

Replace permissive or placeholder authorization checks with context-aware gating, and reject unsupported authorization-related policy fields at transaction admission until the protocol version explicitly enables them.

## How It Was Fixed

The patch tightens worker-side authorization for CHURP key-share queries by consulting runtime descriptor information, and it adds consensus-side validation so `MayQuery` cannot be set before the feature release that supports it.

# Why It Matters

1. Key-share query handling is a security-sensitive path in a key manager subsystem.

2. The old code explicitly signaled incomplete authorization intent via a TODO.

3. Version-gating `MayQuery` reduces ambiguity about authorization semantics before protocol support exists.

4. The evidence supports hardening of confidentiality-related access control, even if exploitability is not proven from the excerpts alone.

# Evidence Notes

The strongest support is the pre-patch TODO plus the weak `accessList.Runtimes(peerID).Empty()` check, and the new worker code that consults `RegistryDescriptor(ctx)` and `rt.TEEHardware`. The consensus excerpts clearly show new `verifyPolicy` enforcement for `MayQuery`. However, the exact post-patch allow/deny rules are only partially visible, and the provided material does not prove that unauthorized key-share access definitely occurred in practice. Rust-side and other cross-component changes are listed but not evidenced here, so they should not be used to strengthen the claim. Protocol security invariant: CHURP key-share query handling should apply explicit authorization rules tied to runtime/policy context, and consensus should not admit `MayQuery` policy state before the protocol version that defines and supports it. Verification notes: The excerpts do not prove that unauthorized key-share extraction was practically exploitable in deployment. The exact secure-TEE allowlist semantics after the patch are only partially visible. The Rust-side changes are not shown, so end-to-end enforcement across all components is inferred but not fully demonstrated. The patch evidence supports a confidentiality/access-control concern, not a proven integrity or availability issue. The claim should stay at hardening/likely-security rather than confirmed exploit fix. No direct proof of attacker-controlled unauthorized key-share disclosure is present in the excerpts. The exact semantics of `MayQuery` and the full secure-TEE authorization matrix are not fully shown. Additional cross-language files were changed, but their behavior is not provided and should not be treated as primary evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final tags: `cryptography, access-control, consensus, rpc`

The supplied patch evidence is sufficient to treat this as a security-hardening change. It tightens authorization on a key-share query path in the key manager subsystem and adds consensus-side validation to block use of the `MayQuery` policy field before the feature version that supports it. Those are security-sensitive controls, and the pre-patch TODO plus broad runtime-membership check indicate an exposed risky condition. However, the excerpts do not fully show the new authorization rules or prove a concrete exploitable vulnerability, so this should not be upgraded to a confirmed security-fix.

## Security Evidence

1. Pre-patch `authorizeNode` contained a TODO asking which nodes may query key shares, indicating unresolved authorization semantics on a sensitive path.
2. The old check only denied peers with an empty runtime access list, which is a broad gate for `RPCMethodKeyShare`.
3. Post-patch `authorizeNode` becomes context-aware by loading the runtime descriptor and branching on `rt.TEEHardware`, showing tighter security-sensitive gating.
4. `create` and `update` now call `verifyPolicy` before state preparation, so unsupported `MayQuery` policy values are rejected at admission time.
5. `verifyPolicy` explicitly keeps non-empty `MayQuery` disabled until feature version `24.2`, reducing premature or ambiguous authorization behavior.

## Missing Evidence

1. The full body of the new `authorizeNode` logic is not shown, so the exact allow/deny matrix is incomplete.
2. The excerpts do not prove that unauthorized peers could successfully extract usable key shares in a real deployment before the patch.
3. Rust-side and other cross-component changes are listed in the commit but not provided as primary evidence here.
4. No advisory, bug report, or regression test excerpt demonstrates a concrete exploit scenario or security impact.

## Claim Boundaries

1. Supported: the commit hardens access control around CHURP key-share queries and restricts early use of `MayQuery`.
2. Supported: the pre-patch code shows an under-specified authorization boundary on a key-manager RPC path.
3. Not supported: a definitive pre-patch confidentiality breach, privilege escalation, or attacker-triggered key disclosure.
4. Not supported: end-to-end security guarantees across all changed Go and Rust components beyond the shown excerpts.
