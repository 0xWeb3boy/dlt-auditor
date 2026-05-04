---
case_id: case_20210909_60bab8f7d4
project: avalanchego
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
bug_class: consensus-safety
impact_type:
  - consensus-failure
confidence: medium
source_quality: medium
tags:
  - blockchain-core
  - consensus
  - consensus-safety
  - consensus-failure
  - validator
  - database
date: 2021-09-09
source_refs:
  - git:60bab8f7d4f5b987eab985cac81ea440ad507f1c
  - "vms/proposervm/pre_fork_block.go:73"
  - "vms/proposervm/vm_byzantine_test.go:295"
  - "vms/proposervm/vm_byzantine_test.go:198"
  - "vms/proposervm/vm_byzantine_test.go:180"
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant proposer VM fork-boundary validation flaw. The implementation adds state checks in `verifyPreForkChild` so a pre-fork child after activation is rejected when the parent is inconsistent with pre-fork status. The evidence supports a fork-validation security fix, but not the exact exploit path or concrete impact.

## Observed Patch Facts

1. In `vms/proposervm/pre_fork_block.go`, the patch replaces `b.vm.ctx.Log.Debug("allowing pre-fork block %s after the fork time because the parent...` with `if parentStatus := b.Status(); parentStatus == choices.Accepted {`.

2. In `vms/proposervm/vm_byzantine_test.go`, the patch replaces `if _, ok := opts[0].(*postForkOption); !ok {` with `if err := aBlock.Verify(); err != nil {`.

3. In `vms/proposervm/vm_byzantine_test.go`, the patch adds `if err := aBlock.Accept(); err != nil {`.

4. In `vms/proposervm/vm_byzantine_test.go`, the patch adds `if err := aBlock.Verify(); err != nil {`.

## Project Context

The changed code sits primarily in `vms/proposervm`, which anchors the finding in the `consensus` area of the project. Historical context from `vms/proposervm/pre_fork_block_test.go`, `vms/proposervm/post_fork_block_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vms/proposervm/vm_test.go`, `vms/proposervm/pre_fork_block_test.go`. The strongest project-level identifiers around this patch are `Fatal`, `block`, `Verify`, and `parent`.

## Before/After Behavior

Before the patch, the visible code path allowed a pre-fork block after fork activation when the parent passed the oracle-block check, with no shown checks against accepted post-fork state or post-fork tree membership. After the patch, `verifyPreForkChild` checks whether the parent is accepted and whether a post-fork block has already been accepted, and also checks whether a non-accepted parent inner block is present in the post-fork block tree. These cases now return `errUnexpectedBlockType`.

# Root Cause

The validation path for pre-fork children after activation relied on the oracle-parent exception without the added state checks needed to distinguish a genuine pre-fork oracle parent from a parent already associated with post-fork state.

## Walkthrough

1. A pre-fork child is verified after `activationTime` in `vms/proposervm/pre_fork_block.go`.

2. The parent must pass `verifyIsOracleBlock`.

3. The patch checks whether the parent status is `choices.Accepted`.

4. If accepted, the code calls `b.vm.GetLastAccepted()` and rejects unless it gets `database.ErrNotFound`.

5. If not accepted, the code checks `b.vm.Tree.Contains(b.Block)` and rejects when the parent inner block is already in the post-fork tree.

6. Regression tests exercise faulty or Byzantine parent-option cases around verifying and accepting post-fork blocks.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vms/proposervm/pre_fork_block.go | 73 | consensus validation guard for pre-fork child blocks after activation time |
| vms/proposervm/vm_byzantine_test.go | 180 | regression setup verifying post-fork oracle parent before option verification |
| vms/proposervm/vm_byzantine_test.go | 198 | regression test ensuring parsed option remains invalid after accepting post-fork block |
| vms/proposervm/vm_byzantine_test.go | 295 | regression test for post-fork option with faulty parent |

## Code Snippets

## Snippet 1

Context: `vms/proposervm/pre_fork_block.go:73` (changes persisted or aggregate state handling)

Before
```go
}

		b.vm.ctx.Log.Debug("allowing pre-fork block %s after the fork time because the parent is an oracle block",
			b.ID())
```
After
```go
}

		if parentStatus := b.Status(); parentStatus == choices.Accepted {
			_, err := b.vm.GetLastAccepted()
			if err != database.ErrNotFound {
				// If the parent block is accepted and it was a preForkBlock,
				// then there shouldn't have been an accepted postForkBlock yet.
				// If there was an accepted postForkBlock, then the parent
```

## Snippet 2

Context: `vms/proposervm/vm_byzantine_test.go:295` (changes signature or replay validation logic)

