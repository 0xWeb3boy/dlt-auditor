---
case_id: case_20220905_fa52dea46
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2022-09-05
source_refs:
  - git:fa52dea46bd3a178d0e4c7d86f4a83b32e188afe
  - "go/consensus/tendermint/full/full.go:247"
  - "go/runtime/registry/host.go:335"
  - "go/consensus/api/submission.go:246"
  - "go/consensus/api/grpc.go:769"
bug_class: freshness-verification
impact_type:
  - stale-attestation-acceptance
confidence: medium
tags:
  - tee
  - attestation
  - freshness
  - consensus-proof
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The shown patch adds a new runtime-host `ProveFreshness` transaction flow and extends consensus submission APIs to return a `transaction.Proof`. That is consistent with security hardening around freshness, but the supplied evidence does not show the verifier-side logic, a pre-patch acceptance flaw, or a demonstrated vulnerability.

## Observed Patch Facts

1. In `go/consensus/tendermint/full/full.go`, the patch replaces `// Subscribe to the transaction being included in a block.` with `if _, err := t.submitTx(ctx, tx); err != nil {`.

2. In `go/runtime/registry/host.go`, the patch replaces `// Implements protocol.Handler.` with `func (h *runtimeHostHandler) handleHostProveFreshness(`.

3. In `go/consensus/api/submission.go`, the patch replaces `// NoOpSubmissionManager implements a submission manager that doesn't support submitt...` with `// SignAndSubmitTxWithProof is a helper function that signs and submits`.

4. In `go/consensus/api/grpc.go`, the patch replaces `func (c *consensusClient) StateToGenesis(ctx context.Context, height int64) (*genesis...` with `func (c *consensusClient) SubmitTxWithProof(ctx context.Context, tx *transaction.Sign...`.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/full`, `go/consensus/tendermint`, `go/runtime/registry`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `go/consensus/api/api.go`, `go/consensus/tendermint/full/light.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/api/api.go`, `go/consensus/tendermint/full/common.go`. The strongest project-level identifiers around this patch are `transaction`, `error`, `proof`, and `protocol`. Nearby tests or test-like files include `go/consensus/tests/tester.go`, `go/runtime/client/tests/tester.go`.

## Before/After Behavior

Before the shown change, the visible consensus API path exposed `SubmitTx(ctx, tx) error` and the supplied excerpts did not include a dedicated `handleHostProveFreshness` path or a proof-returning submit API. After the change, `go/runtime/registry/host.go` constructs a `ProveFreshness` transaction and calls a new `SignAndSubmitTxWithProof`, while the consensus backend and gRPC client gain `SubmitTxWithProof` to return a `transaction.Proof`.

# Root Cause

Not established by the provided evidence. The observable change is that the runtime-host path previously lacked an end-to-end way to submit a freshness-related transaction and receive a consensus inclusion proof back through the API layers. The excerpts do not show whether stale TEE evidence was previously accepted, where verification happened, or whether this is a new feature versus a fix for an exploitable bug.

## Walkthrough

1. `go/runtime/registry/host.go` adds `handleHostProveFreshness`, which gets node identity, creates `registry.NewProveFreshnessTx(0, nil, rq.Blob)`, and calls `consensus.SignAndSubmitTxWithProof`.

2. `go/consensus/api/submission.go` adds `SignAndSubmitTxWithProof`, a helper that signs, submits, and returns an inclusion proof.

3. `go/consensus/tendermint/full/full.go` refactors `SubmitTx` through shared `submitTx` and adds `SubmitTxWithProof` that returns `*transaction.Proof`.

4. `go/consensus/api/grpc.go` adds a client-side `SubmitTxWithProof`, allowing the proof to cross the RPC boundary.

5. These excerpts show proof plumbing for a freshness-related transaction, but not the code that verifies or enforces freshness.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/runtime/registry/host.go | 335 | adds host-side `handleHostProveFreshness`, building a registry freshness transaction and obtaining proof |
| go/consensus/api/submission.go | 244 | adds helper to sign, submit, and return inclusion proof for freshness transactions |
| go/consensus/tendermint/full/full.go | 243 | consensus backend now exposes transaction submission with proof, enabling freshness anchoring |
| go/consensus/api/grpc.go | 767 | client API gains `SubmitTxWithProof`, carrying the consensus proof across the RPC boundary |
| go/runtime/host/protocol/types.go | 1 | host protocol surface changes to carry freshness request/response types for the runtime-host boundary |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/full/full.go:247` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// Implements consensusAPI.Backend.
func (t *fullService) SubmitTx(ctx context.Context, tx *transaction.SignedTransaction) error {
	// Subscribe to the transaction being included in a block.
	data := cbor.Marshal(tx)
```
After
```go
// Implements consensusAPI.Backend.
func (t *fullService) SubmitTx(ctx context.Context, tx *transaction.SignedTransaction) error {
	if _, err := t.submitTx(ctx, tx); err != nil {
		return err
	}
	return nil
}
```

## Snippet 2

Context: `go/runtime/registry/host.go:335` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

// Implements protocol.Handler.
func (h *runtimeHostHandler) Handle(ctx context.Context, rq *protocol.Body) (*protocol.Body, error) {
```
After
```go
}

func (h *runtimeHostHandler) handleHostProveFreshness(
	ctx context.Context,
	rq *protocol.HostProveFreshnessRequest,
) (*protocol.HostProveFreshnessResponse, error) {
	identity, err := h.env.GetNodeIdentity(ctx)
	if err != nil {
```

## Snippet 3

Context: `go/consensus/api/submission.go:246` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

// NoOpSubmissionManager implements a submission manager that doesn't support submitting transactions.
type NoOpSubmissionManager struct{}
```
After
```go
}

