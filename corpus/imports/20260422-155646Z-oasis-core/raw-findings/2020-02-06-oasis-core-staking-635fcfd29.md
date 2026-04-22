---
case_id: case_20200206_635fcfd29
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2020-02-06
source_refs:
  - git:635fcfd29eedd917235b363f313afe68c347f0dc
  - "go/consensus/tendermint/apps/registry/transactions.go:556"
  - "go/consensus/tendermint/apps/keymanager/keymanager.go:111"
  - "go/consensus/tendermint/apps/keymanager/keymanager.go:96"
  - "go/consensus/tendermint/apps/roothash/roothash.go:123"
bug_class: missing-stake-enforcement
impact_type:
  - policy-bypass
  - improper-runtime-admission
confidence: medium
tags:
  - consensus
  - staking
  - runtime-registration
  - economic-guards
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided diff shows new stake/deposit checks for runtime registration and for keeping registered runtimes active. That is plausibly security relevant because it adds consensus gating, but the evidence does not establish that this was fixing a pre-existing vulnerability rather than introducing or tightening a new economic policy.

## Observed Patch Facts

1. In `go/consensus/tendermint/apps/registry/transactions.go`, the patch replaces `// If TEE is required, check if runtime provided at least one enclave ID.` with `if !params.DebugBypassStake {`.

2. In `go/consensus/tendermint/apps/keymanager/keymanager.go`, the patch replaces `var forceEmit bool` with `// Suspend the runtime in case the registering entity no longer has enough stake to c...`.

3. In `go/consensus/tendermint/apps/keymanager/keymanager.go`, the patch replaces `//` with `params, err := regState.ConsensusParameters()`.

4. In `go/consensus/tendermint/apps/roothash/roothash.go`, the patch replaces `if empty && !params.DebugDoNotSuspendRuntimes {` with `//`.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/apps/registry`, `go/consensus/tendermint/apps`, `go/consensus/tendermint/apps/keymanager`, which anchors the finding in the `staking` area of the project. Historical context from `go/consensus/tendermint/apps/registry/registry.go`, `go/consensus/tendermint/apps/registry/genesis.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/tendermint/apps/scheduler/scheduler.go`, `go/consensus/tendermint/apps/registry/registry.go`. The strongest project-level identifiers around this patch are `runtime`, `entity`, `stake`, and `params`.

## Before/After Behavior

Before the patch, the shown registration, key manager epoch, and roothash committee-change paths did not include the displayed `EnsureSufficientRuntimeStake` checks at those points. After the patch, registration fails for insufficient runtime stake and existing runtimes can be suspended during epoch or committee processing when stake is insufficient, unless `DebugBypassStake` is enabled.

# Root Cause

The affected paths previously lacked explicit runtime stake/deposit checks at the shown admission and lifecycle transition points. From the provided evidence alone, it is not proven whether that absence was a vulnerability or simply behavior that this change intentionally tightened.

## Walkthrough

1. `registerRuntime` now calls `EnsureSufficientRuntimeStake(ctx, rt)` under `!params.DebugBypassStake` and returns an error if the entity lacks sufficient stake.

2. `keymanagerApplication.onEpochChange` now loads consensus parameters and checks each key manager runtime's stake sufficiency before continuing normal status handling.

3. If that key manager check fails, the runtime is suspended instead of remaining active.

4. `rootHashApplication.onCommitteeChanged` keeps the existing empty-committee suspension logic and adds a stake sufficiency check for runtimes that would otherwise stay active.

5. The new comments explicitly tie the check to covering entity and runtime deposits, but the excerpts do not prove whether those deposits were previously required or newly introduced here.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/apps/registry/transactions.go | 511 | runtime registration path now rejects entities without sufficient runtime stake |
| go/consensus/tendermint/apps/keymanager/keymanager.go | 91 | epoch transition path now suspends key manager runtimes whose entity no longer meets stake requirements |
| go/consensus/tendermint/apps/roothash/roothash.go | 89 | committee-change path now suspends compute runtimes when the owning entity lacks required stake |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/apps/registry/transactions.go:556` (changes a sensitive control or state-update path)

Before
```go
}

	// If TEE is required, check if runtime provided at least one enclave ID.
	if rt.TEEHardware != node.TEEHardwareInvalid {
```
After
```go
}

	if !params.DebugBypassStake {
		// Make sure that the entity has enough stake for at least being an entity and having a
		// runtime (separate thresholds for compute and key manager runtimes).
		if err = registryState.EnsureSufficientRuntimeStake(ctx, rt); err != nil {
			ctx.Logger().Error("RegisterRuntime: Insufficent stake",
				"err", err,
```

## Snippet 2

Context: `go/consensus/tendermint/apps/keymanager/keymanager.go:111` (changes a sensitive control or state-update path)

Before
```go
}

		var forceEmit bool
		oldStatus, err := state.Status(rt.ID)
```
After
```go
}

		// Suspend the runtime in case the registering entity no longer has enough stake to cover
		// the entity and runtime deposits.
		if !params.DebugBypassStake {
			if err = registryState.EnsureSufficientRuntimeStake(ctx, rt); err != nil {
				ctx.Logger().Warn("insufficient stake for key manager runtime operation",
					"err", err,
```

## Snippet 3

Context: `go/consensus/tendermint/apps/keymanager/keymanager.go:96` (changes a consensus- or validator-sensitive branch)

