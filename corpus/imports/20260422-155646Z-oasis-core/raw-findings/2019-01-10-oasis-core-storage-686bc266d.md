---
case_id: case_20190110_686bc266d
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2019-01-10
source_refs:
  - git:686bc266d8ced581d1d2731ac23444d2f6a0a0d5
  - "go/worker/committee/node.go:660"
  - "go/worker/committee/node.go:215"
  - "go/worker/p2p/p2p.go:195"
  - "go/worker/committee/node.go:333"
bug_class: improper-authorization-check
impact_type:
  - unauthorized-message-processing
confidence: medium
tags:
  - p2p
  - authorization
  - state-validation
  - worker
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds earlier peer-authorization and worker-state checks around committee batch handling, but the provided evidence does not establish that this was fixing a proven vulnerability rather than completing or hardening the new Go worker path used in E2E testing.

## Observed Patch Facts

1. In `go/worker/committee/node.go`, the patch replaces `func (n *Node) handleExternalBatch(batch *externalBatch) {` with `func (n *Node) handleExternalBatch(batch *externalBatch) error {`.

2. In `go/worker/committee/node.go`, the patch replaces `// Quick check to see if header is compatible.` with `respCh, err := n.queueExternalBatch(ctx, batchHash, hdr)`.

3. In `go/worker/p2p/p2p.go`, the patch replaces `err := handler.HandlePeerMessage(rawPeerID, message)` with `// Check if peer is authorized to send messages.`.

4. In `go/worker/committee/node.go`, the patch replaces `// Re-register node to increase expiry.` with `// Re-register node to increase expiry. Do this in the background to avoid`.

## Project Context

The changed code sits primarily in `go/worker/committee`, `go/worker`, `go/worker/p2p`, which anchors the finding in the `storage` area of the project. Historical context from `go/worker/committee/group.go`, `go/worker/committee/registration.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/committee/group.go`, `go/worker/committee/registration.go`. The strongest project-level identifiers around this patch are `register`, `batch`, `epoch`, and `logger`. Nearby tests or test-like files include `go/worker/tests/tester.go`.

## Before/After Behavior

Before the change, the shown P2P handler dispatched a runtime message after runtime lookup without the newly added explicit IsPeerAuthorized check, and the external batch handler did not return an error and, in the shown snippet, allowed only leader-or-backup roles. After the change, the P2P path drops unauthorized peers before dispatch, HandleBatchFromCommittee routes through queueExternalBatch and waits for an error result, and handleExternalBatch returns an error, rejects incorrect local state, and uses a worker-or-backup role check.

# Root Cause

The evidence supports only a narrow conclusion: authorization and state validation were not enforced as early or as uniformly as the updated code now enforces them. It does not prove a concrete exploitable root cause beyond that.

## Walkthrough

1. The P2P stream handler now checks handler.IsPeerAuthorized(rawPeerID) before passing the message to the runtime handler.

2. If the peer is unauthorized, the stream is reset and processing stops immediately.

3. The committee batch entrypoint now calls queueExternalBatch and waits for an error result from the worker goroutine instead of relying on only the previous inline path.

4. The external batch handler now returns an error and immediately rejects calls unless the node is in StateWaitingForBatch.

5. The same handler also changes its role gate from leader-or-backup to worker-or-backup, indicating behavior alignment for the new worker path rather than a clearly documented vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/worker/p2p/p2p.go | 166 | P2P ingress authorization gate for runtime committee messages |
| go/worker/committee/node.go | 200 | Committee batch entrypoint rerouted through queued worker-goroutine path with propagated errors |
| go/worker/committee/node.go | 607 | External batch handler now rejects incorrect worker state and enforces worker-or-backup role before processing |

## Code Snippets

## Snippet 1

Context: `go/worker/committee/node.go:660` (changes a consensus- or validator-sensitive branch)

Before
```go
}

func (n *Node) handleExternalBatch(batch *externalBatch) {
	epoch := n.group.GetEpochSnapshot()

	// We can only receive external batches if we are a leader or a backup worker.
	if !epoch.IsLeader() && !epoch.IsBackupWorker() {
		n.logger.Error("got external batch while in incorrect role")
```
After
```go
}

func (n *Node) handleExternalBatch(batch *externalBatch) error {
	// If we are not waiting for a batch, don't do anything.
	if _, ok := n.state.(StateWaitingForBatch); !ok {
		return errIncorrectState
	}
```

## Snippet 2

Context: `go/worker/committee/node.go:215` (changes signature or replay validation logic)

Before
```go
// computed against.
func (n *Node) HandleBatchFromCommittee(ctx context.Context, batchHash hash.Hash, hdr block.Header) error {
	// Quick check to see if header is compatible.
	if !bytes.Equal(hdr.Namespace[:], n.runtimeID) {
```
After
```go
// computed against.
func (n *Node) HandleBatchFromCommittee(ctx context.Context, batchHash hash.Hash, hdr block.Header) error {
	respCh, err := n.queueExternalBatch(ctx, batchHash, hdr)
	if err != nil {
		return err
	}

	// Wait for response from the worker goroutine.
```

