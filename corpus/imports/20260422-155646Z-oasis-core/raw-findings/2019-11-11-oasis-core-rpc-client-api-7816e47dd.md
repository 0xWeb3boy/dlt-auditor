---
case_id: case_20191111_7816e47dd
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2019-11-11
source_refs:
  - git:7816e47ddf3982530cdc61a3bd9e4a2f3e3e36d0
  - "go/tendermint/apps/scheduler/genesis.go:39"
  - "go/tendermint/apps/scheduler/scheduler.go:580"
  - "go/scheduler/api/api.go:194"
  - "go/oasis-node/cmd/genesis/genesis.go:179"
bug_class: validator-selection-policy
impact_type:
  - validator-selection-integrity
  - consensus-policy-enforcement
confidence: medium
tags:
  - blockchain-core
  - consensus
  - validator-election
  - configuration-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a dedicated `ValidatorEntityThreshold` consensus parameter, threads it through genesis creation, validates that it is set, and uses it when truncating the stake-ranked entity list during validator election. That is a consensus-policy change in a security-sensitive path, but the provided evidence does not show that the prior `topN` behavior was vulnerable rather than simply less explicit or less configurable.

## Observed Patch Facts

1. In `go/tendermint/apps/scheduler/genesis.go`, the patch adds `if doc.Scheduler.Parameters.ValidatorEntityThreshold <= 0 {`.

2. In `go/tendermint/apps/scheduler/scheduler.go`, the patch replaces `if len(sortedEntities) > topN {` with `if len(sortedEntities) > params.ValidatorEntityThreshold {`.

3. In `go/scheduler/api/api.go`, the patch replaces `// the staking related checks and operations.` with `// ValidatorEntityThreshold is the cutoff point (by escrow balance)`.

4. In `go/oasis-node/cmd/genesis/genesis.go`, the patch replaces `MinValidators: viper.GetInt(cfgSchedulerMinValidators),` with `MinValidators: viper.GetInt(cfgSchedulerMinValidators),`.

## Project Context

The changed code sits primarily in `go/tendermint/apps/scheduler`, `go/tendermint/apps`, `go/scheduler/api`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `go/tendermint/apps/scheduler/query.go`, `go/tendermint/apps/scheduler/api.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/oasis-node/cmd/registry/runtime/runtime.go`, `go/oasis-node/cmd/registry/node/node.go`. The strongest project-level identifiers around this patch are `viper`, `ValidatorEntityThreshold`, `sortedEntities`, and `scheduler`. Nearby tests or test-like files include `go/scheduler/tests/tester.go`.

## Before/After Behavior

Before the change, scheduler consensus parameters exposed `MinValidators` and `MaxValidators`, genesis construction did not supply `ValidatorEntityThreshold`, `InitChain` did not reject a missing entity-threshold value, and validator election truncated `sortedEntities` using `topN`. After the change, `ValidatorEntityThreshold` is added as a consensus parameter, genesis populates it from configuration, `InitChain` rejects nonpositive values, and election truncates `sortedEntities` using `params.ValidatorEntityThreshold`.

# Root Cause

The visible issue is that the entity-level cutoff used in validator election was not represented as its own explicit, validated consensus parameter. Instead, the election path used `topN`, and the patch separates that policy into `ValidatorEntityThreshold` and requires it to be configured.

## Walkthrough

1. `go/scheduler/api/api.go` adds `ValidatorEntityThreshold` to `ConsensusParameters` and documents it as the top-N entities by escrow balance that remain eligible for validator election.

2. `go/oasis-node/cmd/genesis/genesis.go` starts writing `ValidatorEntityThreshold` into the scheduler genesis parameters from configuration.

3. `go/tendermint/apps/scheduler/genesis.go` adds an initialization check that rejects genesis documents where `ValidatorEntityThreshold <= 0`.

4. `go/tendermint/apps/scheduler/scheduler.go` continues filtering nodes by validator role and stake-related checks, then sorts eligible entities by stake.

5. The truncation step changes from `topN` to `params.ValidatorEntityThreshold`, making the entity cutoff an explicit consensus input.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/tendermint/apps/scheduler/scheduler.go | 560 | consensus validator-election logic that limits which staked entities are eligible for node selection |
| go/tendermint/apps/scheduler/genesis.go | 20 | genesis-time validation that the validator-entity eligibility threshold is configured |
| go/scheduler/api/api.go | 187 | consensus parameter definition for scheduler validator-eligibility policy |
| go/oasis-node/cmd/genesis/genesis.go | 173 | genesis construction path wiring operator configuration into scheduler consensus parameters |

## Code Snippets

## Snippet 1

Context: `go/tendermint/apps/scheduler/genesis.go:39` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return fmt.Errorf("tendermint/scheduler: maximum number of validators not configured")
	}

	regState := registryState.NewMutableState(ctx.State())
```
After
```go
return fmt.Errorf("tendermint/scheduler: maximum number of validators not configured")
	}
	if doc.Scheduler.Parameters.ValidatorEntityThreshold <= 0 {
		return fmt.Errorf("tendermint/scheduler: validator entity threshold not configured")
	}

	regState := registryState.NewMutableState(ctx.State())
```

## Snippet 2

Context: `go/tendermint/apps/scheduler/scheduler.go:580` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return err
	}
	if len(sortedEntities) > topN {
		sortedEntities = sortedEntities[:topN]
	}
	entMap = make(map[signature.MapKey]bool)
```
After
```go
return err
	}
	if len(sortedEntities) > params.ValidatorEntityThreshold {
		sortedEntities = sortedEntities[:params.ValidatorEntityThreshold]
	}
	entMap = make(map[signature.MapKey]bool)
```

