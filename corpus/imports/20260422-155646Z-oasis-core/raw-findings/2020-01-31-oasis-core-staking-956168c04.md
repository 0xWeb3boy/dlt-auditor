---
case_id: case_20200131_956168c04
project: oasis-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2020-01-31
source_refs:
  - git:956168c0474d2406bd4a7b5e110df7dd13a27403
  - "go/consensus/tendermint/apps/staking/slashing.go:73"
  - "go/consensus/tendermint/apps/staking/staking.go:71"
  - "go/consensus/tendermint/apps/staking/slashing.go:13"
  - "go/consensus/tendermint/apps/staking/slashing_test.go:1"
bug_class: integer-overflow
impact_type:
  - integrity
confidence: medium
tags:
  - integer-overflow
  - validator-slashing
  - consensus
  - staking
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes an unchecked overflow in validator slashing state updates by guarding `epoch + penalty.FreezeInterval` and using `registry.FreezeForever` on overflow. The code is in a security-sensitive validator-penalty path, but the provided evidence does not establish that the overflow was practically reachable or exploitable, so the security classification is unclear.

## Observed Patch Facts

1. In `go/consensus/tendermint/apps/staking/slashing.go`, the patch replaces `epoch, err = app.state.GetEpoch(context.Background(), ctx.BlockHeight()+1)` with `epoch, err = ctx.AppState().GetEpoch(context.Background(), ctx.BlockHeight()+1)`.

2. In `go/consensus/tendermint/apps/staking/staking.go`, the patch replaces `if err := app.onEvidenceDoubleSign(ctx, evidence.Validator.Address, evidence.Height,...` with `if err := onEvidenceDoubleSign(ctx, evidence.Validator.Address, evidence.Height, evid...`.

3. In `go/consensus/tendermint/apps/staking/slashing.go`, the patch replaces `func (app *stakingApplication) onEvidenceDoubleSign(` with `registry "github.com/oasislabs/oasis-core/go/registry/api"`.

4. In `go/consensus/tendermint/apps/staking/slashing_test.go`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/apps/staking`, `go/consensus/tendermint/apps`, which anchors the finding in the `staking` area of the project. Historical context from `go/consensus/tendermint/apps/staking/transactions.go`, `go/consensus/tendermint/apps/staking/signing_rewards.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/tendermint/apps/staking/transactions.go`, `go/consensus/tendermint/apps/staking/signing_rewards.go`. The strongest project-level identifiers around this patch are `evidence`, `oasislabs`, `oasis`, and `core`.

## Before/After Behavior

Before the patch, the double-sign handler assigned `nodeStatus.FreezeEndTime = epoch + penalty.FreezeInterval` directly after reading the current epoch. After the patch, it checks `math.MaxUint64-penalty.FreezeInterval < epoch` and sets `nodeStatus.FreezeEndTime = registry.FreezeForever` on overflow, otherwise keeping the bounded addition.

# Root Cause

Unchecked integer addition when deriving `nodeStatus.FreezeEndTime` from the current epoch and the configured freeze interval.

## Walkthrough

1. `BeginBlock` iterates `request.ByzantineValidators` and routes duplicate-vote evidence into `onEvidenceDoubleSign`.

2. The slashing handler resolves the validator, loads node status, and reads the slashing parameters for double signing.

3. When `penalty.FreezeInterval > 0`, the handler fetches the current epoch for `ctx.BlockHeight()+1`.

4. Before the patch, it stored `epoch + penalty.FreezeInterval` directly in `nodeStatus.FreezeEndTime`.

5. After the patch, it checks for overflow before the addition.

6. If the addition would overflow, it stores `registry.FreezeForever`; otherwise it stores the computed sum.

7. A new test file was added, but the supplied evidence does not show the test body, so only the existence of regression coverage is supported.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/apps/staking/staking.go | 71 | BeginBlock entry point that routes Tendermint duplicate-vote evidence into staking slashing |
| go/consensus/tendermint/apps/staking/slashing.go | 19 | Double-sign evidence handler that resolves the validator and applies freeze/slash state transitions |
| go/consensus/tendermint/apps/staking/slashing.go | 73 | Freeze end-time computation changed from unchecked addition to overflow-safe fail-closed assignment |
| go/consensus/tendermint/apps/staking/slashing_test.go | 1 | Regression coverage for the overflow boundary in slashing behavior |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/apps/staking/slashing.go:73` (changes a consensus- or validator-sensitive branch)

Before
```go
if penalty.FreezeInterval > 0 {
		var epoch epochtime.EpochTime
		epoch, err = app.state.GetEpoch(context.Background(), ctx.BlockHeight()+1)
		if err != nil {
			return err
		}

		nodeStatus.FreezeEndTime = epoch + penalty.FreezeInterval
```
After
```go
if penalty.FreezeInterval > 0 {
		var epoch epochtime.EpochTime
		epoch, err = ctx.AppState().GetEpoch(context.Background(), ctx.BlockHeight()+1)
		if err != nil {
			return err
		}

		// Check for overflow.
```

## Snippet 2

Context: `go/consensus/tendermint/apps/staking/staking.go:71` (changes a consensus- or validator-sensitive branch)

