---
case_id: case_20210121_253376f8d
project: oasis-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2021-01-21
source_refs:
  - git:253376f8d2942a6c85c4174086d8cffd518ad86e
  - "go/oasis-node/cmd/registry/runtime/runtime.go:459"
  - "go/registry/api/runtime.go:267"
  - "go/consensus/tendermint/apps/roothash/slashing.go:41"
  - "go/consensus/tendermint/apps/staking/state/state.go:724"
bug_class: insufficient-validator-slashing-enforcement
impact_type:
  - integrity
confidence: medium
tags:
  - consensus
  - slashing
  - validator-accountability
  - runtime
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is security-relevant accountability work, but the provided evidence does not firmly establish a concrete vulnerability fix. The shown changes add slashing-policy fields and parsing, adjust slashing execution to treat zero recovered stake as non-fatal for old evidence, and make common-pool transfers no-op cleanly when nothing can be moved.

## Observed Patch Facts

1. In `go/oasis-node/cmd/registry/runtime/runtime.go`, the patch replaces `// Validate descriptor.` with `if sl := viper.GetStringMapString(CfgStakingSlashing); sl != nil {`.

2. In `go/registry/api/runtime.go`, the patch replaces `// ValidateBasic performs basic descriptor validity checks.` with `// RewardSlashEquvocationRuntimePercent is the percentage of the reward obtained when...`.

3. In `go/consensus/tendermint/apps/roothash/slashing.go`, the patch replaces `return fmt.Errorf("tendermint/roothash: nothing to slash from account %s", entityAddr)` with `// Since evidence can be submitted for past rounds, the node can be out of stake.`.

4. In `go/consensus/tendermint/apps/staking/state/state.go`, the patch replaces `ret := !transferred.IsZero()` with `if transferred.IsZero() {`.

## Project Context

The changed code sits primarily in `go/oasis-node/cmd/registry/runtime`, `go/oasis-node/cmd/registry`, `go/registry/api`, which anchors the finding in the `staking` area of the project. Historical context from `go/consensus/tendermint/apps/roothash/slashing_test.go`, `go/consensus/tendermint/apps/roothash/transactions.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/tendermint/apps/roothash/transactions.go`, `go/consensus/tendermint/apps/roothash/roothash.go`. The strongest project-level identifiers around this patch are `staking`, `slashing`, `Errorf`, and `runtime`. Nearby tests or test-like files include `go/registry/tests/tester.go`.

## Before/After Behavior

Before the patch, the shown runtime-registration path did not include the added parsing of per-runtime slashing values from flags, the runtime staking parameters did not include the two reward-percentage fields shown here, the equivocation slashing path returned an error when nothing could be slashed, and the common-pool transfer helper did not have the shown early return on zero transfer. After the patch, those policy, validation, and edge-case handling paths are present.

# Root Cause

The evidence supports an incomplete or brittle slashing/accounting implementation: policy fields and parsing were missing from the shown registration/API paths, and the slashing/fund-transfer code handled zero-funds cases harshly. The evidence does not prove a stronger root cause such as successful acceptance of incorrect results.

## Walkthrough

1. The runtime CLI code now parses a configured slashing map into typed slash reasons and quantities before descriptor validation.

2. The runtime staking parameters type gains explicit reward-percentage fields for equivocation and bad results, with validation that each is at most 100.

3. The shown roothash slashing handler for runtime equivocation still slashes the controlling entity, but now treats a zero-slashed result as a warning and returns nil instead of failing.

4. That same slashing path introduces reward-address selection logic after the zero-slash check.

5. The staking transfer helper now returns false,nil when no funds can be moved from the common pool and continues with immediate-escrow handling only when something was transferred.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/apps/roothash/slashing.go | 17 | executes runtime misbehavior slashing and reward routing in the roothash consensus path |
| go/registry/api/runtime.go | 259 | defines per-runtime staking slashing and reward parameters used to enforce misbehavior penalties |
| go/oasis-node/cmd/registry/runtime/runtime.go | 453 | parses runtime descriptor slashing configuration so the policy can be registered |
| go/consensus/tendermint/apps/staking/state/state.go | 706 | transfers slashed/common-pool funds used by the penalty payout path |

## Code Snippets

## Snippet 1

