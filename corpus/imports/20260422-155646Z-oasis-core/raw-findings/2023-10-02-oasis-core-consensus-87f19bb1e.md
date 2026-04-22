---
case_id: case_20231002_87f19bb1e
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2023-10-02
source_refs:
  - git:87f19bb1e4296beed05aa0699a724d2babd447ba
  - "go/consensus/cometbft/apps/roothash/liveness.go:95"
  - "go/consensus/cometbft/apps/roothash/liveness.go:43"
  - "go/consensus/cometbft/apps/roothash/liveness_test.go:132"
  - "go/consensus/cometbft/apps/roothash/finalization.go:184"
bug_class: improper-role-scoped-enforcement
impact_type:
  - integrity
  - availability
confidence: medium
tags:
  - consensus
  - validator
  - slashing
  - suspension
  - role-scoping
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is well-supported as a roothash liveness-accounting correction: it narrows enforcement and penalty application to worker members only. The provided evidence does not establish a concrete vulnerability beyond incorrect role-scoped fault accounting, so this should remain classified as unclear rather than a confirmed security fix.

## Observed Patch Facts

1. In `go/consensus/cometbft/apps/roothash/liveness.go`, the patch replaces `err = onRuntimeLivenessFailure(ctx, nodeID, &slashParams.Amount)` with `err = onRuntimeLivenessFailure(ctx, n.PublicKey, &slashParams.Amount)`.

2. In `go/consensus/cometbft/apps/roothash/liveness.go`, the patch replaces `// Collect per node liveness statistics as a single node can have multiple roles.` with `// Penalize worker nodes that were not live enough.`.

3. In `go/consensus/cometbft/apps/roothash/liveness_test.go`, the patch replaces `// When node is live again, fault counter should decrease.` with `// When node is a backup worker, fault counter should not change.`.

4. In `go/consensus/cometbft/apps/roothash/finalization.go`, the patch replaces `// Make sure to not include nodes in multiple roles multiple times.` with `case !ok:`.

## Project Context

The changed code sits primarily in `go/consensus/cometbft/apps/roothash`, `go/consensus/cometbft/apps`, which anchors the finding in the `consensus` area of the project. Historical context from `go/consensus/cometbft/apps/roothash/transactions_test.go`, `go/consensus/cometbft/apps/roothash/transactions.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/cometbft/apps/supplementarysanity/checks.go`, `go/consensus/cometbft/apps/staking/slashing_test.go`. The strongest project-level identifiers around this patch are `PublicKey`, `rtState`, `status`, and `epoch`.

## Before/After Behavior

Before the patch, the liveness path explicitly aggregated statistics per node across possible multiple roles, and finalization had a special case that credited a backup worker with a live round when no commitment was submitted and there was no discrepancy. After the patch, `processLivenessStatistics` is framed as worker-only processing, stops once members are no longer workers, and applies status/slash updates to the current member's `n.PublicKey`. The updated test asserts that when the node is changed to `RoleBackupWorker`, running liveness processing does not change the existing fault counter.

# Root Cause

Liveness accounting and enforcement were scoped too broadly across committee roles for the same node. That mixed worker obligations with backup-worker handling instead of isolating worker liveness evaluation to worker-role entries.

## Walkthrough

1. `liveness.go` previously described collecting liveness statistics per node because one node could have multiple roles, which shows role-collapsed accounting in the old design.

2. `finalization.go` previously used a `seen` map and a special branch that counted some backup-worker non-commit cases as live rounds.

3. The patched `finalization.go` removes that special-case credit path and now skips missing or nil votes.

4. The patched `liveness.go` changes the evaluation phase to 'Penalize worker nodes that were not live enough' and iterates only through worker members, breaking once non-workers are reached.

5. The punishment path now uses `n.PublicKey` for `onRuntimeLivenessFailure` and `SetNodeStatus`, binding updates to the currently evaluated worker member entry.

6. The regression test changes the member role to `RoleBackupWorker`, reruns processing, and checks that suspension is not re-applied and the prior fault count stays unchanged.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/cometbft/apps/roothash/liveness.go | 18 | worker-only liveness evaluation and punishment path |
| go/consensus/cometbft/apps/roothash/liveness.go | 89 | apply suspension/slash state to the evaluated committee member public key |
| go/consensus/cometbft/apps/roothash/finalization.go | 178 | round finalization updates live-round statistics used by liveness enforcement |
| go/consensus/cometbft/apps/roothash/liveness_test.go | 126 | regression coverage that backup-worker service must not change worker fault accounting |

## Code Snippets

## Snippet 1

Context: `go/consensus/cometbft/apps/roothash/liveness.go:95` (changes a sensitive control or state-update path)

Before
```go
// Slash if configured.
				err = onRuntimeLivenessFailure(ctx, nodeID, &slashParams.Amount)
				if err != nil {
					return fmt.Errorf("failed to slash node %s: %w", nodeID, err)
				}
			}
		}
```
After
```go
// Slash if configured.
				err = onRuntimeLivenessFailure(ctx, n.PublicKey, &slashParams.Amount)
				if err != nil {
					return fmt.Errorf("failed to slash node %s: %w", n.PublicKey, err)
				}
			}
		}
```

## Snippet 2

Context: `go/consensus/cometbft/apps/roothash/liveness.go:43` (changes an authorization or privilege gate)

Before
```go
)

	// Collect per node liveness statistics as a single node can have multiple roles.
	type Stats struct {
		liveRounds         uint64
		finalizedProposals uint64
		missedProposals    uint64
	}
```
After
```go
)

	// Penalize worker nodes that were not live enough.
	regState := registryState.NewMutableState(ctx.State())
	for i, n := range rtState.Committee.Members {
		if n.Role != api.RoleWorker {
			// Workers are listed before backup workers.
			break
```