Before
```go
registry.SortNodeList(nodes)

	// Recalculate all the key manager statuses.
	//
```
After
```go
registry.SortNodeList(nodes)

	params, err := regState.ConsensusParameters()
	if err != nil {
		return fmt.Errorf("failed to get consensus parameters: %w", err)
	}

	// Recalculate all the key manager statuses.
```

## Snippet 4

Context: `go/consensus/tendermint/apps/roothash/roothash.go:123` (changes a sensitive control or state-update path)

Before
```go
// If there are no committees for this runtime, suspend the runtime as this
		// means that there is noone to pay the maintenance fees.
		if empty && !params.DebugDoNotSuspendRuntimes {
			if err := app.suspendUnpaidRuntime(ctx, rtState, regState); err != nil {
				return err
```
After
```go
// If there are no committees for this runtime, suspend the runtime as this
		// means that there is noone to pay the maintenance fees.
		//
		// Also suspend the runtime in case the registering entity no longer has enough stake to
		// cover the entity and runtime deposits (this check is skipped if the runtime would be
		// suspended anyway due to nobody being there to pay maintenance fees).
		sufficientStake := true
		if !empty && !params.DebugBypassStake {
```

# Fix Pattern

Add a shared runtime stake/deposit sufficiency check and apply it at both registration time and later lifecycle maintenance points, rejecting or suspending runtimes that do not meet the configured threshold.

## How It Was Fixed

The patch fetches consensus parameters where needed, gates the behavior on `DebugBypassStake`, invokes `EnsureSufficientRuntimeStake`, and uses the result to reject runtime registration or suspend already-registered runtimes in key manager and roothash flows.

# Why It Matters

1. It prevents under-staked runtimes from being admitted when the new check is enabled.

2. It lets consensus logic disable runtimes that later fall below the configured stake requirement.

3. It makes runtime lifecycle behavior more consistent across registration and ongoing operation.

4. The evidence does not show theft, corruption, replay protection, or a demonstrated exploit.

# Evidence Notes

The strongest evidence is the added `EnsureSufficientRuntimeStake` calls in `registry/transactions.go`, `keymanager/keymanager.go`, and `roothash/roothash.go`, plus comments about covering entity and runtime deposits. The commit subject, `Optionally require a deposit for registering a runtime`, and the breaking-change note point toward a policy/protocol change. The provided excerpts do not show the helper implementation, prior threshold semantics, exploitability, or proof that a previously intended invariant was being violated. Protocol security invariant: When runtime deposit enforcement is enabled, runtime registration and continued runtime operation are intended to require the owning entity to satisfy the relevant stake thresholds. Verification notes: The patch does not show a cryptographic signature, nonce, or replay-validation fix. The patch does not prove live exploitability or prior real-world abuse. The patch does not show theft or state corruption; the visible consequence is unauthorized runtime admission/continuation under insufficient stake. The exact deposit economics, slashing behavior, and threshold values are not proven from the provided diff. Because the feature is optional and debug bypasses remain, this is best treated as protocol security hardening rather than a fully demonstrated vulnerability fix. Assessment is limited to the provided excerpts and metadata. The helper `EnsureSufficientRuntimeStake` implementation is not shown, so exact enforcement semantics are unknown. The evidence does not show whether runtime deposits existed before this commit or were introduced here. No test diff or runtime behavior trace is provided that demonstrates an actual exploitable failure before the patch. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-stake-enforcement`
Final impact type: `policy-bypass, improper-runtime-admission`
Final confidence: `medium`
Final tags: `consensus, staking, runtime-registration, economic-guards`

The patch does not support the original replay/signature-validation claim, but it does clearly add stake/deposit enforcement on runtime registration and continued runtime operation in consensus-critical paths. That is best treated as security hardening: it tightens an admission and lifecycle control that limits who can register or keep operating runtimes, yet the provided diff does not prove a concrete exploitable vulnerability or real-world abuse before the change.

## Security Evidence

1. `registerRuntime` now rejects runtime registration when `EnsureSufficientRuntimeStake` fails.
2. Key manager epoch processing now checks runtime stake sufficiency and suspends runtimes that no longer meet deposit requirements.
3. Roothash committee-change handling now also suspends runtimes whose owning entity lacks sufficient stake.
4. The new checks are applied in consensus-sensitive runtime admission and lifecycle paths, not just in tests or metadata.
5. Comments explicitly tie the new behavior to covering entity and runtime deposits.

## Missing Evidence

1. No evidence shows an attacker could previously exploit this for theft, replay, signature bypass, or state corruption.
2. The helper implementation for `EnsureSufficientRuntimeStake` is not shown, so exact enforcement semantics are not proven.
3. The patch does not prove whether deposits already existed and were accidentally unenforced, or were being introduced here as a new protocol rule.
4. No test excerpt or incident evidence demonstrates a concrete pre-patch vulnerability.

## Claim Boundaries

1. Supported claim: the commit hardens runtime registration and runtime lifecycle handling by enforcing stake/deposit requirements.
2. Supported claim: insufficiently staked runtimes could previously remain admissible or active in the shown paths.
3. Not supported: replay protection, signature validation, forgery, or nonce handling issues.
4. Not supported: a demonstrated exploitable security bug with confirmed impact beyond policy/economic enforcement.
