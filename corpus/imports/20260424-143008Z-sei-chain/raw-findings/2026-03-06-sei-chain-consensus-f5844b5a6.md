---
case_id: case_20260306_f5844b5a6
project: sei-chain
domain: infrastructure
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
source_quality: high
tags:
  - infrastructure
  - consensus
  - consensus-safety
  - consensus-failure
date: 2026-03-06
source_refs:
  - git:f5844b5a64e59b3483c14b0aebe53ed830e029fe
  - "sei-tendermint/internal/autobahn/types/types_test.go:121"
  - "sei-tendermint/internal/autobahn/consensus/inner.go:233"
  - "sei-tendermint/internal/autobahn/consensus/state_test.go:1"
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Likely security fix in the Autobahn consensus timeout path. The production change in `State.voteTimeout` stops constructing TimeoutVotes solely from the current `i.PrepareQC`; when that value is absent, it inherits `i.TimeoutQC.LatestPrepareQC()`. This is grounded as a consensus safety fix, but confidence is medium rather than high because the provided evidence does not include the full `pushTimeoutQC`, proposal verification, or commit-formation logic needed to independently prove the entire conflicting-commit scenario.

## Observed Patch Facts

1. In `sei-tendermint/internal/autobahn/types/types_test.go`, the patch adds `// TestNewTimeoutQC_MixedPrepareQCs verifies quorum-intersection behavior:`.

2. In `sei-tendermint/internal/autobahn/consensus/inner.go`, the patch replaces `v := types.NewFullTimeoutVote(s.cfg.Key, view, i.PrepareQC)` with `// If no PrepareQC was observed in this view, inherit the one from the`.

3. In `sei-tendermint/internal/autobahn/consensus/state_test.go`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `sei-tendermint/internal/autobahn/types`, `sei-tendermint/internal/autobahn`, `sei-tendermint/internal/autobahn/consensus`, which anchors the finding in the `consensus` area of the project. Historical context from `sei-tendermint/internal/autobahn/types/testonly.go`, `sei-tendermint/internal/autobahn/types/proposal_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/autobahn/types/testonly.go`, `sei-tendermint/internal/autobahn/types/proposal_test.go`. The strongest project-level identifiers around this patch are `view`, `PrepareQC`, `utils`, and `TestNewTimeoutQC_MixedPrepareQCs`.

## Before/After Behavior

Before the patch, `voteTimeout` called `types.NewFullTimeoutVote(s.cfg.Key, view, i.PrepareQC)`, so a TimeoutVote could omit a PrepareQC whenever the current state's `i.PrepareQC` was absent. The commit context states that this can happen after timeout-driven view changes. After the patch, `voteTimeout` uses the current PrepareQC when present, but falls back to `i.TimeoutQC.LatestPrepareQC()` when a TimeoutQC exists and the current PrepareQC is absent, then builds the TimeoutVote with that selected value.

# Root Cause

The timeout-vote construction path did not preserve an existing PrepareQC lock across consecutive timeout-driven views when the current-view `i.PrepareQC` was empty, even though the prior lock was available from the justifying TimeoutQC.

## Walkthrough

1. A validator can enter a new view using a TimeoutQC that carries a latest PrepareQC.

2. The supplied commit context says `pushTimeoutQC` clears `i.PrepareQC` on view change.

3. Before the fix, `voteTimeout` only used `i.PrepareQC` when constructing a TimeoutVote.

4. If no new current-view PrepareQC was observed, consecutive timeouts could emit TimeoutVotes without the inherited PrepareQC.

5. The new code preserves `i.PrepareQC` when present, otherwise reads `i.TimeoutQC.LatestPrepareQC()`.

6. The TimeoutVote is then created with the selected PrepareQC value.

7. Added tests cover inherited PrepareQC behavior, consecutive timeouts, persisted restart behavior, and TimeoutQC selection cases.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/autobahn/consensus/inner.go | 233 | production fix in State.voteTimeout; carries inherited PrepareQC into NewFullTimeoutVote when current-view PrepareQC is absent |
| sei-tendermint/internal/autobahn/consensus/state_test.go | 1 | new consensus-state regression coverage for voteTimeout, pushTimeoutQC, persistence, and consecutive timeout behavior |
| sei-tendermint/internal/autobahn/types/types_test.go | 121 | TimeoutQC selection tests validating mixed PrepareQC votes and highest PrepareQC selection |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/internal/autobahn/types/types_test.go:121` (changes signature or replay validation logic)

Before
```go
}
}
```
After
```go
}
}

// TestNewTimeoutQC_MixedPrepareQCs verifies quorum-intersection behavior:
// even if only one vote carries a PrepareQC, NewTimeoutQC picks it up
// and Verify accepts the result.
func TestNewTimeoutQC_MixedPrepareQCs(t *testing.T) {
	rng := utils.TestRng()
```

## Snippet 2

Context: `sei-tendermint/internal/autobahn/consensus/inner.go:233` (changes a sensitive control or state-update path)

Before
```go
return nil
		}
		v := types.NewFullTimeoutVote(s.cfg.Key, view, i.PrepareQC)
		i.TimeoutVote = utils.Some(v)
		isend.Store(i)
