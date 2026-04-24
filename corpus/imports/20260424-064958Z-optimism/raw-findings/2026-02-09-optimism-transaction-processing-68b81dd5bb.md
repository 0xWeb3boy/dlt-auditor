---
case_id: case_20260209_68b81dd5bb
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-02-09
source_refs:
  - git:68b81dd5bbbe2bdb7bdc09d263c2c0cac6cd3da2
  - "op-supernode/supernode/chain_container/engine_controller/rewind.go:103"
  - "op-supernode/supernode/chain_container/engine_controller/rewind_test.go:109"
  - "op-supernode/supernode/chain_container/engine_controller/rewind_test.go:196"
  - "op-supernode/supernode/chain_container/engine_controller/rewind.go:21"
bug_class: finalization-boundary-check
impact_type:
  - finalization-invariant-protection
confidence: medium
tags:
  - blockchain-core
  - consensus-sensitive
  - rewind-validation
  - finalization-boundary
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a missing guard in the supernode rewind path so a requested rewind target below the current finalized head is rejected with a dedicated error. That is a real behavior change, but the provided evidence does not establish that the old behavior was an exploitable security vulnerability rather than a correctness or hardening issue.

## Observed Patch Facts

1. In `op-supernode/supernode/chain_container/engine_controller/rewind.go`, the patch adds `if targetBlock.Number < currentFinalized.Number {`.

2. In `op-supernode/supernode/chain_container/engine_controller/rewind_test.go`, the patch adds `name: "target before finalized",`.

3. In `op-supernode/supernode/chain_container/engine_controller/rewind_test.go`, the patch adds `if tc.targetBeforeFinalized {`.

4. In `op-supernode/supernode/chain_container/engine_controller/rewind.go`, the patch adds `ErrRewindOverFinalizedHead = errors.New("cannot rewind over finalized head")`.

## Project Context

The changed code sits primarily in `op-supernode/supernode/chain_container/engine_controller`, `op-supernode/supernode/chain_container`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-supernode/supernode/chain_container/engine_controller/engine_controller_test.go`, `op-supernode/supernode/chain_container/engine_controller/engine_controller.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-supernode/supernode/chain_container/chain_container.go`, `op-supernode/supernode/chain_container/engine_controller/engine_controller_test.go`. The strongest project-level identifiers around this patch are `targetBlock`, `Number`, `L2BlockRef`, and `ErrRewindOverFinalizedHead`.

## Before/After Behavior

Before the patch, `computeRewindTargets` fetched the current safe and finalized refs and immediately returned `earliest(currentSafe, targetBlock)` and `earliest(currentFinalized, targetBlock)` without an explicit check for `targetBlock.Number < currentFinalized.Number`. After the patch, the function returns `ErrRewindOverFinalizedHead` and zero refs for that case, and the tests now cover a target that is older than the finalized head.

# Root Cause

`computeRewindTargets` had access to the current finalized head but did not explicitly reject rewind requests whose target block number was below that finalized boundary before deriving rewind targets.

## Walkthrough

1. `computeRewindTargets` reads the current safe and current finalized `eth.L2BlockRef` values.

2. In the pre-patch code shown, it then returned `earliest(currentSafe, targetBlock)` and `earliest(currentFinalized, targetBlock)` with no explicit finalized-boundary check.

3. The patch adds `ErrRewindOverFinalizedHead` and a guard that rejects `targetBlock.Number < currentFinalized.Number`.

4. The updated test suite adds a `target before finalized` case.

5. That test makes the finalized head newer than the requested target by setting `l2.refsByLabel[eth.Finalized]` to `targetBlockNum + 1` and expects `ErrRewindOverFinalizedHead`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-supernode/supernode/chain_container/engine_controller/rewind.go | 94 | core rewind target validation against current finalized head |
| op-supernode/supernode/chain_container/engine_controller/rewind.go | 15 | named error for finalized-boundary violation |
| op-supernode/supernode/chain_container/engine_controller/rewind_test.go | 103 | regression test covering rewind target before finalized head |
| op-supernode/supernode/chain_container/engine_controller/rewind_test.go | 190 | test setup that makes finalized head newer than the requested rewind target |

## Code Snippets

## Snippet 1

Context: `op-supernode/supernode/chain_container/engine_controller/rewind.go:103` (changes a sensitive control or state-update path)

Before
```go
}

	return earliest(currentSafe, targetBlock), earliest(currentFinalized, targetBlock), nil
}
```
After
```go
}

	if targetBlock.Number < currentFinalized.Number {
		return eth.L2BlockRef{}, eth.L2BlockRef{}, ErrRewindOverFinalizedHead
	}

	return earliest(currentSafe, targetBlock), earliest(currentFinalized, targetBlock), nil
}
```

## Snippet 2

Context: `op-supernode/supernode/chain_container/engine_controller/rewind_test.go:109` (changes a consensus- or validator-sensitive branch)

Before
```go
expectedError:       ErrRewindTimestampToBlockConversion,
		},
	}
