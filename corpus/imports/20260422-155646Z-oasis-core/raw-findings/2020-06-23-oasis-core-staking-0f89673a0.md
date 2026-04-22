---
case_id: case_20200623_0f89673a0
project: oasis-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
source_quality: high
date: 2020-06-23
source_refs:
  - git:0f89673a0f097b5b011abda8f7e57c1c95274a52
  - "go/consensus/tendermint/apps/registry/transactions.go:331"
  - "go/consensus/tendermint/apps/registry/transactions.go:378"
  - "go/consensus/tendermint/apps/registry/transactions_test.go:51"
  - "go/consensus/tendermint/apps/registry/transactions_test.go:129"
bug_class: missing-update-validation
impact_type:
  - unauthorized-state-modification
  - integrity-violation
confidence: medium
tags:
  - registry
  - node-registration
  - validation-gap
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a validation gap in the Tendermint registry application's `registerNode` flow. Before the change, an already-known node that was treated as expired could go through the recreate path and reach `state.SetNode(...)` without first passing `registry.VerifyNodeUpdate(...)`. After the change, update verification is required whenever `existingNode != nil`.

## Observed Patch Facts

1. In `go/consensus/tendermint/apps/registry/transactions.go`, the patch replaces `if isNewNode || isExpiredNode {` with `// If the node already exists make sure to verify the node update.`.

2. In `go/consensus/tendermint/apps/registry/transactions.go`, the patch removes `} else {`.

3. In `go/consensus/tendermint/apps/registry/transactions_test.go`, the patch replaces `tcs := []struct {` with `// Store all successful registrations in a map for easier reference in later test cases.`.

4. In `go/consensus/tendermint/apps/registry/transactions_test.go`, the patch replaces `n.AddRoles(node.RoleComputeWorker)` with `tcd.node.AddRoles(node.RoleComputeWorker)`.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/apps/registry`, `go/consensus/tendermint/apps`, which anchors the finding in the `staking` area of the project. Historical context from `go/consensus/tendermint/apps/registry/genesis.go`, `go/consensus/tendermint/apps/registry/registry.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/tendermint/apps/registry/genesis.go`, `go/consensus/tendermint/apps/staking/state/gas.go`. The strongest project-level identifiers around this patch are `newNode`, `existingNode`, `Logger`, and `signature`.

## Before/After Behavior

Before the patch, `registry.VerifyNodeUpdate(...)` was only reached in the `else` branch for already-existing, non-expired nodes, while the `if isNewNode || isExpiredNode` branch could write via `state.SetNode(...)` directly. After the patch, the code adds an `if existingNode != nil` guard that runs `registry.VerifyNodeUpdate(...)` before the final write path, so expired existing nodes no longer skip that check.

# Root Cause

The update-verification check was attached to the wrong control-flow condition. The code keyed verification on the non-new, non-expired branch instead of on the existence of a prior stored node record.

## Walkthrough

1. Pre-patch, the `isNewNode || isExpiredNode` branch called `state.SetNode(ctx, existingNode, newNode, sigNode)` directly.

2. Pre-patch, `registry.VerifyNodeUpdate(ctx.Logger(), existingNode, newNode)` appeared only in the separate `else` branch.

3. That structure meant an `existingNode` treated as expired would not pass through the update-verification block.

4. The patch adds a new guard: `if existingNode != nil { ... VerifyNodeUpdate(...) ... }`.

5. The old `else`-scoped verification block is removed/restructured, showing verification now depends on prior existence instead of expiration state.

6. Test changes preserve successful registrations for later cases, supporting the intent to exercise update behavior on previously registered nodes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/apps/registry/transactions.go | 331 | `registerNode` state-transition path; adds mandatory verification for any existing node before accepting the new descriptor |
| go/consensus/tendermint/apps/registry/transactions.go | 378 | old existing-node-only verification branch removed/restructured, indicating verification is no longer skipped for expired existing records |
| go/consensus/tendermint/apps/registry/transactions_test.go | 22 | registration/update test matrix expanded to preserve successful registrations and exercise update behavior across later cases |
| go/consensus/tendermint/apps/registry/transactions_test.go | 120 | tests around runtime/role-bearing nodes adjusted to cover the corrected update-verification behavior |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/apps/registry/transactions.go:331` (changes signature or replay validation logic)

Before
```go
}

	if isNewNode || isExpiredNode {
		// Node doesn't exist (or is expired). Create node.
		if err = state.SetNode(ctx, existingNode, newNode, sigNode); err != nil {
			ctx.Logger().Error("RegisterNode: failed to create node",
				"err", err,
				"node", newNode,
```
After
```go
}

	// If the node already exists make sure to verify the node update.
	if existingNode != nil {
		if err = registry.VerifyNodeUpdate(ctx.Logger(), existingNode, newNode); err != nil {
			ctx.Logger().Error("RegisterNode: failed to verify node update",
				"err", err,
				"new_node", newNode,
```

## Snippet 2

Context: `go/consensus/tendermint/apps/registry/transactions.go:378` (changes signature or replay validation logic)

Before
```go
return fmt.Errorf("failed to set node status: %w", err)
		}
	} else {
		// The node already exists, validate and update the node's entry.
		if err = registry.VerifyNodeUpdate(ctx.Logger(), existingNode, newNode); err != nil {
			ctx.Logger().Error("RegisterNode: failed to verify node update",
				"err", err,
				"new_node", newNode,
```
After
```go
return fmt.Errorf("failed to set node status: %w", err)
		}
	}
```

