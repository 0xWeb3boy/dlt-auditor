---
case_id: case_20230629_95923572b
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2023-06-29
source_refs:
  - git:95923572b51b9ab0d3bfac5565f52dd6af4b99ae
  - "go/worker/client/committee/node.go:151"
  - "go/runtime/registry/host.go:383"
  - "go/consensus/cometbft/full/full.go:207"
  - "go/consensus/api/grpc.go:778"
bug_class: state-verification-gap
impact_type:
  - verification-freshness
  - integrity-hardening
confidence: medium
tags:
  - blockchain-core
  - consensus
  - verifier
  - proofs
  - state-verification
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a same-block verification improvement in the runtime consensus verifier, not a clearly established vulnerability fix. The patch adds a path to fetch the block metadata transaction with proof-bearing transaction data so latest-block state verification no longer waits for a later block, but the provided snippets do not show prior acceptance of forged or attacker-controlled state.

## Observed Patch Facts

1. In `go/worker/client/committee/node.go`, the patch replaces `var resolvedRound uint64` with `rtInfo, err := hrt.GetInfo(ctx)`.

2. In `go/runtime/registry/host.go`, the patch replaces `func (h *runtimeHostHandler) handleHostProveFreshness(` with `func (h *runtimeHostHandler) handleHostFetchBlockMetadataTx(`.

3. In `go/consensus/cometbft/full/full.go`, the patch replaces `txs, err := t.GetTransactions(ctx, data.Height)` with `tps, err := t.GetTransactionsWithProofs(ctx, data.Height)`.

4. In `go/consensus/api/grpc.go`, the patch replaces `func (c *consensusClient) GetUnconfirmedTransactions(ctx context.Context) ([][]byte,...` with `func (c *consensusClient) GetTransactionsWithProofs(ctx context.Context, height int64...`.

## Project Context

The changed code sits primarily in `go/worker/client/committee`, `go/worker/client`, `go/runtime/registry`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `go/consensus/api/api.go`, `go/runtime/registry/registry.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/cometbft/full/common.go`, `go/runtime/registry/registry.go`. The strongest project-level identifiers around this patch are `data`, `error`, `block`, and `GetTransactionsWithProofs`. Nearby tests or test-like files include `go/consensus/tests/tester.go`, `go/runtime/client/tests/tester.go`.

## Before/After Behavior

Before the change, the visible query path used annotated-block/history-based resolution and the supplied snippets did not show a dedicated block-metadata fetch path backed by transaction proofs; the commit body says latest-block state verification had a block delay. After the change, the runtime host adds block-metadata transaction fetching, the consensus API exposes transaction retrieval with proofs, and the backend produces proof-bearing transaction data so same-block validation can be performed.

# Root Cause

The verifier stack lacked an explicit end-to-end way to obtain the block metadata transaction, together with the needed proof-bearing transaction data, for the exact height being checked. That left latest-block verification delayed rather than performed through a same-block metadata path.

## Walkthrough

1. `go/runtime/registry/host.go` adds `handleHostFetchBlockMetadataTx`, which fetches transactions with proofs for a requested height and searches for the block metadata transaction.

2. `go/consensus/api/grpc.go` adds `GetTransactionsWithProofs`, making proof-bearing transaction retrieval available through the consensus client API.

3. `go/consensus/cometbft/full/full.go` switches from plain transaction retrieval to proof-bearing retrieval and computes Merkle proofs over transaction hashes.

4. `go/worker/client/committee/node.go` removes the visible `resolvedRound`/`GetAnnotatedBlock` setup, while the commit message states the goal is same-block state verification with no block delay.

5. The provided evidence shows a verifier-freshness/path improvement, but not a demonstrated exploit or prior integrity break.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/worker/client/committee/node.go | 136 | committee client query path that chooses how latest runtime/consensus state is resolved and verified |
| go/runtime/registry/host.go | 383 | runtime host handler that fetches the block metadata transaction used to bind post-block state to a specific height |
| go/consensus/cometbft/full/full.go | 203 | consensus backend path returning transaction inclusion proofs needed for metadata-tx verification |
| go/consensus/api/grpc.go | 778 | consensus client API surface exposing transaction-plus-proof retrieval to verifier consumers |

## Code Snippets

## Snippet 1

