---
case_id: case_20230504_73f310c0e2
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
impact_type:
  - state-consistency
  - client-view-divergence
source_quality: medium
date: 2023-05-04
source_refs:
  - git:73f310c0e29a60e7d45bc10a082506eef28a3d2c
  - "proxyd/backend.go:647"
  - "proxyd/backend.go:605"
  - "proxyd/backend.go:91"
  - "proxyd/rewriter.go:1"
bug_class: insufficient-consensus-validation
confidence: medium
tags:
  - blockchain-core
  - rpc-client-api
  - consensus
  - request-validation
  - block-tag-rewrite
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a consensus-bound rewrite stage for proxyd requests before backend forwarding. The evidence supports a correctness and consistency fix in the consensus-aware path, but it does not establish a concrete vulnerability or exploit, so this should not be kept as a confirmed security fix.

## Observed Patch Facts

1. In `proxyd/backend.go`, the patch replaces `res, err := back.Forward(ctx, rpcReqs, isBatch)` with `res := make([]*RPCRes, 0)`.

2. In `proxyd/backend.go`, the patch replaces `backends = b.loadBalancedConsensusGroup()` with `overriddenResponses := make([]*indexedReqRes, 0)`.

3. In `proxyd/backend.go`, the patch replaces `ErrBackendUnexpectedJSONRPC = errors.New("backend returned an unexpected JSON-RPC res...` with `ErrBlockOutOfRange = &RPCErr{`.

4. In `proxyd/rewriter.go`, the patch changes a sensitive implementation path.

## Project Context

Historical context from `proxyd/backend_rate_limiter.go`, `proxyd/server.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `proxyd/server.go`, `proxyd/proxyd.go`. The strongest project-level identifiers around this patch are `backend`, `errors`, `group`, and `rpcReqs`. Nearby tests or test-like files include `proxyd/integration_tests/mock_backend_test.go`, `proxyd/integration_tests/ws_test.go`.

## Before/After Behavior

Before the patch, consensus mode selected a consensus backend set and forwarded the original requests directly. After the patch, the proxy derives the current consensus block, runs requests through RewriteTags, may synthesize local responses or return a new "block is out of range" error, and only forwards the remaining rewritten requests.

# Root Cause

The consensus-aware forwarding path enforced backend selection but, based on the provided evidence, did not also enforce block-tag or block-number compliance with the tracked consensus height before forwarding requests.

## Walkthrough

1. `BackendGroup.Forward` previously switched to `loadBalancedConsensusGroup()` in consensus mode and then forwarded `rpcReqs` as-is.

2. The patch adds `overriddenResponses` and `rewrittenReqs`, showing a new pre-forward classification step.

3. In consensus mode, the code now builds `RewriteContext{latest: b.Consensus.GetConsensusBlockNumber()}`.

4. Each request is passed through `RewriteTags`, which can override the response, override the request, or leave it unchanged.

5. A new `ErrBlockOutOfRange` RPC error is introduced and used when rewriting detects an out-of-range request.

6. The backend loop now only calls `back.Forward` if there are rewritten requests left to send.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| proxyd/backend.go | 600 | consensus-aware RPC forwarding path now rewrites block-tagged requests and may override responses before backend dispatch |
| proxyd/rewriter.go | 1 | block tag / block number rewrite logic keyed off the consensus latest block |
| proxyd/backend.go | 85 | client-visible error mapping for requests deemed outside the allowed consensus range |

## Code Snippets

## Snippet 1

Context: `proxyd/backend.go:647` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
for _, back := range backends {
		res, err := back.Forward(ctx, rpcReqs, isBatch)
		if errors.Is(err, ErrMethodNotWhitelisted) {
			return nil, err
		}
		if errors.Is(err, ErrBackendOffline) {
			log.Warn(
```
After
```go
for _, back := range backends {
		res := make([]*RPCRes, 0)
		var err error

		if len(rpcReqs) > 0 {
			res, err = back.Forward(ctx, rpcReqs, isBatch)
			if errors.Is(err, ErrMethodNotWhitelisted) {
```

## Snippet 2

Context: `proxyd/backend.go:605` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
backends := b.Backends

	// When `consensus_aware` is set to `true`, the backend group acts as a load balancer
	// serving traffic from any backend that agrees in the consensus group
	if b.Consensus != nil {
		backends = b.loadBalancedConsensusGroup()
	}
