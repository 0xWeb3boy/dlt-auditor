---
case_id: case_20241003_0d2f546b2
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: medium
date: 2024-10-03
source_refs:
  - git:0d2f546b23794f299db4a28ea720dc54481d43a6
  - "runtime/src/enclave_rpc/client.rs:109"
  - "runtime/src/enclave_rpc/client.rs:884"
  - "runtime/src/enclave_rpc/demux.rs:82"
  - "runtime/src/enclave_rpc/sessions.rs:177"
bug_class: stale-session-state
impact_type:
  - stale-trust-policy
  - session-state-confusion
confidence: medium
tags:
  - session-management
  - rpc
  - enclave-identity
  - concurrency
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The diff shows concurrent-session support plus hardening-like cleanup in the enclave RPC layer. The clearest security-relevant change is that `update_enclaves` now drains sessions when the remote enclave identity set changes, but the provided evidence does not establish a concrete vulnerability or exploit path.

## Observed Patch Facts

1. In `runtime/src/enclave_rpc/client.rs`, the patch replaces `async fn send_peer_feedback(&mut self, pf: types::PeerFeedback) {` with `async fn send_peer_feedback(&mut self, feedback: types::PeerFeedback) {`.

2. In `runtime/src/enclave_rpc/client.rs`, the patch replaces `rt.block_on(client.flush_cmd_queue()).unwrap(); // Flush cmd queue to get peer feedback.` with `(13, types::PeerFeedback::Failure), // Failed call due to induced error.`.

3. In `runtime/src/enclave_rpc/demux.rs`, the patch replaces `sessions.add(session, now)?` with `sessions`.

4. In `runtime/src/enclave_rpc/sessions.rs`, the patch replaces `/// Update remote enclave identity verification in the session builder.` with `/// Update remote enclave identity verification in the session builder`.

## Project Context

The changed code sits primarily in `runtime/src/enclave_rpc`, `runtime/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/enclave_rpc/types.rs`, `runtime/src/enclave_rpc/transport.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/enclave_rpc/transport.rs`, `runtime/src/enclave_rpc/types.rs`. The strongest project-level identifiers around this patch are `PeerFeedback`, `types::PeerFeedback`, `types::PeerFeedback::Failure`, and `session`. Nearby tests or test-like files include `runtime/src/storage/mkvs/tests/mod.rs`.

## Before/After Behavior

Before the patch, `update_enclaves` returned a boolean and did not show session teardown on enclave-identity changes; after the patch it returns drained sessions and documents that all sessions are cleared when the identity set changes. Before the patch, peer feedback was enqueued through a weak command queue; after the patch it is submitted directly on the transport using the saved `request_id`. A test was updated to remove queue flushing and to check feedback history across multiple request IDs. The demux path now asserts that adding a new responder session after cleanup must succeed.

# Root Cause

The visible issue is stale or shared session/request state management in the concurrent enclave RPC path. The evidence supports that session state was not explicitly cleared when remote enclave identity policy changed, and that peer feedback previously went through shared queue-based bookkeeping instead of direct request-bound submission.

## Walkthrough

1. `runtime/src/enclave_rpc/sessions.rs` changed `update_enclaves` from a boolean-returning update to a method that returns drained sessions and documents clearing all sessions when enclave identities change.

2. That is direct evidence that existing sessions are now discarded on policy change, whereas the previous snippet did not show that behavior.

3. `runtime/src/enclave_rpc/client.rs` changed `send_peer_feedback` from queueing `Command::PeerFeedback(request_id, ...)` via `cmdq` to calling `self.transport.submit_peer_feedback(request_id, feedback).await`.

4. The client test removed `flush_cmd_queue()` and now expects feedback history with multiple request IDs, which supports a behavior change in concurrent feedback attribution.

5. `runtime/src/enclave_rpc/demux.rs` changed `sessions.add(session, now)?` to `.expect("there should be space for the new session")` after removing prior per-peer state, making an internal assumption explicit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/enclave_rpc/sessions.rs | 177 | invalidate all active RPC sessions when remote enclave identity verification settings change |
| runtime/src/enclave_rpc/demux.rs | 71 | create or replace per-peer responder sessions in the multiplexed concurrent-session path |
| runtime/src/enclave_rpc/client.rs | 106 | submit request-scoped peer feedback directly through the transport for concurrent calls |
| runtime/src/enclave_rpc/client.rs | 878 | regression coverage for feedback attribution across concurrent/in-flight requests |

## Code Snippets

## Snippet 1

Context: `runtime/src/enclave_rpc/client.rs:109` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
/// Send peer feedback.
    async fn send_peer_feedback(&mut self, pf: types::PeerFeedback) {
        if let Some(request_id) = self.request_id.take() {
            // Only count feedback once.
            if let Some(cmdq) = self.cmdq.upgrade() {
                let _ = cmdq.send(Command::PeerFeedback(request_id, pf)).await;
            }
```
After
```rust
/// Send peer feedback.
    async fn send_peer_feedback(&mut self, feedback: types::PeerFeedback) {
        if let Some(request_id) = self.request_id.take() {
            // Only count feedback once.
            let _ = self
                .transport
                .submit_peer_feedback(request_id, feedback)
```

## Snippet 2

Context: `runtime/src/enclave_rpc/client.rs:884` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
})
            .unwrap();
        rt.block_on(client.flush_cmd_queue()).unwrap(); // Flush cmd queue to get peer feedback.
        assert_eq!(result, 46, "insecure call should work");
        assert_eq!(
            transport.take_peer_feedback_history(),
            vec![
                (14, types::PeerFeedback::Failure), // Failed call due to induced error.
```
After
```rust
})
            .unwrap();
        assert_eq!(result, 46, "insecure call should work");
        assert_eq!(
            transport.take_peer_feedback_history(),
            vec![
                (13, types::PeerFeedback::Failure), // Failed call due to induced error.
                (14, types::PeerFeedback::Success), // Handled call.
```

## Snippet 3

Context: `runtime/src/enclave_rpc/demux.rs:82` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
let _ = sessions.remove_for(&peer_id, now)?;
                    let session = sessions.create_responder(peer_id, session_id);
                    sessions.add(session, now)?
                }
            }
```
After
```rust
let _ = sessions.remove_for(&peer_id, now)?;
                    let session = sessions.create_responder(peer_id, session_id);
                    sessions
                        .add(session, now)
                        .expect("there should be space for the new session")
                }
            }