Before
```go
t.Fatal("could not retrieve options from post fork oracle block")
	}
	if _, ok := opts[0].(*postForkOption); !ok {
		t.Fatal("unexpected option type")
	}

	if err := opts[0].Verify(); err == nil {
		t.Fatal("option 0 has invalid parent, should not verify")
```
After
```go
t.Fatal("could not retrieve options from post fork oracle block")
	}

	if err := aBlock.Verify(); err != nil {
		t.Fatal(err)
	}
	if err := opts[0].Verify(); err == nil {
		t.Fatal("option 0 has invalid parent, should not verify")
```

## Snippet 3

Context: `vms/proposervm/vm_byzantine_test.go:198` (changes signature or replay validation logic)

Before
```go
t.Fatal("unexpectedly passed block verification")
	}
}
```
After
```go
t.Fatal("unexpectedly passed block verification")
	}

	if err := aBlock.Accept(); err != nil {
		t.Fatal(err)
	}

	if err := yBlock.Verify(); err == nil {
```

## Snippet 4

Context: `vms/proposervm/vm_byzantine_test.go:180` (changes signature or replay validation logic)

Before
```go
}

	if err := opts[0].Verify(); err != nil {
		t.Fatal(err)
```
After
```go
}

	if err := aBlock.Verify(); err != nil {
		t.Fatal(err)
	}
	if err := opts[0].Verify(); err != nil {
		t.Fatal(err)
```

# Fix Pattern

Enforce the fork-boundary block-type invariant at verification time using VM state rather than relying only on oracle-block shape.

## How It Was Fixed

`preForkBlock.verifyPreForkChild` was changed to reject pre-fork children whose parent is incompatible with pre-fork status based on accepted post-fork state or post-fork block-tree membership. Byzantine regression tests were updated to verify parent blocks before option validation and to confirm invalid parsed options remain invalid after accepting the related post-fork block.

# Why It Matters

1. Consensus validation must classify fork-boundary blocks consistently.

2. The patch targets invalid parent and block-type handling.

3. The evidence does not show cryptographic failure or direct asset theft.

4. The supplied tests support a Byzantine or faulty-parent regression scenario.

# Evidence Notes

The strongest evidence is the new guard in `vms/proposervm/pre_fork_block.go` and the commit subject `patched pre-fork-block exploit`. The test changes in `vms/proposervm/vm_byzantine_test.go` support the faulty-parent validation thesis. The evidence does not establish the full network exploit path, specific attacker actions, fund loss, or a cryptographic primitive issue. The mapper's high confidence is downgraded because the provided snippets do not fully demonstrate exploitability or consensus divergence. Protocol security invariant: After proposer VM fork activation, a pre-fork child block may only be valid when its parent is still consistent with being a pre-fork oracle block; accepted post-fork state or post-fork block-tree membership must prevent that parent from being used as a valid pre-fork parent. Verification notes: The patch does not prove the exact network exploit path. The patch does not show a cryptographic primitive failure. The patch does not establish asset theft or direct fund loss. The patch evidence is limited to proposer VM fork-boundary validation behavior. The patch does not prove every possible consensus divergence scenario, only this invalid parent/block-type case. No independent file inspection or command execution was used. Assessment is limited to the supplied snippets and metadata. Security corpus inclusion is justified by explicit exploit language plus consensus validation changes. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied evidence supports retaining this as a security-fix case. The commit subject explicitly describes a pre-fork-block exploit, and the implementation adds consensus validation checks that reject pre-fork children whose parent is inconsistent with accepted post-fork state or post-fork block-tree membership. The regression tests exercise Byzantine or faulty-parent verification paths. The evidence does not prove the full exploit mechanics or concrete network impact, but it is strong enough for a consensus validation security fix.

## Security Evidence

1. Commit subject says "patched pre-fork-block exploit".
2. `verifyPreForkChild` now rejects parents inconsistent with pre-fork status after activation.
3. The new checks consult accepted post-fork state via `GetLastAccepted()` and post-fork tree membership via `Tree.Contains`.
4. Tests cover Byzantine/faulty parent option verification and ensure invalid parsed options remain invalid after accepting a related post-fork block.

## Missing Evidence

1. No full attacker workflow or exploit reproduction is provided.
2. No explicit demonstration of consensus divergence, chain halt, or asset loss is shown.
3. No advisory, issue, or external vulnerability description is supplied.

## Claim Boundaries

1. Classify as a proposer VM fork-boundary consensus validation fix.
2. Do not claim cryptographic primitive failure.
3. Do not claim direct fund theft or asset loss.
4. Do not infer the exact exploit path beyond invalid pre-fork/post-fork parent handling.