```
After
```go
backends := b.Backends

	overriddenResponses := make([]*indexedReqRes, 0)
	rewrittenReqs := make([]*RPCReq, 0, len(rpcReqs))

	if b.Consensus != nil {
		// When `consensus_aware` is set to `true`, the backend group acts as a load balancer
		// serving traffic from any backend that agrees in the consensus group
```

## Snippet 3

Context: `proxyd/backend.go:91` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
HTTPErrorCode: 503,
	}

	ErrBackendUnexpectedJSONRPC = errors.New("backend returned an unexpected JSON-RPC response")
```
After
```go
HTTPErrorCode: 503,
	}
	ErrBlockOutOfRange = &RPCErr{
		Code:          JSONRPCErrorInternal - 19,
		Message:       "block is out of range",
		HTTPErrorCode: 400,
	}
```

## Snippet 4

Context: `proxyd/rewriter.go:1` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
(no before snippet captured)
```
After
```go
package proxyd

import (
	"encoding/json"
	"errors"
	"strings"

	"github.com/ethereum/go-ethereum/common/hexutil"
```

# Fix Pattern

Add a pre-dispatch validation and normalization gate that derives authoritative consensus state, rewrites or rejects incompatible requests, and short-circuits invalid inputs before backend execution.

## How It Was Fixed

The fix inserts consensus-based request rewriting into `proxyd/backend.go`, introduces `RewriteContext` in `proxyd/rewriter.go` to carry the latest consensus block, and adds `ErrBlockOutOfRange` so requests outside the allowed range are rejected locally instead of being forwarded unchanged.

# Why It Matters

1. It makes consensus-aware routing enforce request semantics, not just backend selection.

2. It reduces the chance that mutable tags like `latest` are resolved beyond the proxy's tracked consensus point.

3. It gives clients a consistent local error for out-of-range requests.

4. The provided evidence shows consistency hardening, not a demonstrated attacker-driven security impact.

# Evidence Notes

Grounded evidence is limited to the added rewrite path in `proxyd/backend.go`, the new `ErrBlockOutOfRange` error in the same file, and the new `RewriteContext` type in `proxyd/rewriter.go`. The supplied material does not show the full `RewriteTags` implementation, the exact RPC methods covered, any attacker model, backend compromise, privilege bypass, or concrete security impact. The stronger claim that this is a confirmed vulnerability fix is therefore unsupported by the provided evidence. Protocol security invariant: In a consensus-aware proxyd backend group, RPC requests that reference chain state by block tag or block number should be rewritten or rejected against the group's tracked consensus block, rather than forwarded unchanged to a backend. Verification notes: The patch does not prove that an attacker could force backend disagreement or control a backend. The diff does not show funds loss, privilege escalation, or authentication bypass. The exact set of RPC methods and block tag forms rewritten is not fully shown in the provided context. The patch supports consensus-safe response shaping, but it does not prove a previously exploitable remote vulnerability on its own. The visible diff shows a behavior change in consensus-aware request handling. The provided evidence does not prove exploitability or security impact. The exact rewrite coverage is not established from the supplied snippets alone. This is better classified as unclear security relevance rather than a confirmed security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-consensus-validation`
Final confidence: `medium`
Final tags: `blockchain-core, rpc-client-api, consensus, request-validation, block-tag-rewrite`

The patch does not prove a concrete exploitable vulnerability, but it clearly hardens a security-sensitive blockchain RPC path by enforcing consensus bounds before requests are forwarded. Before this change, consensus-aware mode selected agreeing backends yet still forwarded original block-tagged requests unchanged; after the change, proxyd derives the consensus height, rewrites tags, and rejects out-of-range requests locally. That supports retaining this as security hardening rather than a confirmed security fix.

## Security Evidence

1. Consensus-aware forwarding now derives an authoritative consensus block number before backend dispatch.
2. Requests are passed through RewriteTags and may be rewritten, short-circuited, or rejected instead of always being forwarded unchanged.
3. A dedicated ErrBlockOutOfRange response is introduced for requests outside the allowed consensus range.
4. The commit subject explicitly states block tags are rewritten to enforce consensus.

## Missing Evidence

1. The patch does not show a concrete exploit path, attacker model, or abuse scenario.
2. The full RewriteTags implementation and exact RPC methods affected are not provided.
3. No evidence shows privilege escalation, authentication bypass, or direct unauthorized data access.
4. Referenced tests are not included here, so the exact invariant coverage is not visible.

## Claim Boundaries

1. Supported: this patch strengthens consensus enforcement in a security-sensitive RPC path.
2. Supported: prior behavior forwarded original requests in consensus-aware mode without this rewrite/reject gate.
3. Not supported: the pre-patch behavior was a demonstrably exploitable vulnerability.
4. Not supported: impacts beyond consensus/state-view integrity, such as account compromise or privilege bypass.
