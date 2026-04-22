---
case_id: case_20221208_52536d293
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2022-12-08
source_refs:
  - git:52536d29300a0c25b0f8865306fd625d8e727143
  - "go/runtime/registry/host.go:505"
  - "go/runtime/registry/host.go:545"
  - "runtime/src/dispatcher.rs:1017"
  - "go/runtime/registry/host.go:621"
bug_class: quote-policy-synchronization
impact_type:
  - stale-security-policy
  - attestation-verification-weakening
confidence: medium
tags:
  - attestation
  - sgx
  - quote-policy
  - rpc
  - policy-sync
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a dedicated path to propagate key-manager quote policy updates from the host into the runtime and refreshes that state on epoch changes that may reflect redeployment. That is security-relevant attestation plumbing, but the provided evidence does not by itself prove that invalid RPC quotes were previously accepted or that quote verification was fully bypassed before the change.

## Observed Patch Facts

1. In `go/runtime/registry/host.go`, the patch replaces `// Subscribe to key manager status updates.` with `// Subscribe to key manager status updates (policy might change).`.

2. In `go/runtime/registry/host.go`, the patch replaces `case ev := <-evCh:` with `case epoch := <-epoCh:`.

3. In `runtime/src/dispatcher.rs`, the patch adds `fn handle_km_quote_policy_update(`.

4. In `go/runtime/registry/host.go`, the patch replaces `func (n *runtimeHostNotifier) watchConsensusLightBlocks() {` with `func (n *runtimeHostNotifier) updateKeyManagerQuotePolicy(ctx context.Context, policy...`.

## Project Context

The changed code sits primarily in `go/runtime/registry`, `go/runtime`, `runtime/src`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `runtime/src/policy.rs`, `runtime/src/protocol.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/protocol.rs`, `runtime/src/policy.rs`. The strongest project-level identifiers around this patch are `policy`, `manager`, `quote`, and `logger`. Nearby tests or test-like files include `go/runtime/host/tests/tester.go`, `runtime/src/storage/mkvs/tests/mod.rs`.

## Before/After Behavior

Before the patch, the shown host-side update flow propagated signed key-manager policy and reacted to runtime host events, but the provided snippets do not show a separate quote-policy update path into the runtime. After the patch, the host also watches epochs because quote policy may change on redeploy, queries the current runtime descriptor on epoch transitions, sends a RuntimeKeyManagerQuotePolicyUpdateRequest carrying QuotePolicy, and the runtime dispatcher gains a handler for that update.

# Root Cause

The pre-fix design appears to have lacked an explicit mechanism to keep key-manager quote-policy state synchronized inside the runtime, especially across epoch/redeploy-driven changes. The evidence supports a state-synchronization gap in attestation policy handling more clearly than a proven verification bypass.

## Walkthrough

1. In go/runtime/registry/host.go, quote-policy changes are explicitly tied to epoch transitions, with comments saying quote policy might change when the key manager is redeployed.

2. The host adds an epoch-triggered refresh that re-queries the key manager runtime descriptor, indicating the previous triggers were not sufficient for this state.

3. The host adds updateKeyManagerQuotePolicy, which sends RuntimeKeyManagerQuotePolicyUpdateRequest with a QuotePolicy payload to the runtime.

4. In runtime/src/dispatcher.rs, a new handle_km_quote_policy_update entry point is added, showing that quote-policy updates are now consumed as runtime state.

5. These changes support the claim that quote-policy synchronization was missing or incomplete; they do not directly show the exact pre-fix verification logic or an exploit path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/runtime/registry/host.go | 499 | Consensus-side notifier that now watches key manager status and epoch changes so quote policy updates are not missed. |
| go/runtime/registry/host.go | 545 | Epoch-driven refresh path that re-queries the key manager runtime descriptor when a new quote policy may take effect after redeploy. |
| go/runtime/registry/host.go | 621 | Host-to-runtime propagation path for RuntimeKeyManagerQuotePolicyUpdateRequest carrying the active quote policy into the runtime. |
| runtime/src/dispatcher.rs | 1017 | Runtime-side handler that receives key manager quote policy updates and feeds the attestation/verification state used by enclave RPC. |

## Code Snippets

## Snippet 1

Context: `go/runtime/registry/host.go:505` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
n.logger.Debug("watching key manager policy updates", "keymanager", kmRtID)

	// Subscribe to key manager status updates.
	stCh, stSub := n.consensus.KeyManager().WatchStatuses()
	defer stSub.Close()

	// Subscribe to runtime host events.
	evCh, evSub, err := n.host.WatchEvents(n.ctx)
```
After
```go
n.logger.Debug("watching key manager policy updates", "keymanager", kmRtID)

	// Subscribe to key manager status updates (policy might change).
	stCh, stSub := n.consensus.KeyManager().WatchStatuses()
	defer stSub.Close()

	// Subscribe to epoch transitions (quote policy might change).
	epoCh, sub, err := n.consensus.Beacon().WatchEpochs(ctx)
