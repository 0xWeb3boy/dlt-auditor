---
case_id: case_20260325_7e59d7195
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: high
date: 2026-03-25
source_refs:
  - git:7e59d719538e199b0d398746e0efbd180dab6737
  - "consensus/bor/bor.go:1761"
  - "params/config_test.go:1330"
  - "consensus/bor/bor_test.go:5271"
  - "consensus/bor/heimdall/client.go:272"
bug_class: consensus-input-nondeterminism
impact_type:
  - consensus-divergence
  - state-consistency
confidence: medium
tags:
  - consensus
  - validator
  - state-sync
  - determinism
  - heimdall
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a consensus-relevant determinism fix in Bor's state-sync import path. The patch adds a deterministic-state-sync gate and a Heimdall height lookup by cutoff time to avoid different validators deriving different state-sync sets from different Heimdall views. The evidence does not prove exploitation or a historical chain split.

## Observed Patch Facts

1. In `consensus/bor/bor.go`, the patch replaces `eventRecords, err = c.HeimdallClient.StateSyncEvents(c.ctx, from, to.Unix())` with `queryCtx := c.ctx`.

2. In `params/config_test.go`, the patch adds `func TestIsDeterministicStateSync(t *testing.T) {`.

3. In `consensus/bor/bor_test.go`, the patch adds `// trackingHeimdallClient records which IHeimdallClient methods were called.`.

4. In `consensus/bor/heimdall/client.go`, the patch replaces `func FetchOnce[T any](ctx context.Context, client http.Client, url *url.URL, closeCh...` with `// BlockHeightByTimeResponse is the response from the Heimdall clerk/block-height-by-...`.

## Project Context

The changed code sits primarily in `consensus/bor`, `consensus/bor/heimdall`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `consensus/bor/heimdall.go`, `consensus/bor/heimdall/state_sync_url_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/bor/heimdall/state_sync_url_test.go`, `consensus/bor/heimdallgrpc/state_sync.go`. The strongest project-level identifiers around this patch are `Unix`, `height`, `from`, and `Error`.

## Before/After Behavior

Before the patch, `CommitStates` waited for Heimdall sync and then directly called `StateSyncEvents(c.ctx, from, to.Unix())`, so record selection depended on the local Heimdall view at query time. After the patch, `CommitStates` introduces `queryCtx := c.ctx` and, when `IsDeterministicStateSync(header.Number)` is active, first calls `GetBlockHeightByTime(queryCtx, to.Unix())`; the added client API and test counters indicate the intent is to anchor selection to a Heimdall height derived from the cutoff time.

# Root Cause

The consensus path selected imported state-sync data using a time-based Heimdall query without first pinning the read to a canonical Heimdall snapshot boundary. Different validators querying different Heimdall views could therefore derive different state-sync sets for the same Bor block.

## Walkthrough

1. `CommitStates` computes the state-sync range by reading `LastStateId`, setting `from`, and computing cutoff time `to`.

2. Before the change, after waiting for Heimdall sync, it directly called `StateSyncEvents(c.ctx, from, to.Unix())`.

3. The patch adds `queryCtx := c.ctx` and gates new behavior behind `IsDeterministicStateSync(header.Number)`.

4. Inside that branch, Bor calls `HeimdallClient.GetBlockHeightByTime(queryCtx, to.Unix())`.

5. `heimdall/client.go` documents that new API as returning the Heimdall block height at or before the cutoff timestamp.

6. The added inline comment in `bor.go` states the security-relevant concern directly: different validators could derive different state-sync sets from different Heimdall views.

7. Tests add a deterministic-state-sync config check and tracking for the new Heimdall client calls.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/bor/bor.go | 1701 | Consensus state-sync import path that computes which Heimdall events are applied for a Bor block. |
| consensus/bor/bor.go | 1761 | New deterministic branch that resolves a Heimdall height from cutoff time before fetching state-sync data. |
| consensus/bor/heimdall/client.go | 272 | Heimdall client API addition for mapping cutoff time to canonical Heimdall height used by consensus. |

## Code Snippets

## Snippet 1

Context: `consensus/bor/bor.go:1761` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
c.spanStore.waitUntilHeimdallIsSynced(c.ctx)

	eventRecords, err = c.HeimdallClient.StateSyncEvents(c.ctx, from, to.Unix())
	if err != nil {
		log.Error("Error occurred when fetching state sync events", "fromID", from, "to", to.Unix(), "err", err)

		stateSyncs := make([]*types.StateSyncData, 0)
		return stateSyncs, nil
```
After
```go
c.spanStore.waitUntilHeimdallIsSynced(c.ctx)

	queryCtx := c.ctx

	if c.config.IsDeterministicStateSync(header.Number) {
		heimdallHeight, err := c.HeimdallClient.GetBlockHeightByTime(queryCtx, to.Unix())
		if err != nil {
			log.Error("Failed to get Heimdall height for deterministic state sync", "to", to.Unix(), "err", err)
```

## Snippet 2

Context: `params/config_test.go:1330` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
})
}
```
After
```go
})
}

func TestIsDeterministicStateSync(t *testing.T) {
	t.Parallel()

	config := &BorConfig{
		DeterministicStateSyncBlock: big.NewInt(100),
```

## Snippet 3

Context: `consensus/bor/bor_test.go:5271` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}
}
```
After
```go
}
}

