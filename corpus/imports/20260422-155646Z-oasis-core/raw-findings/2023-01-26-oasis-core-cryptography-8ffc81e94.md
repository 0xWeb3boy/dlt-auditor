---
case_id: case_20230126_8ffc81e94
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2023-01-26
source_refs:
  - git:8ffc81e9472042e0e545079e7ea736ceae2f1e25
  - "runtime/src/enclave_rpc/session.rs:276"
  - "runtime/src/enclave_rpc/client.rs:477"
  - "runtime/src/enclave_rpc/session.rs:434"
  - "go/runtime/registry/host.go:186"
bug_class: insufficient-peer-identity-verification
impact_type:
  - identity-misbinding
tags:
  - rpc
  - noise
  - key-manager
  - peer-authentication
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports security hardening for explicit-member key manager RPCs, not a clearly established fix for a pre-existing exploitable vulnerability. The patch adds plumbing for selected-node identity and session-side checks so explicit peer selection can be verified in the Noise path.

## Observed Patch Facts

1. In `runtime/src/enclave_rpc/session.rs`, the patch replaces `pub fn is_closed(&self) -> bool {` with `/// Whether the session is connected to one of the given nodes.`.

2. In `runtime/src/enclave_rpc/client.rs`, the patch replaces `session.builder = mem::take(&mut session.builder).quote_policy(Some(Arc::new(policy)));` with `let policy = Some(Arc::new(policy));`.

3. In `runtime/src/enclave_rpc/session.rs`, the patch replaces `/// Configure quote policy used for remote quote verification.` with `/// Return remote runtime ID if configured in the builder.`.

4. In `go/runtime/registry/host.go`, the patch replaces `res, err := kmCli.CallEnclave(ctx, rq.Request, nil, rq.Kind, rq.PeerFeedback)` with `res, node, err := kmCli.CallEnclave(ctx, rq.Request, rq.Nodes, rq.Kind, rq.PeerFeedback)`.

## Project Context

The changed code sits primarily in `runtime/src/enclave_rpc`, `runtime/src`, `go/runtime/registry`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/enclave_rpc/demux.rs`, `runtime/src/enclave_rpc/dispatcher.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/dispatcher.rs`, `runtime/src/enclave_rpc/demux.rs`. The strongest project-level identifiers around this patch are `session`, `policy`, `mem::take`, and `Arc::new`. Nearby tests or test-like files include `go/runtime/host/tests/tester.go`, `runtime/src/storage/mkvs/tests/mod.rs`.

## Before/After Behavior

Before the change, the shown host RPC path returned only the RPC response, and the shown session/builder APIs did not expose the added helpers for checking or retrieving the remote node or configuring remote runtime identity. After the change, the host can pass explicit node selections into `CallEnclave`, return the selected node for explicit-member requests, and the session/builder APIs expose state used for remote identity verification in the Noise path.

# Root Cause

Explicit-member routing needed additional identity-binding state across the host/session boundary. The provided evidence shows that this state was previously not exposed in the relevant APIs, so explicit peer selection could not be tied as directly to session identity verification as it is after the patch.

## Walkthrough

1. `go/runtime/registry/host.go` changes the key manager RPC path to receive both `res` and `node` from `CallEnclave` and return `Node` for explicit-member requests.

2. `runtime/src/enclave_rpc/session.rs` adds `is_connected_to(...)` and `get_node()`, both operating on `remote_node`, which exposes session peer identity to callers.

3. The same session file adds builder accessors for `remote_runtime_id`, and the comment explicitly says this is for remote node identity verification.

4. `runtime/src/enclave_rpc/client.rs` shows session configuration updates being compared before reset, consistent with rebuilding sessions when verification-relevant inputs change.

5. The commit message states the intended security property: in Noise sessions, the enclave obtains the selected instance's trusted RAK from consensus and compares it to the session peer key.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/runtime/registry/host.go | 186 | Host-side key manager RPC path now returns the selected remote node identity for explicit-member calls. |
| runtime/src/enclave_rpc/session.rs | 276 | Session tracks and checks whether it is connected to one of the expected remote nodes; exposes remote node identity. |
| runtime/src/enclave_rpc/session.rs | 434 | Session builder carries remote runtime identity configuration used for remote node identity verification. |
| runtime/src/enclave_rpc/client.rs | 477 | RPC client updates session verification inputs and resets sessions when identity-relevant parameters change. |

## Code Snippets

## Snippet 1

Context: `runtime/src/enclave_rpc/session.rs:276` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    /// Whether the session is in closed state.
    pub fn is_closed(&self) -> bool {
        matches!(self.state, State::Closed)
    }
}
```
After
```rust
}

    /// Whether the session is connected to one of the given nodes.
    pub fn is_connected_to(&self, nodes: &Vec<signature::PublicKey>) -> bool {
        nodes.iter().any(|&node| Some(node) == self.remote_node)
    }

    /// Whether the session is in closed state.
```

## Snippet 2

