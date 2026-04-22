---
case_id: case_20230731_67711fa42
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: medium
date: 2023-07-31
source_refs:
  - git:67711fa426c4948cca108fb0b04687bf0c5951ab
  - "go/consensus/cometbft/apps/roothash/roothash.go:541"
  - "go/consensus/cometbft/apps/roothash/transactions.go:96"
  - "go/scheduler/api/api.go:181"
  - "go/scheduler/api/api.go:150"
bug_class: proposer-liveness-accounting-gap
impact_type:
  - availability
  - penalty-bypass
confidence: medium
tags:
  - consensus
  - roothash
  - liveness
  - validator-accountability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds proposer-liveness tracking in roothash by recording missed proposals on valid proposer-timeout events and by introducing a helper that maps the round-selected scheduler into committee-member index space. That is security-adjacent availability/accountability logic, but the provided evidence does not establish a concrete pre-existing vulnerability or exploit; it more clearly shows new or strengthened liveness instrumentation.

## Observed Patch Facts

1. In `go/consensus/cometbft/apps/roothash/roothash.go`, the patch replaces `// Initialize per-epoch liveness statistics.` with `// Remember the index of the transaction scheduler within the committee.`.

2. In `go/consensus/cometbft/apps/roothash/transactions.go`, the patch replaces `// Timeout triggered by executor node, emit empty error block.` with `// Record that the scheduler did not propose.`.

3. In `go/scheduler/api/api.go`, the patch replaces `workers := c.Workers()` with `idx, err := c.TransactionSchedulerIdx(round)`.

4. In `go/scheduler/api/api.go`, the patch replaces `// Workers returns committee nodes with Worker role.` with `// TransactionSchedulerIdx returns the index of the transaction scheduler`.

## Project Context

The changed code sits primarily in `go/consensus/cometbft/apps/roothash`, `go/consensus/cometbft/apps`, `go/scheduler/api`, which anchors the finding in the `staking` area of the project. Historical context from `go/consensus/cometbft/apps/roothash/transactions_test.go`, `go/consensus/cometbft/apps/roothash/slashing.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/cometbft/apps/roothash/transactions_test.go`, `go/consensus/cometbft/apps/roothash/slashing.go`. The strongest project-level identifiers around this patch are `round`, `Committee`, `workers`, and `rtState`. Nearby tests or test-like files include `go/scheduler/tests/tester.go`.

## Before/After Behavior

Before the change, the shown proposer-timeout path did not update proposer-specific liveness statistics, and scheduler selection was exposed through `TransactionScheduler(round)` over the worker subset. After the change, `executorProposerTimeout` resolves `TransactionSchedulerIdx(rpt.Round)`, initializes liveness stats if needed, and increments `MissedProposals[schedulerIdx]`; scheduler lookup also gains `TransactionSchedulerIdx(round)` so code can refer to the selected worker by its index in `Committee.Members`.

# Root Cause

The evidence shows a liveness-accounting gap in the displayed code paths: proposer timeout handling did not record a missed proposal there, and there was no helper for resolving the selected scheduler directly into committee-member index space. However, the evidence does not prove that this caused an exploitable bypass, mis-slashing, or consensus failure before the patch.

## Walkthrough

1. `executorProposerTimeout` still validates timing and request correctness before the new logic runs.

2. After validation, the patch computes `schedulerIdx` with `rtState.ExecutorPool.Committee.TransactionSchedulerIdx(rpt.Round)`.

3. That timeout path now ensures `rtState.LivenessStatistics` exists and increments `MissedProposals[schedulerIdx]`.

4. `go/scheduler/api/api.go` adds `TransactionSchedulerIdx(round)`, which counts only worker-role members but returns the selected worker's index in `Committee.Members`.

5. `TransactionScheduler(round)` is rewritten to call the new helper and return `c.Members[idx]`.

6. `tryFinalizeExecutorCommits` also starts capturing the scheduler index early, which is consistent with broader liveness bookkeeping.

7. Related liveness-processing context shows these statistics are later consumed for runtime liveness evaluation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/cometbft/apps/roothash/transactions.go | 45 | records a missed proposal when a valid executor proposer timeout occurs |
| go/consensus/cometbft/apps/roothash/roothash.go | 534 | captures the round's scheduler identity in the executor commit-finalization path for liveness bookkeeping |
| go/scheduler/api/api.go | 154 | maps the round-selected scheduler to the committee-member index used by liveness statistics |
| go/consensus/cometbft/apps/roothash/liveness.go | 18 | consumes accumulated liveness statistics for runtime liveness evaluation and enforcement |

## Code Snippets

## Snippet 1