## Snippet 3

Context: `go/consensus/tendermint/apps/registry/transactions_test.go:51` (changes signature or replay validation logic)

Before
```go
require.NoError(err, "registry.SetConsensusParameters")

	tcs := []struct {
		name        string
		prepareFn   func(n *node.Node) []signature.Signer
		stakeParams *staking.ConsensusParameters
		valid       bool
	}{
```
After
```go
require.NoError(err, "registry.SetConsensusParameters")

	// Store all successful registrations in a map for easier reference in later test cases.
	type testCaseData struct {
		// Signers.
		entitySigner    signature.Signer
		nodeSigner      signature.Signer
		consensusSigner signature.Signer
```

## Snippet 4

Context: `go/consensus/tendermint/apps/registry/transactions_test.go:129` (changes signature or replay validation logic)

Before
```go
_ = state.SetRuntime(ctx, &rt, sigRt, false)

				n.AddRoles(node.RoleComputeWorker)
				n.Runtimes = []*node.Runtime{
					&node.Runtime{ID: rt.ID},
				}
				return nil
			},
```
After
```go
_ = state.SetRuntime(ctx, &rt, sigRt, false)

				tcd.node.AddRoles(node.RoleComputeWorker)
				tcd.node.Runtimes = []*node.Runtime{
					&node.Runtime{ID: rt.ID},
				}
			},
			nil,
```

# Fix Pattern

Require validation based on presence of existing state, not on a narrower branch condition, before allowing a state overwrite.

## How It Was Fixed

`registerNode` now calls `registry.VerifyNodeUpdate(...)` whenever a prior node record exists, including when that record is expired, before accepting the new descriptor and writing it to state. The tests were adjusted to keep prior registrations around for later update-oriented cases.

# Why It Matters

1. Prevents expired node records from bypassing update-policy checks.

2. Protects registry integrity for re-registration and renewal paths.

3. Keeps expiration from acting as a reset of prior-node validation rules.

# Evidence Notes

The strongest evidence is the movement of `registry.VerifyNodeUpdate(...)` in `go/consensus/tendermint/apps/registry/transactions.go`: it was previously confined to the `else` branch and is now gated by `existingNode != nil`. That directly supports a skipped-validation bug for expired existing nodes. The evidence does not establish the exact fields checked by `VerifyNodeUpdate`, nor does it prove signature forgery, replay, or a concrete consensus-level exploit. Protocol security invariant: A registration must not overwrite a previously stored node record without passing the registry's node-update verification, even if the stored record is expired. Verification notes: The patch does not prove a working exploit against consensus or validator selection. It does not show which specific node fields `VerifyNodeUpdate` protects, only that the check was previously skipped in one path. It does not prove signature forgery or replay by itself; the demonstrated flaw is missing update-policy enforcement on existing expired nodes. It does not show asset loss or full network compromise, only a registry integrity gap in node re-registration/update handling. The provided test diff shows new scaffolding to retain successful registrations for later update cases. The test changes support regression coverage for existing-node update behavior. No evidence here proves exploitability beyond the demonstrated missing verification path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-update-validation`
Final impact type: `unauthorized-state-modification, integrity-violation`
Final confidence: `medium`
Final tags: `registry, node-registration, validation-gap, consensus`

The patch clearly closes a validation gap in a security-sensitive registry path: an existing node record that was considered expired could previously be rewritten through the create path without first passing `VerifyNodeUpdate`. Requiring update verification whenever `existingNode != nil` materially strengthens authorization/integrity checks around node registration. However, the patch alone does not prove a concrete exploitable replay, signature-forgery, or consensus-compromise bug, so the original classification is too strong and is better retained as security hardening.

## Security Evidence

1. The commit subject explicitly says `Fix node update verification`, indicating the problem was missing verification logic.
2. Before the patch, the `isNewNode || isExpiredNode` branch called `state.SetNode(...)` directly, so an expired existing node could bypass `VerifyNodeUpdate(...)`.
3. After the patch, `VerifyNodeUpdate(...)` runs whenever `existingNode != nil`, which broadens validation from a narrower branch condition to all updates of existing records.
4. The changed code is in node registration / registry state handling inside the consensus application, which is a security-sensitive trust boundary.
5. Test changes preserve prior successful registrations for later cases, consistent with exercising update behavior on already-registered nodes.

## Missing Evidence

1. The patch does not show what `VerifyNodeUpdate(...)` enforces, so the exact security property is not proven from the provided diff.
2. There is no proof here of an attacker-controlled exploit path, successful bypass in practice, or concrete impact on funds or consensus safety.
3. The evidence does not establish replay, signature forgery, or impersonation specifically; it only shows skipped update verification on one path.

## Claim Boundaries

1. Supported claim: the patch fixes a missing validation check for updates to previously existing node records, including expired ones.
2. Supported claim: this improves registry integrity and authorization hygiene in a consensus-adjacent component.
3. Not supported: a specific replay attack, signature-validation flaw, or concrete consensus takeover.
4. Not supported: direct asset loss, remote code execution, or demonstrated real-world exploitability.