```
After
```go
return nil
		}
		// If no PrepareQC was observed in this view, inherit the one from the
		// TimeoutQC that justified entering this view. Without this,
		// consecutive timeouts (e.g. offline leader) would lose the lock and
		// allow a conflicting proposal to be committed.
		pqc := i.PrepareQC
		if tqc, ok := i.TimeoutQC.Get(); ok && !pqc.IsPresent() {
```

## Snippet 3

Context: `sei-tendermint/internal/autobahn/consensus/state_test.go:1` (changes bounds, limits, or capacity handling)

Before
```go
(no before snippet captured)
```
After
```go
package consensus

import (
	"context"
	"fmt"
	"testing"
	"time"
```

# Fix Pattern

Preserve consensus lock state at the vote-construction boundary by falling back from current-view state to the lock already carried in the justifying certificate.

## How It Was Fixed

`sei-tendermint/internal/autobahn/consensus/inner.go` changed `State.voteTimeout` to assign `pqc := i.PrepareQC`, check for a present TimeoutQC when `pqc` is absent, and set `pqc = tqc.LatestPrepareQC()` before calling `types.NewFullTimeoutVote`. Tests were added in consensus and types test files to exercise inheritance and TimeoutQC PrepareQC selection.

# Why It Matters

1. Protects a consensus safety invariant rather than confidentiality or authentication.

2. Prevents PrepareQC lock loss across consecutive timeout-driven views.

3. Keeps later proposal handling tied to the latest known PrepareQC according to the commit context.

4. The fix uses existing TimeoutQC data rather than changing protocol messages.

# Evidence Notes

Strongest direct evidence is the production hunk in `State.voteTimeout`, which changes TimeoutVote construction from unconditional `i.PrepareQC` use to a current-or-inherited PrepareQC value. The commit message and inline comment explicitly describe the safety issue and the conflicting-proposal risk. Test additions support the intended behavior. Unsupported or only partially supported by the supplied evidence: live exploitability, the full proof that two CommitQCs can form, and the exact enforcement behavior of `FullProposal.Verify`, because those code paths are not included. Protocol security invariant: Timeout-driven view changes at the same RoadIndex must preserve the latest PrepareQC lock in TimeoutVotes and TimeoutQCs so later leaders remain constrained by the reproposal rule. Dropping that lock can remove the constraint that prevents conflicting commits. Verification notes: The evidence supports a consensus safety invariant violation, not a confidentiality or authentication flaw. The patch does not prove arbitrary remote code execution or key compromise. The supplied context describes a possible conflicting-commit scenario but does not independently demonstrate a live exploit on a deployed network. No protocol schema or message-format change is shown; the fix uses an existing TimeoutQC field. The concrete behavior of FullProposal.Verify is asserted by the commit context, not shown in the provided patch hunks. Production logic changed in `sei-tendermint/internal/autobahn/consensus/inner.go`. Regression tests were added for inherited PrepareQC and consecutive timeout cases. TimeoutQC selection tests were added for mixed and highest PrepareQC cases. No command output or independent test run is provided in the input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied evidence supports retaining this as a likely consensus security fix. The production change preserves a PrepareQC lock across timeout-driven view changes by inheriting it from the justifying TimeoutQC when the current view has none, and both the commit message and inline code comment tie the prior behavior to conflicting proposals and possible duplicate CommitQCs at the same RoadIndex. The full safety proof and proposal verification path are not shown, so the finding should remain likely/medium rather than upgraded to confirmed/high.

## Security Evidence

1. Production consensus code changed TimeoutVote construction from always using current i.PrepareQC to using current-or-inherited PrepareQC.
2. Inline comment states consecutive timeouts could lose the lock and allow a conflicting proposal to be committed.
3. Commit body describes a consensus safety invariant break with two CommitQCs possible at the same RoadIndex.
4. Tests were added for inherited PrepareQC behavior, consecutive timeout chaining, persisted restart behavior, and TimeoutQC PrepareQC selection.

## Missing Evidence

1. Full pushTimeoutQC implementation is not provided.
2. FullProposal.Verify enforcement logic is asserted but not shown.
3. CommitQC formation logic and an end-to-end conflicting-commit reproduction are not included.
4. No independent test output is provided in the supplied input.

## Claim Boundaries

1. Supports a consensus-safety security fix, not confidentiality, authentication, RCE, or key compromise.
2. Exploitability depends on the broader Autobahn consensus protocol behavior not fully included in the patch evidence.
3. The validated issue is lock loss across consecutive timeouts, not a schema or wire-protocol flaw.
4. Confidence should remain medium because the supplied evidence does not independently prove the entire duplicate-commit scenario.