Context: `go/consensus/cometbft/apps/roothash/roothash.go:541` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
pool := rtState.ExecutorPool

	// Initialize per-epoch liveness statistics.
	if rtState.LivenessStatistics == nil {
```
After
```go
pool := rtState.ExecutorPool

	// Remember the index of the transaction scheduler within the committee.
	schedulerIdx, err := pool.Committee.TransactionSchedulerIdx(pool.Round)
	if err != nil {
		return err
	}
```

## Snippet 2

Context: `go/consensus/cometbft/apps/roothash/transactions.go:96` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	// Timeout triggered by executor node, emit empty error block.
	ctx.Logger().Debug("proposer round timeout",
```
After
```go
}

	// Record that the scheduler did not propose.
	schedulerIdx, err := rtState.ExecutorPool.Committee.TransactionSchedulerIdx(rpt.Round)
	if err != nil {
		return err
	}
	if rtState.LivenessStatistics == nil {
```

## Snippet 3

Context: `go/scheduler/api/api.go:181` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// based on the provided round.
func (c *Committee) TransactionScheduler(round uint64) (*CommitteeNode, error) {
	workers := c.Workers()
	numNodes := uint64(len(workers))
	if numNodes == 0 {
		return nil, fmt.Errorf("no workers in committee")
	}
	schedulerIdx := round % numNodes
```
After
```go
// based on the provided round.
func (c *Committee) TransactionScheduler(round uint64) (*CommitteeNode, error) {
	idx, err := c.TransactionSchedulerIdx(round)
	if err != nil {
		return nil, err
	}
	return c.Members[idx], nil
}
```

## Snippet 4

Context: `go/scheduler/api/api.go:150` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

// Workers returns committee nodes with Worker role.
func (c *Committee) Workers() []*CommitteeNode {
	var workers []*CommitteeNode
	for _, member := range c.Members {
		if member.Role != RoleWorker {
			continue
```
After
```go
}

// TransactionSchedulerIdx returns the index of the transaction scheduler
// within the committee for the provided round.
func (c *Committee) TransactionSchedulerIdx(round uint64) (int, error) {
	var (
		total  uint64
		worker uint64
```

# Fix Pattern

Add explicit failure-path accounting and a shared identity-mapping helper so liveness state is updated in the same index space used by downstream enforcement.

## How It Was Fixed

The patch records missed proposals when a valid proposer-timeout transaction is processed, and it adds `TransactionSchedulerIdx` so scheduler identity can be expressed as a committee-member index instead of only as a position within the filtered worker slice. This makes the new proposer-timeout accounting usable by later liveness evaluation code.

# Why It Matters

1. Proposer timeout events are now reflected in per-member liveness state.

2. Scheduler selection and liveness statistics now use a consistent member-index reference.

3. The evidence supports improved liveness accounting, not a proven prior vulnerability.

# Evidence Notes

Grounded evidence is limited to: new missed-proposal incrementing in `go/consensus/cometbft/apps/roothash/transactions.go`; early scheduler-index capture in `go/consensus/cometbft/apps/roothash/roothash.go`; and the new `TransactionSchedulerIdx` helper plus `TransactionScheduler` rewrite in `go/scheduler/api/api.go`. Related `liveness.go` context shows those statistics are later evaluated. The commit message describes new monitoring that runtimes can use for penalties, which reads more like adding or strengthening enforcement support than fixing a demonstrated vulnerability. Protocol security invariant: If proposer liveness is evaluated, proposer timeout events must be attributed to the intended committee member so later liveness processing uses consistent per-member statistics. Verification notes: The patch does not prove a consensus-safety failure such as state divergence or finality break. The patch does not show a memory-safety, cryptographic, or authentication flaw. The evidence does not prove external exploitability without control of a runtime committee role. The patch shows proposer failures were previously untracked or not attributable in this path, but it does not quantify real-world impact before deployment. No provided diff shows a concrete pre-patch exploit, consensus break, or mis-slashing incident. No evidence here quantifies real-world impact or shows that prior indexing was wrong at a call site that already updated proposer liveness. Treat this as security-adjacent hardening/feature work unless stronger proof of an actual vulnerability exists elsewhere. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `proposer-liveness-accounting-gap`
Final impact type: `availability, penalty-bypass`
Final confidence: `medium`
Final tags: `consensus, roothash, liveness, validator-accountability`

The patch is not well supported as a concrete security bug fix, but it does clearly strengthen a security-sensitive consensus path by recording missed proposer actions and aligning scheduler identity with the committee-member index space used for liveness statistics and later penalties. That supports treating the change as security hardening around validator accountability and availability enforcement, not as a proven exploitable vulnerability or a state-serialization issue.

## Security Evidence

1. `executorProposerTimeout` now records a missed proposal for the selected scheduler instead of only emitting the timeout path.
2. The new `TransactionSchedulerIdx(round)` maps the selected worker back into `Committee.Members` index space, which matches how liveness statistics are tracked.
3. `TransactionScheduler(round)` is rewritten to use the shared index helper, reducing mismatched attribution between scheduler selection and liveness accounting.
4. Commit metadata explicitly says proposer liveness is now monitored so runtimes can penalize proposers with insufficient commitments.
5. Related context shows liveness statistics are later consumed for runtime liveness evaluation and enforcement.

## Missing Evidence

1. No provided diff proves a pre-patch exploitable vulnerability, consensus break, or real slashing bypass incident.
2. No evidence quantifies attacker impact or shows that an adversary could reliably abuse the missing accounting for denial of service.
3. The patch does not show a direct authentication, authorization, cryptographic, or memory-safety flaw being fixed.
4. The excerpts do not prove whether prior behavior caused incorrect penalties in production or only lacked enforcement coverage.

## Claim Boundaries

1. Supported claim: the patch hardens proposer-liveness tracking and downstream penalty/accountability enforcement.
2. Supported claim: before the patch, proposer-timeout handling shown here did not attribute a missed proposal into liveness statistics.
3. Not supported: a confirmed exploitable security vulnerability with demonstrated attack steps or incident impact.
4. Not supported: serialization/state-representation or client-view-divergence as the primary bug class for this commit.