```

## Snippet 2

Context: `go/runtime/registry/host.go:545` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}
			st = newSt
			n.updateKeyManagerPolicy(ctx, st.Policy)
		case ev := <-evCh:
			// Runtime host changes, make sure to update the policy if runtime is restarted.
			if ev.Started == nil && ev.Updated == nil {
				continue
			}
```
After
```go
}
			st = newSt

			n.updateKeyManagerPolicy(ctx, st.Policy)
		case epoch := <-epoCh:
			// Check if the key manager was redeployed, as that is when a new quote policy might
			// take effect.
			dsc, err := n.consensus.Registry().GetRuntime(ctx, &registry.GetRuntimeQuery{
```

## Snippet 3

Context: `runtime/src/dispatcher.rs:1017` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
Ok(Body::RuntimeKeyManagerPolicyUpdateResponse {})
    }
}
```
After
```rust
Ok(Body::RuntimeKeyManagerPolicyUpdateResponse {})
    }

    fn handle_km_quote_policy_update(
        &self,
        ctx: Context,
        state: State,
        quote_policy: QuotePolicy,
```

## Snippet 4

Context: `go/runtime/registry/host.go:621` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (n *runtimeHostNotifier) watchConsensusLightBlocks() {
	rawCh, sub, err := n.consensus.WatchBlocks(n.ctx)
```
After
```go
}

func (n *runtimeHostNotifier) updateKeyManagerQuotePolicy(ctx context.Context, policy *quote.Policy) {
	n.logger.Debug("got key manager quote policy update", "policy", policy)

	req := &protocol.Body{RuntimeKeyManagerQuotePolicyUpdateRequest: &protocol.RuntimeKeyManagerQuotePolicyUpdateRequest{
		Policy: *policy,
	}}
```

# Fix Pattern

Add an explicit host-to-runtime propagation path for security policy state and refresh it on the consensus events that can change that policy.

## How It Was Fixed

The fix introduces quote-policy update delivery into the runtime, adds epoch-based refresh logic because quote policy may change on redeploy, and adds a runtime-side handler to receive the new policy state. This makes the quote policy available to the runtime along the same trust path as other key-manager policy updates.

# Why It Matters

1. Attestation decisions should not depend on stale local policy state.

2. Redeploy- or epoch-driven policy changes can be missed if the update triggers are too narrow.

3. A dedicated propagation path reduces the risk of runtime and consensus policy state diverging.

# Evidence Notes

Grounded evidence exists for new epoch watching, runtime-descriptor refresh, a new RuntimeKeyManagerQuotePolicyUpdateRequest sender, and a new runtime handler for quote-policy updates. The commit subject suggests RPC quote verification is the motivating use case, but the provided snippets do not show the actual quote-verification call site before and after, so stronger claims about a concrete acceptance bypass are not established. Protocol security invariant: If enclave RPC quote verification depends on the key manager's consensus-published SGX quote policy, the runtime must receive and refresh that policy when it changes so verification does not rely on stale local state. Verification notes: The patch does not prove that enclave RPC quotes were previously accepted with no verification at all; stale or incomplete policy application is also consistent with the diff. The patch does not show a demonstrated exploit, remote compromise, or signature forgery path. The patch does not establish how long any acceptance window lasted or which deployment patterns were affected. The patch evidence is specific to SGX/key-manager quote-policy enforcement in enclave RPC, not a general consensus or storage integrity flaw. The evidence supports a security-relevant policy-synchronization change. The evidence does not prove that quote verification was absent before the patch. No exploit scenario, affected window, or impact scope is demonstrated in the supplied snippets. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `quote-policy-synchronization`
Final impact type: `stale-security-policy, attestation-verification-weakening`
Final confidence: `medium`
Final tags: `attestation, sgx, quote-policy, rpc, policy-sync`

The supplied evidence supports retaining this as a security-hardening case. The commit subject explicitly ties the change to verifying RPC quotes with the key manager quote policy, and the patch adds a new host-to-runtime quote-policy update path plus epoch-driven refresh logic for redeploys. That is clearly security-sensitive attestation plumbing and reduces the risk of quote verification using stale or missing policy state. However, the provided snippets do not directly show the pre-fix verification path accepting invalid quotes or fully skipping verification, so the safer classification is hardening rather than a confirmed exploitable security fix.

## Security Evidence

1. Commit subject says RPC quotes are verified with key manager quote policy.
2. Patch adds explicit RuntimeKeyManagerQuotePolicyUpdateRequest delivery to the runtime.
3. Runtime dispatcher gains a dedicated quote-policy update handler.
4. Host now watches epochs because quote policy may change on redeploy.
5. Change is in SGX/key-manager/attestation-related runtime code paths.

## Missing Evidence

1. No before/after quote-verification call site is shown.
2. No proof that invalid RPC quotes were accepted before the patch.
3. No exploit scenario, attack preconditions, or affected window are demonstrated.
4. No test evidence is included here showing a previously failing security case.

## Claim Boundaries

1. Supported claim: quote-policy state synchronization for RPC quote verification was tightened.
2. Supported claim: stale or missing quote policy in the runtime was treated as a risk worth fixing.
3. Not supported: a proven authentication or attestation bypass existed before the patch.
4. Not supported: concrete impact such as remote compromise, signature forgery, or broad integrity failure.