// SignAndSubmitTxWithProof is a helper function that signs and submits
// a transaction to the consensus backend and creates a proof of inclusion.
//
// If the nonce is set to zero, it will be automatically filled in based on the
// current consensus state.
//
```

## Snippet 4

Context: `go/consensus/api/grpc.go:769` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (c *consensusClient) StateToGenesis(ctx context.Context, height int64) (*genesis.Document, error) {
	var rsp genesis.Document
```
After
```go
}

func (c *consensusClient) SubmitTxWithProof(ctx context.Context, tx *transaction.SignedTransaction) (*transaction.Proof, error) {
	var proof transaction.Proof
	if err := c.conn.Invoke(ctx, methodSubmitTxWithProof.FullName(), tx, &proof); err != nil {
		return nil, err
	}
	return &proof, nil
```

# Fix Pattern

Add proof-returning submission APIs and a dedicated freshness transaction path so callers can obtain consensus inclusion evidence for freshness-related operations.

## How It Was Fixed

The patch introduces a `ProveFreshness` host handler that submits a dedicated registry transaction and receives a proof of inclusion. Supporting APIs were added so the proof can be produced by the backend and returned over gRPC instead of collapsing the operation to success-or-error only. The supplied excerpts do not show the consuming verifier logic.

# Why It Matters

1. It provides explicit consensus inclusion proof instead of only a submission result.

2. It gives freshness-related operations a dedicated path rather than relying on generic transaction submission alone.

3. It may support replay-resistance or freshness checks, but that enforcement is not shown in the provided evidence.

# Evidence Notes

Direct evidence is limited to four Go excerpts showing new proof-returning submission helpers and a new `handleHostProveFreshness` path. The commit subject and changed-file list suggest broader TEE freshness work, including verifier-side changes, but those code paths are not included here, so stronger security claims are unsupported. Protocol security invariant: If client or TEE freshness is enforced, the decision should rely on recent consensus-anchored evidence rather than a bare transaction-submission success result. The provided excerpts only show plumbing toward that invariant, not the full enforcement point. Verification notes: The provided excerpts do not show the exact verifier-side acceptance logic, only the new proof-generation path. The patch does not by itself prove that stale attestations were exploitable in all deployments. No evidence here shows consensus compromise, key theft, or arbitrary code execution. The diff supports a freshness/replay-prevention interpretation, but not the precise attacker prerequisites or impact scope. The verifier-side diff is needed to confirm that stale or replayed evidence is actually rejected. The protocol type changes are not shown, so the exact request/response contents for freshness are not directly verified here. A regression test demonstrating rejection of stale freshness evidence would be needed to classify this as a confirmed vulnerability fix or hardening with confidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `freshness-verification`
Final impact type: `stale-attestation-acceptance`
Final confidence: `medium`
Final tags: `tee, attestation, freshness, consensus-proof, hardening`

The supplied material supports a security-hardening interpretation, not a confirmed vulnerability fix. The commit metadata is explicitly about adding client-node TEE freshness verification, and the shown code adds a dedicated freshness transaction path plus consensus inclusion proofs so freshness evidence can be anchored and returned across the API boundary. That is security-sensitive behavior, but the excerpts do not show the verifier-side rejection logic, a concrete pre-patch acceptance flaw, or a demonstrated exploit path. This is strong enough to retain as hardening, but not to promote to a confirmed security fix.

## Security Evidence

1. Commit subject explicitly says client node TEE freshness verification.
2. A new `handleHostProveFreshness` path creates a `ProveFreshness` transaction from a host request.
3. The patch adds `SignAndSubmitTxWithProof` and `SubmitTxWithProof`, returning a consensus inclusion proof instead of only success or error.
4. Changed files include runtime verifier and consensus verifier code, consistent with security-sensitive freshness enforcement work.
5. Tests/runtime files were touched alongside implementation, suggesting intended end-to-end validation.

## Missing Evidence

1. No verifier-side snippet shows stale or replayed TEE evidence being rejected.
2. No patch excerpt demonstrates how the returned proof is consumed and validated.
3. No regression test excerpt shows a previously accepted stale freshness artifact now failing.
4. No commit message or advisory text describes a concrete exploitable pre-patch weakness.

## Claim Boundaries

1. Supported claim: the patch strengthens TEE freshness handling by adding proof-backed freshness plumbing.
2. Supported claim: this is security-relevant hardening in a sensitive attestation/consensus area.
3. Unsupported claim: a specific exploitable vulnerability is proven from the supplied excerpts alone.
4. Unsupported claim: the patch by itself proves consensus compromise, key theft, or arbitrary code execution risk.