```

## Snippet 4

Context: `runtime/src/enclave_rpc/sessions.rs:177` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    /// Update remote enclave identity verification in the session builder.
    pub fn update_enclaves(&mut self, enclaves: Option<HashSet<EnclaveIdentity>>) -> bool {
        if self.builder.get_remote_enclaves() == &enclaves {
            return false;
        }
```
After
```rust
}

    /// Update remote enclave identity verification in the session builder
    /// and clear all sessions if the identity has changed.
    pub fn update_enclaves(
        &mut self,
        enclaves: Option<HashSet<EnclaveIdentity>>,
    ) -> Vec<SharedSession<PeerID>> {
```

# Fix Pattern

Clear cached session state when trust-policy inputs change, and move per-request side effects from shared asynchronous bookkeeping to the transport/request path that already owns the request identifier.

## How It Was Fixed

The patch makes `update_enclaves` drain sessions when the remote enclave identity set changes, switches peer-feedback submission to direct transport submission keyed by `request_id`, and tightens a responder-session creation invariant with an `expect` after cleanup. The accompanying test was updated for concurrent feedback behavior without command-queue flushing.

# Why It Matters

1. Stale sessions after identity-policy changes can preserve outdated trust decisions.

2. Direct per-request feedback submission is simpler than queue-based attribution under concurrency.

3. The diff suggests hardening of sensitive state transitions in a secure RPC subsystem.

4. The provided evidence does not prove auth bypass, impersonation, or other concrete exploitation.

# Evidence Notes

The strongest grounded evidence is `sessions.rs`, where `update_enclaves` now drains sessions on identity changes. The client feedback change and test update support a concurrency/bookkeeping change, not a proven security flaw. The demux `expect` is an internal invariant assertion, not by itself evidence of a vulnerability fix. The commit subject and diff framing point to feature work ('Support concurrent sessions') with some security-relevant cleanup, but not an established vulnerability. Protocol security invariant: If the allowed remote enclave identity set changes, cached secure RPC sessions should not continue unchanged under the old policy. Request-scoped peer feedback should remain tied to the originating request even when multiple sessions are active. Verification notes: The diff does not prove an externally reachable auth bypass or enclave impersonation bug. The patch does not show message forgery, key disclosure, or cryptographic primitive failure. It is not proven that misrouted peer feedback had consensus, slashing, or availability impact beyond local bookkeeping. The commit is primarily framed as concurrent-session support, so security relevance is inferred from session invalidation and state-isolation behavior rather than an explicit vulnerability statement. No commit message text or advisory in the provided input states a vulnerability. The exploitability of retaining sessions across identity-policy changes is inferred, not demonstrated. The security impact of the peer-feedback routing change is not established by the snippets alone. The caller-side handling of drained sessions is not shown in the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `stale-session-state`
Final impact type: `stale-trust-policy, session-state-confusion`
Final confidence: `medium`
Final tags: `session-management, rpc, enclave-identity, concurrency`

The patch does not show a proven exploitable vulnerability, and the commit is primarily framed as concurrent-session support. However, the `sessions.rs` change is a clear security-sensitive tightening: when the allowed remote enclave identity set changes, existing secure RPC sessions are now drained instead of being left alive under prior trust assumptions. That is credible security hardening in an enclave-authenticated RPC subsystem. The peer-feedback routing changes and test updates support safer request/session isolation under concurrency, but they do not independently prove a security bug.

## Security Evidence

1. `update_enclaves` now explicitly clears all sessions when remote enclave identity verification inputs change.
2. The changed code sits in a secure inter-enclave RPC/session subsystem that uses enclave identity and quote policy concepts.
3. The patch replaces shared queue-based peer feedback submission with direct transport submission keyed by `request_id`, which tightens request-scoped attribution under concurrency.
4. Regression coverage was updated to assert peer-feedback history across multiple request IDs, indicating deliberate handling of concurrent in-flight state.

## Missing Evidence

1. No commit message, advisory, or test explicitly states a security vulnerability was fixed.
2. The patch does not demonstrate that stale sessions previously allowed unauthorized peers or bypassed enclave identity checks in practice.
3. Caller-side handling of drained sessions is not shown, so end-to-end security effect is inferred rather than proven.
4. No evidence shows confidentiality, integrity, or authentication compromise beyond security-sensitive state cleanup.

## Claim Boundaries

1. Treat this as security hardening, not a confirmed exploitable security fix.
2. The strongest supported claim is session invalidation on trust-policy change in a security-sensitive RPC path.
3. Do not claim cryptographic breakage, enclave impersonation, or auth bypass from the provided diff alone.
4. The peer-feedback changes support concurrency-safe state attribution, but their direct security impact is only suggestive.