Before
```go
switch evidence.Type {
		case tmtypes.ABCIEvidenceTypeDuplicateVote:
			if err := app.onEvidenceDoubleSign(ctx, evidence.Validator.Address, evidence.Height, evidence.Time, evidence.Validator.Power); err != nil {
				return err
			}
```
After
```go
switch evidence.Type {
		case tmtypes.ABCIEvidenceTypeDuplicateVote:
			if err := onEvidenceDoubleSign(ctx, evidence.Validator.Address, evidence.Height, evidence.Time, evidence.Validator.Power); err != nil {
				return err
			}
```

## Snippet 3

Context: `go/consensus/tendermint/apps/staking/slashing.go:13` (changes a sensitive control or state-update path)

Before
```go
stakingState "github.com/oasislabs/oasis-core/go/consensus/tendermint/apps/staking/state"
	epochtime "github.com/oasislabs/oasis-core/go/epochtime/api"
	staking "github.com/oasislabs/oasis-core/go/staking/api"
)

func (app *stakingApplication) onEvidenceDoubleSign(
	ctx *abci.Context,
	addr tmcrypto.Address,
```
After
```go
stakingState "github.com/oasislabs/oasis-core/go/consensus/tendermint/apps/staking/state"
	epochtime "github.com/oasislabs/oasis-core/go/epochtime/api"
	registry "github.com/oasislabs/oasis-core/go/registry/api"
	staking "github.com/oasislabs/oasis-core/go/staking/api"
)

func onEvidenceDoubleSign(
	ctx *abci.Context,
```

## Snippet 4

Context: `go/consensus/tendermint/apps/staking/slashing_test.go:1` (changes signature or replay validation logic)

Before
```go
(no before snippet captured)
```
After
```go
package staking

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
```

# Fix Pattern

Add an explicit overflow check around state-transition arithmetic and substitute a safe sentinel value when the intended result is not representable.

## How It Was Fixed

The fix changed the freeze-end calculation from raw addition to guarded logic. It imports `registry`, checks whether `epoch + penalty.FreezeInterval` would overflow `uint64`, and records `registry.FreezeForever` instead of allowing wraparound.

# Why It Matters

1. It prevents wraparound in validator penalty state.

2. It preserves the intended freeze semantics when the computed end time is not representable.

3. The evidence supports a correctness fix in a sensitive path, but not a proven exploit.

# Evidence Notes

The strongest direct evidence is the changed hunk in `go/consensus/tendermint/apps/staking/slashing.go` replacing `nodeStatus.FreezeEndTime = epoch + penalty.FreezeInterval` with an overflow check and `registry.FreezeForever`. `go/consensus/tendermint/apps/staking/staking.go` shows the path is reached from duplicate-vote evidence handling in `BeginBlock`. The method-to-function and `app.state` to `ctx.AppState()` changes are supported as refactoring/plumbing around the fix, not as separate vulnerability evidence. The provided material does not show test assertions, attacker control, or real-world reachability of near-maximum epochs. Protocol security invariant: When duplicate-vote evidence is processed, the recorded validator freeze end time should preserve the configured penalty and must not wrap if `epoch + FreezeInterval` exceeds the representable epoch range. Verification notes: The patch does not prove an external attacker can force `epoch` near `MaxUint64` in normal operation. The patch does not show fund theft, signature bypass, or arbitrary state corruption. The patch does not establish a network-wide consensus split; it shows a validator-penalty state bug in a consensus-sensitive path. The `app.state` to `ctx.AppState()` and method-to-function changes look like plumbing around the fix, not independent security issues. Overflow handling is directly visible in the provided diff. Evidence confirms the affected path is duplicate-vote slashing during `BeginBlock`. Exploitability is not established by the supplied snippets. Test coverage presence is visible, but test semantics are not. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `integer-overflow, validator-slashing, consensus, staking`

The patch directly hardens a security-sensitive validator-slashing path by preventing `epoch + penalty.FreezeInterval` from wrapping and by failing closed to `FreezeForever` when overflow would occur. That supports treating it as security hardening for penalty-enforcement integrity. However, the provided evidence does not prove realistic reachability, attacker control over the overflow condition, or a demonstrated exploitable bypass, so this should not be elevated to a confirmed security-fix case.

## Security Evidence

1. The changed code is in duplicate-vote evidence handling for validator slashing during `BeginBlock`.
2. The fix adds an explicit overflow guard before computing `nodeStatus.FreezeEndTime`.
3. On overflow, the new behavior uses `registry.FreezeForever`, which is a fail-closed penalty outcome.
4. Without the guard, unsigned wraparound could produce an incorrect freeze end time in validator penalty state.
5. The commit message explicitly names an epoch-time overflow in a consensus/staking subsystem.

## Missing Evidence

1. No proof that `epoch` can realistically approach `MaxUint64` in deployed operation is shown.
2. No exploit or concrete scenario demonstrates that a validator could use this to evade slashing or rejoin early.
3. The supplied test evidence does not show assertions, so behavioral security guarantees are not directly verified.
4. The patch alone does not show broader consequences such as consensus split, fund loss, or externally triggerable corruption.

## Claim Boundaries

1. Supported claim: this patch hardens overflow handling in validator freeze-end computation.
2. Supported claim: the affected code is security-sensitive because it enforces duplicate-vote penalties.
3. Not supported: a concrete exploitable vulnerability was definitely present in production.
4. Not supported: the issue caused proven liveness loss, fund theft, or consensus failure.
5. The method-to-function and state-access refactors should be treated as plumbing around the overflow fix, not separate security evidence.