## Snippet 3

Context: `go/consensus/cometbft/apps/roothash/liveness_test.go:132` (changes an authorization or privilege gate)

Before
```go
epoch += 2

	// When node is live again, fault counter should decrease.
	rtState.LivenessStatistics.LiveRounds[0] = 91 // At least 90 required.
	err = processLivenessStatistics(ctx, epoch, rtState)
```
After
```go
epoch += 2

	// When node is a backup worker, fault counter should not change.
	rtState.Committee.Members[0].Role = scheduler.RoleBackupWorker
	rtState.LivenessStatistics.LiveRounds[0] = 91 // At least 90 required.
	err = processLivenessStatistics(ctx, epoch, rtState)
	require.NoError(err, "processLivenessStatistics")
	status, err = registryState.NodeStatus(ctx, sk.Public())
```

## Snippet 4

Context: `go/consensus/cometbft/apps/roothash/finalization.go:184` (changes an authorization or privilege gate)

Before
```go
for i, n := range rtState.Committee.Members {
		vote, ok := sc.Votes[n.PublicKey]
		// Make sure to not include nodes in multiple roles multiple times.
		_, wasSeen := seen[n.PublicKey]
		seen[n.PublicKey] = struct{}{}
		switch {
		case !ok && n.Role == scheduler.RoleBackupWorker && !pool.Discrepancy && !wasSeen:
			// This is a backup worker only that did not submit a commitment and there was no
```
After
```go
for i, n := range rtState.Committee.Members {
		vote, ok := sc.Votes[n.PublicKey]
		switch {
		case !ok:
			continue
		case vote == nil:
			// Skip failures.
			continue
```

# Fix Pattern

Restrict accounting and penalty logic to the role that actually carries the obligation, and remove cross-role aggregation or special-case credit that can leak non-obligated role behavior into enforcement.

## How It Was Fixed

The patch removed the old per-node multi-role aggregation approach in `liveness.go`, changed liveness enforcement to a worker-only loop, and updated slashing/status writes to use the current member public key. In `finalization.go`, it deleted the backup-worker live-round credit branch. In `liveness_test.go`, it added coverage that backup-worker status must not change worker fault accounting.

# Why It Matters

1. It aligns suspension and slashing decisions with worker-role obligations.

2. It prevents backup-worker handling from affecting worker fault accounting through the shown paths.

3. It reduces incorrect liveness-enforcement outcomes in consensus-related logic.

4. The new test documents the intended worker-only behavior.

# Evidence Notes

The strongest support is in `go/consensus/cometbft/apps/roothash/liveness.go`, where the code changes from per-node multi-role statistics to worker-only penalization and switches status/slash updates from `nodeID` to `n.PublicKey`. `go/consensus/cometbft/apps/roothash/finalization.go` removes the `seen`-based backup-worker live-round credit path. `go/consensus/cometbft/apps/roothash/liveness_test.go` directly asserts that converting the member to `RoleBackupWorker` leaves the fault counter unchanged. The evidence supports a correctness fix in role-scoped liveness accounting, but does not prove attacker-controlled exploitability, production impact, or a broader consensus break. Protocol security invariant: Worker liveness enforcement should be driven only by committee members that have worker-role liveness obligations. Non-worker roles, including backup workers, should not contribute worker liveness credit or have worker liveness penalties applied through mixed per-node accounting. Verification notes: The patch does not prove an external attacker can choose or manipulate committee roles at will. The patch does not show a confirmed consensus safety break; it shows incorrect liveness/fault accounting. The patch does not prove wrongful slashing happened in production; the test demonstrates intended accounting behavior only. The patch does not establish a network-triggerable denial of service or remote code execution condition. Regression evidence exists in `liveness_test.go` for the backup-worker case. The provided hunks support worker-only accounting and penalty scoping. No supplied evidence demonstrates an externally triggerable exploit or confirms real-world abuse. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-role-scoped-enforcement`
Final impact type: `integrity, availability`
Final confidence: `medium`
Final tags: `consensus, validator, slashing, suspension, role-scoping`

The patch clearly narrows a security-sensitive enforcement path: liveness penalties, suspension, and slashing are changed from mixed per-node/multi-role accounting to worker-only processing, and the regression test shows backup workers should no longer affect worker fault counts. That supports retaining this as security hardening in a consensus/validator context. However, the supplied evidence does not prove a concrete exploit, attacker control over committee-role composition, or an actual consensus break, so this should not be upgraded to a confirmed security fix.

## Security Evidence

1. `processLivenessStatistics` now explicitly penalizes worker nodes only and stops when committee members are no longer workers.
2. The penalty path updates suspension/slashing state using the currently evaluated member key (`n.PublicKey`), tightening which identity is punished.
3. `finalization.go` removes backup-worker-specific live-round credit logic and the prior multi-role deduplication path, reducing cross-role leakage into liveness accounting.
4. The updated test asserts that changing a node to `RoleBackupWorker` leaves the fault counter unchanged and does not reapply suspension.

## Missing Evidence

1. No evidence shows an external actor could deliberately trigger the bad role/accounting combination.
2. No evidence proves a concrete consensus safety failure, privilege bypass, or attacker-triggerable denial of service.
3. No evidence shows wrongful slashing or suspension occurred in production or led to financial loss.

## Claim Boundaries

1. Supported: the patch hardens role-scoped liveness accounting so backup workers do not influence worker penalties.
2. Supported: the affected behavior includes suspension/slashing logic, which is security-sensitive in validator consensus code.
3. Not supported: a concrete exploitable vulnerability with a demonstrated attack path.
4. Not supported: a confirmed consensus break or real-world abuse from this bug.