## Snippet 3

Context: `go/scheduler/api/api.go:194` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
MaxValidators int `json:"max_validators"`

	// DebugBypassStake is true iff the scheduler should bypass all of
	// the staking related checks and operations.
```
After
```go
MaxValidators int `json:"max_validators"`

	// ValidatorEntityThreshold is the cutoff point (by escrow balance)
	// of the top-N entities running validator nodes, to be eligible
	// for the entity's nodes to be elected as a validator.
	ValidatorEntityThreshold int `json:"validator_entity_threshold"`

	// DebugBypassStake is true iff the scheduler should bypass all of
```

## Snippet 4

Context: `go/oasis-node/cmd/genesis/genesis.go:179` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
doc.Scheduler = scheduler.Genesis{
		Parameters: scheduler.ConsensusParameters{
			MinValidators:         viper.GetInt(cfgSchedulerMinValidators),
			MaxValidators:         viper.GetInt(cfgSchedulerMaxValidators),
			DebugBypassStake:      viper.GetBool(cfgSchedulerDebugBypassStake),
			DebugStaticValidators: viper.GetBool(cfgSchedulerDebugStaticValidators),
		},
	}
```
After
```go
doc.Scheduler = scheduler.Genesis{
		Parameters: scheduler.ConsensusParameters{
			MinValidators:            viper.GetInt(cfgSchedulerMinValidators),
			MaxValidators:            viper.GetInt(cfgSchedulerMaxValidators),
			ValidatorEntityThreshold: viper.GetInt(cfgSchedulerValidatorEntityThreshold),
			DebugBypassStake:         viper.GetBool(cfgSchedulerDebugBypassStake),
			DebugStaticValidators:    viper.GetBool(cfgSchedulerDebugStaticValidators),
		},
```

# Fix Pattern

Turn an implicit consensus-policy cutoff into an explicit parameter, plumb it through configuration/genesis, validate it at initialization, and consume that parameter directly in the selection path.

## How It Was Fixed

The patch introduces `ValidatorEntityThreshold`, stores it in consensus parameters, requires it to be configured during chain initialization, and uses it when limiting the set of stake-ranked entities considered for validator election.

# Why It Matters

1. Validator election is a consensus-critical path.

2. The entity eligibility cutoff is now explicit instead of inferred from another variable.

3. Genesis validation now rejects an unset threshold.

4. The evidence supports policy hardening or parameterization, not a demonstrated exploit fix.

# Evidence Notes

The direct evidence is limited to adding a new consensus parameter, wiring it into genesis, validating that it is positive, and swapping the election truncation from `topN` to `params.ValidatorEntityThreshold`. Nothing in the provided diff shows what `topN` semantically represented before, whether its old value was wrong, whether unauthorized validators could be elected, or whether consensus safety/liveness had been at risk. The stronger RPC/serialization explanation from the heuristic baseline is not supported by the shown code. Protocol security invariant: Validator election should apply explicitly defined eligibility limits consistently at genesis and during validator selection; the evidence shows this limit became a separate configured parameter, but does not establish that the prior behavior violated safety or allowed an exploit. Verification notes: The patch does not prove the old behavior allowed an attacker to become a validator without satisfying stake checks. It does not show a concrete consensus split, liveness failure, or economic exploit caused by the previous `topN` cutoff. It does not prove that any deployed network used unsafe threshold values before this change. It does not support the heuristic claim that this is primarily an RPC or serialization-state fix. Need the surrounding definition and prior meaning of `topN` to determine whether the old behavior was incorrect or just less explicit. Need evidence of an actual bad pre-patch outcome to classify this as a security fix rather than policy hardening. The provided snippets do not establish attacker control, privilege bypass, consensus split, or economic impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validator-selection-policy`
Final impact type: `validator-selection-integrity, consensus-policy-enforcement`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, validator-election, configuration-validation`

The patch operates in validator-election and genesis-validation code, which is security-sensitive in a blockchain system, and it introduces an explicit, required consensus parameter that constrains which entities are eligible for validator election. That supports a security-hardening reading: the change tightens and validates validator-selection policy. However, the diff does not prove that the prior `topN` behavior was exploitable or incorrect, so this should not be treated as a confirmed security bug fix.

## Security Evidence

1. Adds a dedicated `ValidatorEntityThreshold` consensus parameter for validator eligibility.
2. Rejects genesis documents where `ValidatorEntityThreshold` is unset or nonpositive.
3. Uses the explicit threshold in validator election when truncating eligible entities by stake.
4. Change is in consensus-critical validator-selection logic, not just comments or refactoring.

## Missing Evidence

1. No proof that prior `topN` semantics allowed unauthorized or unsafe validator election.
2. No evidence of attacker control, privilege bypass, consensus split, or economic exploit.
3. No regression test or commit message excerpt tying the change to a concrete vulnerability.
4. No context showing whether `topN` already enforced the same effective limit before the patch.

## Claim Boundaries

1. This supports security hardening of validator-election policy, not a demonstrated exploit fix.
2. The evidence does not support the original `rpc-client-api` / serialization framing.
3. The patch shows stricter consensus configuration and eligibility enforcement only.
4. Any stronger claim about prior network compromise or validator takeover would be speculative.