Context: `go/oasis-node/cmd/registry/runtime/runtime.go:459` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}
	}

	// Validate descriptor.
	if err = rt.ValidateBasic(true); err != nil {
```
After
```go
}
	}
	if sl := viper.GetStringMapString(CfgStakingSlashing); sl != nil {
		rt.Staking.Slashing = make(map[staking.SlashReason]staking.Slash)
		for reasonRaw, valueRaw := range sl {
			var (
				reason staking.SlashReason
				value  quantity.Quantity
```

## Snippet 2

Context: `go/registry/api/runtime.go:267` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// Slashing are the per-runtime misbehavior slashing parameters.
	Slashing map[staking.SlashReason]staking.Slash `json:"slashing,omitempty"`
}

// ValidateBasic performs basic descriptor validity checks.
func (s *RuntimeStakingParameters) ValidateBasic(runtimeKind RuntimeKind) error {
	for kind, q := range s.Thresholds {
		switch kind {
```
After
```go
// Slashing are the per-runtime misbehavior slashing parameters.
	Slashing map[staking.SlashReason]staking.Slash `json:"slashing,omitempty"`

	// RewardSlashEquvocationRuntimePercent is the percentage of the reward obtained when slashing
	// for equivocation that is transferred to the runtime's account.
	RewardSlashEquvocationRuntimePercent uint8 `json:"reward_equivocation,omitempty"`

	// RewardSlashBadResultsRuntimePercent is the percentage of the reward obtained when slashing
```

## Snippet 3

Context: `go/consensus/tendermint/apps/roothash/slashing.go:41` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return fmt.Errorf("tendermint/roothash: error slashing account %s: %w", entityAddr, err)
	}
	if totalSlashed.IsZero() {
		return fmt.Errorf("tendermint/roothash: nothing to slash from account %s", entityAddr)
	}

	// Move slashed amount to the runtime account.
	// TODO: part of slashed amount (configurable) should be transferred to the transaction submitter.
```
After
```go
return fmt.Errorf("tendermint/roothash: error slashing account %s: %w", entityAddr, err)
	}
	// Since evidence can be submitted for past rounds, the node can be out of stake.
	if totalSlashed.IsZero() {
		ctx.Logger().Warn("nothing to slash from entity for runtime equivocation",
			"penalty", penaltyAmount,
			"addr", entityAddr,
		)
```

## Snippet 4

Context: `go/consensus/tendermint/apps/staking/state/state.go:724` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return false, fmt.Errorf("tendermint/staking: failed to transfer from common pool: %w", err)
	}

	ret := !transferred.IsZero()
	if ret {
		if err = s.SetCommonPool(ctx, commonPool); err != nil {
			return false, fmt.Errorf("tendermint/staking: failed to set common pool: %w", err)
		}
```
After
```go
return false, fmt.Errorf("tendermint/staking: failed to transfer from common pool: %w", err)
	}
	if transferred.IsZero() {
		// Common pool has been depleated, nothing to transfer.
		return false, nil
	}

	// If escrow is requested, escrow the transferred stake immediately.
```

# Fix Pattern

Add missing policy/configuration fields and make slashing-related fund movement tolerant of zero-funds edge cases.

## How It Was Fixed

The patch wires per-runtime slashing settings into runtime configuration and API validation, then adjusts slashing and transfer helpers so stale-evidence or empty-pool cases do not abort the operation path. The visible changes look like support and robustness work for runtime slashing rather than standalone proof of an exploitable bug.

# Why It Matters

1. Misbehavior penalties depend on configuration being expressible and validated.

2. Old evidence should not crash or abort processing just because stake is already depleted.

3. Reward-routing and transfer code needs defined behavior when zero funds are available.

4. These changes improve accountability plumbing even if exploitability is not shown.

# Evidence Notes

The strongest grounded evidence is limited to policy-field additions, CLI parsing, a zero-slash behavior change in the equivocation handler, and a zero-transfer behavior change in staking state. The commit subject mentions incorrect results, and one added field is named for bad-results rewards, but the provided hunks do not show the actual incorrect-results slashing logic itself. The evidence therefore supports security-relevant hardening/plumbing, not a confirmed vulnerability fix. Protocol security invariant: Runtime misbehavior penalties should be representable in the runtime staking parameters and processed without failing on expected edge cases such as stale evidence or zero available funds. Verification notes: The patch evidence does not prove that incorrect results were previously accepted into finalized state. The patch evidence does not prove a concrete attacker profit path or bypass of all other consensus checks. The shown hunks do not establish whether the change fixes an exploitable vulnerability versus strengthening economic deterrence and protocol accountability. Helper changes in CLI parsing and staking transfers are supportive plumbing, not standalone proof of a separate security bug. The provided snippets do not show a direct before/after enforcement path for incorrect results. No evidence here proves prior acceptance of invalid results, attacker profit, or consensus compromise. Tests are mentioned in the file list, but no test diff is provided in the evidence excerpt. Commit metadata suggests security relevance, but the vulnerability thesis remains unproven from the supplied code. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-validator-slashing-enforcement`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `consensus, slashing, validator-accountability, runtime`

The supplied patch evidence supports keeping this as a security-hardening case, not as a confirmed vulnerability fix. The changes clearly operate in a security-sensitive consensus and staking path: they add runtime slashing configuration, validate slashing reward percentages, and adjust evidence-handling and fund-transfer behavior so slashing-related processing does not fail on zero-stake or zero-pool edge cases. That strengthens validator accountability and misbehavior handling. However, the excerpts do not directly show a concrete exploitable flaw being fixed or prove that incorrect results were previously accepted into finalized state.

## Security Evidence

1. The commit subject is about slashing runtime compute nodes for incorrect results, which is a security-sensitive consensus accountability function.
2. `RuntimeStakingParameters` gains explicit slashing reward percentage fields with bounds checks, tightening misbehavior-penalty configuration.
3. The runtime registration path adds parsing for per-runtime slashing settings, indicating new or strengthened enforcement plumbing.
4. `onEvidenceRuntimeEquivocation` is part of the consensus evidence-processing path and was changed to handle stale-evidence zero-stake cases without aborting.
5. `TransferFromCommon` now handles zero-transfer cases explicitly in slashing/reward-related fund movement, making penalty processing more robust.

## Missing Evidence

1. No excerpt shows the actual detection or enforcement path for `incorrect results` itself.
2. No before/after snippet proves a validator could previously avoid slashing for bad results.
3. No evidence shows prior acceptance of invalid state transitions, finalized bad results, or attacker-controlled consensus impact.
4. Test diffs are mentioned in file lists but not included in the provided evidence.

## Claim Boundaries

1. This supports security hardening of validator accountability and slashing behavior.
2. This does not prove a concrete exploitable vulnerability was fixed.
3. This does not establish prior consensus compromise or invalid-result finalization from the shown hunks alone.
4. The original `serialization-or-state-representation` classification is not supported by the provided patch evidence.