```
After
```go
expectedError:       ErrRewindTimestampToBlockConversion,
		},
		{
			name:                  "target before finalized",
			targetBeforeFinalized: true,
			expectedError:         ErrRewindOverFinalizedHead,
		},
	}
```

## Snippet 3

Context: `op-supernode/supernode/chain_container/engine_controller/rewind_test.go:196` (changes signature or replay validation logic)

Before
```go
rollupConfig.Genesis = rollup.Genesis{L2Time: 2000}
			}

			// Make a "good" engine controller, using a potentially sabotaged mock L2
```
After
```go
rollupConfig.Genesis = rollup.Genesis{L2Time: 2000}
			}
			if tc.targetBeforeFinalized {
				l2.refsByLabel[eth.Finalized] = eth.L2BlockRef{Number: targetBlockNum + 1, Hash: common.Hash{0xff}}
			}

			// Make a "good" engine controller, using a potentially sabotaged mock L2
```

## Snippet 4

Context: `op-supernode/supernode/chain_container/engine_controller/rewind.go:21` (changes a consensus- or validator-sensitive branch)

Before
```go
ErrRewindTimestampToBlockConversion = errors.New("failed to convert timestamp to block number")
	ErrRewindPayloadNotFound            = errors.New("failed to get payload for block")
)
```
After
```go
ErrRewindTimestampToBlockConversion = errors.New("failed to convert timestamp to block number")
	ErrRewindPayloadNotFound            = errors.New("failed to get payload for block")
	ErrRewindOverFinalizedHead          = errors.New("cannot rewind over finalized head")
)
```

# Fix Pattern

Add an explicit invariant check at the start of a state-transition helper, return a dedicated error on violation, and add a regression test for the forbidden ordering.

## How It Was Fixed

The fix introduces `ErrRewindOverFinalizedHead` in `rewind.go` and returns it from `computeRewindTargets` when the requested target block is older than the current finalized head. The tests were extended to construct that condition and assert the error is returned.

# Why It Matters

1. It makes the finalized-boundary rule explicit in the rewind helper.

2. It prevents this helper from producing rewind targets below the current finalized head.

3. It turns the bad case into a named error path instead of implicit downstream behavior.

# Evidence Notes

Direct evidence is limited to the added guard and error in `op-supernode/supernode/chain_container/engine_controller/rewind.go` and the matching regression test additions in `rewind_test.go`. The commit subject references finalized-head rewinds, and the commit body mentions panic-versus-error handling, but the provided material does not show caller reachability, real exploitability, consensus impact, or whether the old behavior was only an internal correctness bug. Protocol security invariant: The rewind helper should not return targets older than the current finalized L2 head. The provided evidence establishes this as a local rewind-path invariant, but does not prove a broader security property or exploit path. Verification notes: The patch does not show that an external attacker can invoke this rewind path. The patch does not prove on-chain finalized history could actually be rewritten; it shows local controller validation was missing. The patch does not establish whether the old behavior caused consensus divergence, local panic/DoS, or only incorrect operator-facing behavior. The broader impact through `chain_container` orchestration is not demonstrated in the provided diff. Confirmed the patch adds `if targetBlock.Number < currentFinalized.Number` and returns `ErrRewindOverFinalizedHead`. Confirmed the tests add a `target before finalized` scenario and expect that error. Did not find evidence in the provided material that the old behavior was externally reachable or caused a demonstrated security failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `finalization-boundary-check`
Final impact type: `finalization-invariant-protection`
Final confidence: `medium`
Final tags: `blockchain-core, consensus-sensitive, rewind-validation, finalization-boundary`

The patch adds an explicit guard that rejects rewinds below the current finalized head and backs it with a regression test. In a blockchain execution/control path, preventing state movement across a finalized boundary is a security-sensitive invariant, so this is stronger than ordinary reliability work. That said, the provided evidence does not prove an externally reachable exploit, consensus break, or concrete attacker impact, so the safest classification is security hardening rather than a confirmed security bug fix.

## Security Evidence

1. The implementation now returns ErrRewindOverFinalizedHead when targetBlock.Number is below currentFinalized.Number.
2. Before the patch, computeRewindTargets would derive rewind targets without an explicit finalized-boundary check.
3. A dedicated regression test adds a "target before finalized" case and expects the new error.
4. The changed code is in rewind/control logic for L2 block references, which is consensus-sensitive state-management code.

## Missing Evidence

1. No proof that an attacker or untrusted input could trigger this rewind path.
2. No evidence that the old behavior caused consensus divergence, finalized-state rollback, or chain safety failure in practice.
3. No direct demonstration of panic, denial of service, or privilege boundary crossing from the pre-patch behavior.
4. No caller-level evidence showing how far the bad rewind targets could propagate before being stopped elsewhere.

## Claim Boundaries

1. The patch supports the claim that a finalized-boundary invariant was previously unenforced in this helper.
2. The patch supports retaining this as a security-hardening case, not as a proven exploitable security fix.
3. The evidence does not justify claiming confirmed consensus compromise, attacker exploitability, or externally reachable rollback of finalized history.