## Snippet 3

Context: `go/worker/p2p/p2p.go:195` (changes a sensitive control or state-update path)

Before
```go
}

	err := handler.HandlePeerMessage(rawPeerID, message)
	response := &Message{
```
After
```go
}

	// Check if peer is authorized to send messages.
	if !handler.IsPeerAuthorized(rawPeerID) {
		p.logger.Error("dropping stream from unauthorized peer",
			"runtime_id", message.RuntimeID,
			"peer_id", peerID,
		)
```

## Snippet 4

Context: `go/worker/committee/node.go:333` (changes a sensitive control or state-update path)

Before
```go
}

	// Re-register node to increase expiry.
	if err := n.registerNode(); err != nil {
		n.logger.Error("failed to re-register node",
			"err", err,
		)
	}
```
After
```go
}

	// Re-register node to increase expiry. Do this in the background to avoid
	// blocking on node registration to complete as we can be processing stuff
	// while re-registration is ongoing.
	go func() {
		if err := n.registerNode(); err != nil {
			n.logger.Error("failed to re-register node",
```

# Fix Pattern

Add explicit ingress checks, route work through a single queued path with error propagation, and reject requests early when local state or peer authorization is wrong.

## How It Was Fixed

The code now rejects unauthorized peers at the P2P boundary, routes committee batch handling through queueExternalBatch with a returned error path, and makes handleExternalBatch fail when the node is not in the expected state. These changes tighten validation and make rejection explicit.

# Why It Matters

1. Unauthorized peers are now rejected before message dispatch.

2. External batch handling now fails closed on wrong local state.

3. The worker path has clearer error propagation instead of silent or delayed rejection.

4. The evidence still does not show a demonstrated exploit or impact.

# Evidence Notes

The strongest evidence is the new IsPeerAuthorized check in go/worker/p2p/p2p.go and the new StateWaitingForBatch/error-return behavior in go/worker/committee/node.go. However, the commit subject is "Use new Go compute worker in E2E tests," and the diff spans test and worker-path migration context. That context weakens any claim that this was definitively a vulnerability fix. The provided snippets do not show exploitability, attacker reachability, or a concrete integrity/confidentiality failure. Protocol security invariant: Committee-related messages and external batches should only be accepted from authorized peers and only when the local worker is in the expected role and state for that path. Verification notes: The patch does not prove that unauthorized peers could previously reach a consensus-impacting state transition in production. The patch does not show a concrete confidentiality or integrity break beyond improper message acceptance risk. The commit subject suggests worker/test migration context, so some changes may be enablement for a new path rather than a standalone vulnerability fix. No concrete exploit, attacker prerequisites, or cross-runtime impact is demonstrated by the provided diff alone. No advisory, bug report, or commit message text ties this change to a security issue. The provided snippets show hardening-style checks but not a proven vulnerable behavior in production. Because the evidence is partial and mixed with test/migration context, stronger labels such as confirmed or likely are not supported. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-authorization-check`
Final impact type: `unauthorized-message-processing`
Final confidence: `medium`
Final tags: `p2p, authorization, state-validation, worker, hardening`

The patch clearly adds an explicit authorization gate on inbound P2P messages and tighter state checks before processing external batches. That is security-relevant hardening because it narrows who can drive sensitive worker/committee paths and causes wrong-state requests to fail closed. The evidence does not prove a concrete exploitable vulnerability or show that prior code was definitely reachable by attackers in production, so this should be retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `handleStreamMessages` now rejects unauthorized peers before dispatching runtime messages.
2. Unauthorized peer handling resets the stream and returns immediately, which removes an exposed processing path.
3. `handleExternalBatch` now returns an error and rejects requests unless the node is in `StateWaitingForBatch`.
4. The batch handler also enforces role checks on the worker path, tightening acceptance conditions for committee-related input.

## Missing Evidence

1. No advisory, bug report, or commit message states that a vulnerability was being fixed.
2. The patch does not prove whether authorization was already enforced deeper in `HandlePeerMessage` or related handlers.
3. No concrete attacker model, exploit path, or demonstrated integrity/confidentiality impact is shown.
4. The commit context suggests worker/test migration work, so some changes may be enablement rather than vulnerability remediation.

## Claim Boundaries

1. Supported claim: the patch hardens authorization and state validation on sensitive message-processing paths.
2. Unsupported claim: this commit definitively fixes a proven exploitable security bug.
3. Unsupported claim: prior behavior enabled privilege escalation or consensus compromise in production.
4. Best corpus label from the patch alone is security hardening, not confirmed security fix.