Context: `runtime/src/enclave_rpc/client.rs:477` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
/// Update key manager's quote policy.
    pub fn update_quote_policy(&self, policy: QuotePolicy) {
        let mut session = self.inner.session.lock().unwrap();
        session.builder = mem::take(&mut session.builder).quote_policy(Some(Arc::new(policy)));
        session.reset();
    }
}
```
After
```rust
/// Update key manager's quote policy.
    pub fn update_quote_policy(&self, policy: QuotePolicy) {
        let policy = Some(Arc::new(policy));
        let mut session = self.inner.session.lock().unwrap();
        if session.builder.get_quote_policy() == &policy {
            return;
        }
        session.builder = mem::take(&mut session.builder).quote_policy(policy);
```

## Snippet 3

Context: `runtime/src/enclave_rpc/session.rs:434` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    /// Configure quote policy used for remote quote verification.
    pub fn quote_policy(mut self, policy: Option<Arc<QuotePolicy>>) -> Self {
```
After
```rust
}

    /// Return remote runtime ID if configured in the builder.
    pub fn get_remote_runtime_id(&self) -> &Option<Namespace> {
        &self.remote_runtime_id
    }

    /// Set remote runtime ID for node identity verification.
```

## Snippet 4

Context: `go/runtime/registry/host.go:186` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return nil, err
		}
		res, err := kmCli.CallEnclave(ctx, rq.Request, nil, rq.Kind, rq.PeerFeedback)
		if err != nil {
			return nil, err
		}
		return &protocol.HostRPCCallResponse{
			Response: cbor.FixSliceForSerde(res),
```
After
```go
return nil, err
		}
		res, node, err := kmCli.CallEnclave(ctx, rq.Request, rq.Nodes, rq.Kind, rq.PeerFeedback)
		if err != nil {
			return nil, err
		}
		// Don't send node identity if the runtime doesn't support explicit key manager RPC calls.
		if rq.Nodes == nil {
```

# Fix Pattern

Add peer-identity plumbing and bind explicit peer selection to authenticated session state in the secure transport path.

## How It Was Fixed

The patch threads the selected key manager node through the host RPC response, exposes remote-node identity from the session, and adds builder/client state used for remote identity verification. Per the commit message, Noise sessions then verify the selected member against consensus-derived trusted RAK material.

# Why It Matters

1. Explicit-member requests need identity binding, not just host-side routing.

2. Returning the selected node lets the enclave verify it talked to the intended member.

3. The evidence supports stronger peer verification specifically in Noise sessions.

4. This is grounded as hardening for a sensitive path, not proof of a prior exploitable impersonation bug.

# Evidence Notes

The strongest direct evidence is the combination of: host RPC changes in `go/runtime/registry/host.go`, session peer-identity helpers in `runtime/src/enclave_rpc/session.rs`, builder support for `remote_runtime_id`, and the commit message explicitly describing Noise-session verification against consensus-derived trusted RAKs. The provided diff does not establish exploitation of prior behavior, compromise of consensus identity data, or equivalent verification for non-Noise transports. Protocol security invariant: For explicit key manager member calls over Noise, the enclave must learn which node was selected and bind the authenticated session to that intended member using trusted identity material from consensus. Verification notes: The patch does not prove that the pre-change behavior allowed a practical attacker to impersonate a key manager node. The evidence only clearly supports identity verification in Noise sessions, not in every transport or legacy RPC mode. The patch does not show that consensus RAK distribution itself was previously wrong or compromised. The removal of sticky-node behavior is not, by itself, evidence of a security flaw. The security-relevant behavior is supported mainly by the commit message plus the API changes shown in the diff snippets. The evidence is sufficient to classify this as security hardening in a sensitive authentication path. The evidence is not sufficient to confirm a concrete pre-patch vulnerability or broader impact outside the explicit-member Noise path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-peer-identity-verification`
Final impact type: `identity-misbinding`
Final tags: `rpc, noise, key-manager, peer-authentication`

The patch is feature-oriented, but the supplied evidence still shows a real security hardening change in a sensitive RPC path. The commit message explicitly says explicit key-manager member calls now verify the remote node identity in Noise sessions by comparing the session peer key against trusted consensus-derived RAK material, and the shown code adds the node plumbing and builder/session state needed for that verification. The evidence does not establish a concrete pre-existing exploitable vulnerability, so this should be retained only as security hardening, not as a confirmed security fix.

## Security Evidence

1. The commit message explicitly describes remote node identity verification in Noise sessions using trusted RAKs from consensus.
2. `session.rs` adds remote-node accessors and membership checks tied to `remote_node`, which supports binding a session to an expected peer.
3. `session.rs` builder comments explicitly say `remote_runtime_id` is for node identity verification.
4. `host.go` starts returning the selected node for explicit-member RPC calls, enabling the enclave side to verify which peer was actually contacted.
5. The change affects key-manager enclave RPCs, a cryptographic/authentication-sensitive path.

## Missing Evidence

1. The provided patch snippets do not show the full code that performs the actual RAK comparison during session establishment.
2. There is no direct evidence that pre-patch behavior was exploitable by an attacker in practice.
3. The evidence does not show equivalent verification behavior for non-Noise transports or broader RPC modes.

## Claim Boundaries

1. Treat this as hardening of explicit key-manager member RPCs, not proof of a previously exploitable vulnerability.
2. Do not generalize the claim beyond the Noise-session path described in the commit message.
3. Do not keep the original serialization/state-consistency framing; the supported issue is peer identity verification/binding in RPC sessions.