// trackingHeimdallClient records which IHeimdallClient methods were called.
// It returns configurable results and tracks call counts for assertions.
type trackingHeimdallClient struct {
	// Call counters
	stateSyncEventsCalled       int
```

## Snippet 4

Context: `consensus/bor/heimdall/client.go:272` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func FetchOnce[T any](ctx context.Context, client http.Client, url *url.URL, closeCh chan struct{}) (*T, error) {
	request := &Request{client: client, url: url, start: time.Now()}
```
After
```go
}

// BlockHeightByTimeResponse is the response from the Heimdall clerk/block-height-by-time endpoint.
type BlockHeightByTimeResponse struct {
	Height int64 `json:"height"`
}

// GetBlockHeightByTime returns the Heimdall block height at or before the given cutoff unix timestamp.
```

# Fix Pattern

For consensus-critical cross-system inputs, resolve queries to a canonical snapshot identifier before fetching records, instead of relying on open-ended time-based reads against each node's live view.

## How It Was Fixed

The patch introduces a feature-gated deterministic path in `CommitStates` and adds `GetBlockHeightByTime` to the Heimdall client. That change moves the state-sync selection logic toward a height-pinned Heimdall read based on the cutoff timestamp, with tests covering the activation gate and the new client-call path.

# Why It Matters

1. Consensus inputs must be identical across validators.

2. A node-local Heimdall view can otherwise change which state-sync events are imported.

3. The evidence supports a determinism fix, not a cryptographic break or proven exploit.

# Evidence Notes

The changed path is the consensus-side `CommitStates` flow, not a generic client cleanup. The added `GetBlockHeightByTime` call and related tests indicate the intent is to anchor Heimdall reads to a stable height so different validators do not observe different event sets when their Heimdall backends are at different sync states. The in-code comment explicitly frames validator divergence as the problem being solved. That supports a security classification, but the patch alone does not prove a practical exploit, adversary control of Heimdall responses, or an observed chain split. Protocol security invariant: For a given Bor block, validators should derive the same Heimdall state-sync record set. Selection should not depend on each node's current Heimdall view at query time. Verification notes: The patch does not prove an externally exploitable remote attack path. It does not prove that a chain split happened in production. It does not show that Heimdall responses were unauthenticated or maliciously forgeable. It does not establish a cryptographic break; the issue is deterministic input selection for consensus. It does not prove impact before the feature gate activates on the configured block. Only excerpts are provided; the final fetch step after the height lookup is inferred from the added client/test surface and not shown in full. The supplied material does not show an observed chain split, attacker control, or exploitation. Confidence is medium because the evidence clearly shows the determinism concern and mitigation intent, but not the full end-to-end patched query flow. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-input-nondeterminism`
Final impact type: `consensus-divergence, state-consistency`
Final confidence: `medium`
Final tags: `consensus, validator, state-sync, determinism, heimdall`

The supplied patch evidence supports a security-relevant hardening change in a consensus-critical path: it adds a deterministic, height-pinned Heimdall lookup for state-sync selection and includes an inline comment explicitly warning that different validators could otherwise derive different state-sync sets from different Heimdall views. That is a protocol integrity concern, but the excerpted patch does not prove a concrete exploitable vulnerability, adversary control, or an observed fork. The original phase-3 labeling as a direct security fix is stronger than the patch alone supports.

## Security Evidence

1. The change is in `CommitStates`, a consensus/state-sync path used by validators.
2. The patch adds `IsDeterministicStateSync(...)` gating and a `GetBlockHeightByTime(...)` lookup before selecting sync data.
3. The new client API is documented as returning the Heimdall height at or before a cutoff timestamp, indicating an attempt to pin reads to a stable snapshot.
4. An inline code comment states that different validators could derive different state-sync sets from different Heimdall views.
5. Tests were added for the deterministic-state-sync config and for the new Heimdall client call path.

## Missing Evidence

1. The excerpt does not show the full post-lookup fetch logic end to end.
2. There is no proof of a real-world exploit, attacker primitive, or observed chain split.
3. The patch does not show that malicious or unauthenticated Heimdall responses were possible.
4. The evidence does not quantify whether divergence was reachable before the feature gate activated.

## Claim Boundaries

1. Supported: the patch hardens consensus input determinism for state-sync selection.
2. Supported: the risk being addressed is validator/view divergence from live Heimdall reads.
3. Not supported: a confirmed exploitable security bug with demonstrated attacker impact.
4. Not supported: cryptographic failure, authentication bypass, or remote code execution.
5. Not supported: proof that production consensus failure actually occurred.
