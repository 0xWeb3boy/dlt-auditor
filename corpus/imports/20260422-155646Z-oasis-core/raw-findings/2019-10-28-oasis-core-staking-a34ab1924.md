---
case_id: case_20191028_a34ab1924
project: oasis-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
source_quality: medium
date: 2019-10-28
source_refs:
  - git:a34ab1924bb8570acd145d1bac041a241b3f8798
  - "go/tendermint/apps/registry/registry.go:121"
  - "go/tendermint/apps/registry/registry.go:248"
  - "go/tendermint/apps/registry/query.go:59"
  - "go/tendermint/apps/registry/registry.go:366"
bug_class: slashability-bypass
impact_type:
  - slashing-bypass
  - accountability-loss
confidence: medium
tags:
  - staking
  - slashing
  - registry
  - validator-lifecycle
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch changes registry object lifetime rules so expired nodes are retained long enough to remain slash-resolvable during debonding, while still being hidden from normal queries. It also blocks entity deregistration when registered nodes still exist. The supplied evidence supports an accountability/slashing bug in registry lifecycle handling, but does not prove a specific exploit chain beyond that.

## Observed Patch Facts

1. In `go/tendermint/apps/registry/registry.go`, the patch replaces `var expiredNodes []*node.Node` with `debondingInterval, err := stakeState.DebondingInterval()`.

2. In `go/tendermint/apps/registry/registry.go`, the patch replaces `removedEntity, removedNodes := state.RemoveEntity(id)` with `// Prevent entity deregistration if there are any registered nodes.`.

3. In `go/tendermint/apps/registry/query.go`, the patch replaces `return rq.state.Node(id)` with `epoch, err := rq.app.timeSource.GetEpoch(ctx, rq.height)`.

4. In `go/tendermint/apps/registry/registry.go`, the patch replaces `if err = state.SetNodeStatus(newNode.ID, &registry.NodeStatus{}); err != nil {` with `var status *registry.NodeStatus`.

## Project Context

The changed code sits primarily in `go/tendermint/apps/registry`, `go/tendermint/apps`, which anchors the finding in the `staking` area of the project. Historical context from `go/tendermint/apps/registry/genesis.go`, `go/tendermint/apps/staking/state/state.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/tendermint/apps/registry/genesis.go`, `go/tendermint/apps/staking/slashing.go`. The strongest project-level identifiers around this patch are `state`, `failed`, `nodes`, and `status`.

## Before/After Behavior

Before the patch, expired nodes were handled based on expiration relative to the current registry epoch, and entity deregistration proceeded without the shown pre-check for remaining nodes. After the patch, the registry consults the staking debonding interval, keeps expired nodes during that interval so they can still be resolved for slashing, hides expired nodes from query results, prevents entity deregistration when nodes remain, and preserves existing node status when an expired node is re-registered.

# Root Cause

Registry cleanup and deregistration rules were too aggressive: node records could be removed on expiration before the staking debonding window ended, and entity removal did not enforce the continued existence of dependent node records.

## Walkthrough

1. The epoch-transition path now reads the staking debonding interval instead of only acting on raw node expiration.

2. A new comment in that path explicitly states expired nodes must be kept so they can still be resolved and slashed during debonding.

3. The entity deregistration path now checks `HasEntityNodes(id)` and rejects removal when nodes still exist.

4. The query path was updated to avoid returning expired nodes, separating internal retention from external visibility.

5. The node re-registration path now reloads existing status for an expired retained node instead of always starting from a fresh empty status.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/tendermint/apps/registry/registry.go | 111 | epoch transition logic now retains expired nodes through the debonding interval so they remain slash-resolvable |
| go/tendermint/apps/registry/registry.go | 229 | entity deregistration path now rejects removal when the entity still has registered nodes |
| go/tendermint/apps/registry/query.go | 56 | read path hides expired nodes from callers while internal state may still keep them for accountability |
| go/tendermint/apps/registry/registry.go | 360 | node re-registration path preserves and resets existing status for previously expired nodes kept in state |

## Code Snippets

## Snippet 1