Context: `go/worker/client/committee/node.go:151` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
maxMessages := dsc.Executor.MaxMessages

	var resolvedRound uint64
	queryFn := func(round uint64) ([]byte, error) {
		annBlk, err := n.commonNode.Runtime.History().GetAnnotatedBlock(ctx, round)
		if err != nil {
			return nil, fmt.Errorf("client: failed to fetch annotated block from history: %w", err)
		}
```
After
```go
maxMessages := dsc.Executor.MaxMessages

	rtInfo, err := hrt.GetInfo(ctx)
	if err != nil {
		return nil, fmt.Errorf("client: failed to fetch runtime info: %w", err)
	}

	// TODO: Remove once same block consensus validation is deployed.
```

## Snippet 2

Context: `go/runtime/registry/host.go:383` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (h *runtimeHostHandler) handleHostProveFreshness(
	ctx context.Context,
```
After
```go
}

func (h *runtimeHostHandler) handleHostFetchBlockMetadataTx(
	ctx context.Context,
	rq *protocol.HostFetchBlockMetadataTxRequest,
) (*protocol.HostFetchBlockMetadataTxResponse, error) {
	tps, err := h.consensus.GetTransactionsWithProofs(ctx, int64(rq.Height))
	if err != nil {
```

## Snippet 3

Context: `go/consensus/cometbft/full/full.go:207` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	txs, err := t.GetTransactions(ctx, data.Height)
	if err != nil {
		return nil, err
	}

	if data.Index >= uint32(len(txs)) {
```
After
```go
}

	tps, err := t.GetTransactionsWithProofs(ctx, data.Height)
	if err != nil {
		return nil, err
	}

	if data.Index >= uint32(len(tps.Transactions)) {
```

## Snippet 4

Context: `go/consensus/api/grpc.go:778` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (c *consensusClient) GetUnconfirmedTransactions(ctx context.Context) ([][]byte, error) {
	var rsp [][]byte
```
After
```go
}

func (c *consensusClient) GetTransactionsWithProofs(ctx context.Context, height int64) (*TransactionsWithProofs, error) {
	var rsp TransactionsWithProofs
	if err := c.conn.Invoke(ctx, methodGetTransactionsWithProofs.FullName(), height, &rsp); err != nil {
		return nil, err
	}
	return &rsp, nil
```

# Fix Pattern

Add a dedicated proof-bearing retrieval path for the consensus metadata object needed by verification, and use that path to validate the latest height directly instead of relying on delayed resolution.

## How It Was Fixed

The patch threads block-metadata retrieval through the runtime host and consensus client, adds transaction-with-proofs support in the backend, and updates proof generation logic so the verifier can use the block metadata transaction for same-block validation.

# Why It Matters

1. Removes a freshness delay in latest-block verification.

2. Makes the verifier depend on an explicit metadata-transaction retrieval path with proof-bearing data.

3. Improves verifier correctness, but the supplied evidence does not establish a concrete security exploit.

# Evidence Notes

The strongest grounded claims are that the patch introduces `handleHostFetchBlockMetadataTx`, adds `GetTransactionsWithProofs`, and updates backend proof handling, while the commit body says this removes a block delay for state verification. The provided snippets do not show prior acceptance of forged state, a remote attack path, consensus failure, signature bypass, or Merkle-proof forgery. Because the security thesis is not established by the provided evidence alone, the security classification should be downgraded to unclear. Protocol security invariant: Latest-block post-execution state should not be treated as fully verified until the verifier can check block metadata for that same height through the intended consensus proof path. Verification notes: The patch does not by itself prove that unverified latest-block state was previously accepted as authoritative. It does not show a concrete exploit path for a remote attacker or a non-consensus participant. It does not prove signature forgery, Merkle-proof forgery, or a consensus safety failure. The observable impact may be freshness/consistency hardening rather than a demonstrated confidentiality or integrity compromise. Commit body explicitly describes eliminating a block delay for state verification. Code snippets show new metadata-transaction and proof-bearing retrieval paths. No provided snippet demonstrates that the pre-patch behavior was exploitable. Many changed verifier files are listed but not excerpted, which limits stronger conclusions. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `state-verification-gap`
Final impact type: `verification-freshness, integrity-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, verifier, proofs, state-verification, security-hardening`

The patch evidence supports keeping this as a security-hardening case, not a concrete security-fix. The commit explicitly changes how latest-block runtime state is verified, adding a dedicated block-metadata transaction fetch path backed by transaction proofs and removing a one-block verification delay. In a consensus verifier, tightening when and how state becomes verified is security-relevant because it reduces exposure to accepting or relying on insufficiently validated state, but the supplied snippets do not prove a previously exploitable vulnerability, attacker-controlled forgery, or consensus break.

## Security Evidence

1. Commit body says post-execution state of the latest consensus block is now verified using the block metadata transaction.
2. New host handler `handleHostFetchBlockMetadataTx` adds an explicit path to retrieve block metadata for a given height.
3. Consensus API adds `GetTransactionsWithProofs`, showing proof-bearing retrieval was introduced for verification.
4. Backend switches from plain transaction retrieval to proof-bearing retrieval and computes Merkle proofs over transaction hashes.
5. The change removes a stated block delay for state verification in a consensus-sensitive verifier path.

## Missing Evidence

1. No snippet shows pre-patch acceptance of forged or attacker-controlled state as valid.
2. No evidence demonstrates an exploitable remote attack path or consensus safety failure.
3. No proof that signatures, Merkle proofs, or transaction inclusion checks were previously bypassable.
4. Most runtime verifier file changes are listed but not excerpted, limiting stronger conclusions about exact pre/post security properties.

## Claim Boundaries

1. Supported claim: the patch strengthens same-block state verification using metadata transactions and proofs.
2. Supported claim: this reduces a verification freshness gap in a security-sensitive consensus path.
3. Not supported: a concrete exploitable vulnerability was fixed.
4. Not supported: pre-patch behavior enabled signature forgery, proof forgery, or consensus compromise.