Context: `go/tendermint/apps/registry/registry.go:121` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	var expiredNodes []*node.Node
	for _, node := range nodes {
		if epochtime.EpochTime(node.Expiration) >= registryEpoch {
			continue
		}
		expiredNodes = append(expiredNodes, node)
```
After
```go
}

	debondingInterval, err := stakeState.DebondingInterval()
	if err != nil {
		app.logger.Error("onRegistryEpochChanged: failed to get debonding interval",
			"err", err,
		)
		return errors.Wrap(err, "registry: onRegistryEpochChanged: failed to get debonding interval")
```

## Snippet 2

Context: `go/tendermint/apps/registry/registry.go:248` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	removedEntity, removedNodes := state.RemoveEntity(id)

	if !ctx.IsCheckOnly() {
```
After
```go
}

	// Prevent entity deregistration if there are any registered nodes.
	hasNodes, err := state.HasEntityNodes(id)
	if err != nil {
		app.logger.Error("DeregisterEntity: failed to check for nodes",
			"err", err,
		)
```

## Snippet 3

Context: `go/tendermint/apps/registry/query.go:59` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
func (rq *registryQuerier) Node(ctx context.Context, id signature.PublicKey) (*node.Node, error) {
	return rq.state.Node(id)
}

func (rq *registryQuerier) Nodes(ctx context.Context) ([]*node.Node, error) {
	return rq.state.Nodes()
}
```
After
```go
func (rq *registryQuerier) Node(ctx context.Context, id signature.PublicKey) (*node.Node, error) {
	epoch, err := rq.app.timeSource.GetEpoch(ctx, rq.height)
	if err != nil {
		return nil, fmt.Errorf("failed to get epoch: %w", err)
	}

	node, err := rq.state.Node(id)
```

## Snippet 4

Context: `go/tendermint/apps/registry/registry.go:366` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

			if err = state.SetNodeStatus(newNode.ID, &registry.NodeStatus{}); err != nil {
				app.logger.Error("RegisterNode: failed to set node status",
					"err", err,
```
After
```go
}

			var status *registry.NodeStatus
			if existingNode != nil {
				// Node exists but is expired, fetch existing status.
				if status, err = state.NodeStatus(newNode.ID); err != nil {
					app.logger.Error("RegisterNode: failed to get node status",
						"err", err,
```

# Fix Pattern

Retain internally accountable records until the punishment window ends, but filter them from ordinary live-state queries and block parent-object deletion while dependent records remain.

## How It Was Fixed

The registry now keeps expired nodes for the staking debonding interval, prevents entity deregistration when the entity still has registered nodes, hides expired retained nodes from query results, and reuses existing node status when such a node is registered again.

# Why It Matters

1. Slashable nodes remain resolvable for the full debonding window.

2. Entity removal can no longer sever node-to-entity accountability while nodes still exist.

3. External callers still do not see expired nodes as live registry entries.

4. The evidence supports accountability and slashing preservation, not direct theft or cryptographic failure.

# Evidence Notes

The strongest support is the commit message and the added code comment stating that expired nodes must be kept so they can still get slashed during the debonding interval; otherwise they could not be resolved if removed. The deregistration guard and query filtering are consistent with that model. The evidence does not establish a broader exploit than loss of slashability/accountability for prematurely removed records. Protocol security invariant: Nodes that remain punishable during the staking debonding interval must remain internally resolvable, and an entity must not be removable while its registered nodes still exist. Verification notes: The patch does not by itself prove a practical exploit was executed on chain. The diff does not show direct fund theft, key compromise, or a cryptographic break. It is not proven that every slashing path was bypassed; the evidence shows unresolved or prematurely removed nodes could interfere with slashing/accountability. The query-layer change appears to preserve external semantics and does not itself demonstrate an access-control issue. Security relevance is supported by explicit slashing-related rationale in the commit message and code comment. Confidence is kept at medium because the provided diff does not show the full slashing call chain failing end-to-end. The patch is not a mere refactor or cleanup; it changes state-lifecycle rules in consensus-critical registry code. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `slashability-bypass`
Final impact type: `slashing-bypass, accountability-loss`
Final confidence: `medium`
Final tags: `staking, slashing, registry, validator-lifecycle`

The supplied patch evidence is sufficient to keep this case in a security-focused corpus. The commit message and inline code comment explicitly state that expired nodes were being removed too early, which meant they could no longer be resolved for slashing during the debonding interval. In a staking/validator system, loss of slashability is a concrete security failure in accountability enforcement, not just reliability or cleanup work. The query filtering and deregistration guard appear to support the same fix by separating internal accountability state from externally visible live state.

## Security Evidence

1. Commit message explicitly says expired nodes must remain so they can still get slashed during debonding.
2. Added comment in epoch-change logic states removed nodes otherwise could not be resolved for slashing.
3. Patch changes registry state-retention rules in consensus/staking-sensitive code, not just API behavior.
4. Entity deregistration is blocked while nodes still exist, preserving accountability linkage.
5. Expired nodes are hidden from queries while retained internally, consistent with fixing internal enforcement rather than changing public semantics.
6. Re-registration path preserves existing node status for expired retained nodes, which supports continued tracking of punishable state.

## Missing Evidence

1. No full slashing call chain is shown end-to-end in the diff.
2. No proof of a demonstrated exploit or on-chain incident is provided.
3. The patch does not quantify whether all slashing modes were affected or only some resolution paths.

## Claim Boundaries

1. Supported claim: premature node removal could prevent slashing during the debonding interval.
2. Supported claim: the patch fixes an accountability/slashability gap in registry lifecycle handling.
3. Not supported: direct fund theft, key compromise, or cryptographic failure.
4. Not supported: a broad state-serialization bug or client-view divergence as the primary security issue.
