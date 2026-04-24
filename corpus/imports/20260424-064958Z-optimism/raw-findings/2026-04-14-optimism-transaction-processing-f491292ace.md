---
case_id: case_20260414_f491292ace
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2026-04-14
source_refs:
  - git:f491292aced7c3ce43354927fa88c73f32f370b9
  - "op-devstack/dsl/eoa.go:338"
  - "op-devstack/sysgo/multichain_supernode_runtime.go:238"
  - "op-supernode/supernode/supernode.go:105"
  - "op-devstack/sysgo/multichain_supernode_runtime.go:130"
bug_class: validation-configuration-mismatch
impact_type:
  - validation-bypass-risk
confidence: medium
tags:
  - blockchain-core
  - interop
  - message-expiry
  - validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a configuration-consistency fix in supernode interop validation, plus test migration and scaffolding. It does not by itself establish a production vulnerability or a confirmed security fix.

## Observed Patch Facts

1. In `op-devstack/dsl/eoa.go`, the patch replaces `// SendInvalidExecMessage sends an executing message with an invalid identifier.` with `// PrepareExecTx builds and signs an executing-message transaction referencing`.

2. In `op-devstack/sysgo/multichain_supernode_runtime.go`, the patch replaces `return &MultiChainRuntime{` with `// Use the potentially-overridden depSet (e.g. with custom message expiry window)`.

3. In `op-supernode/supernode/supernode.go`, the patch replaces `interopActivity := interop.New(log.New("activity", "interop"), *interopActivationTime...` with `// Extract the message expiry window from the first virtual node's dependency set.`.

4. In `op-devstack/sysgo/multichain_supernode_runtime.go`, the patch replaces `supernode, l2CL := startSingleChainSharedSupernode(t, l1Net, l1EL, l1CL, l2Net, l2EL,...` with `if cfg.MessageExpiryWindow != nil && depSetStatic != nil {`.

## Project Context

The changed code sits primarily in `op-devstack/dsl`, `op-devstack/sysgo`, `op-supernode/supernode`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-devstack/sysgo/singlechain_interop.go`, `op-supernode/supernode/interop_config_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-devstack/dsl/deposit_eoa.go`, `op-devstack/sysgo/world.go`. The strongest project-level identifiers around this patch are `DependencySet`, `message`, `interop`, and `txintent`.

## Before/After Behavior

Before the patch, supernode startup constructed interop activity without passing a dependency-set-derived message expiry window, and the runtime could retain the original dependency set instead of an overridden one. After the patch, runtime setup preserves an overridden dependency set, supernode startup reads `MessageExpiryWindow()` from a virtual node dependency set and passes it into `interop.New(...)`, and a new `PrepareExecTx` helper lets tests inject a signed exec transaction directly for expired-message scenarios.

# Root Cause

The shown root cause is inconsistent propagation of the configured message expiry window: the supernode interop path used a default or hardcoded value instead of the dependency-set override, and runtime wiring did not always carry the overridden dependency set forward.

## Walkthrough

1. `op-devstack/sysgo/multichain_supernode_runtime.go` now rebuilds the static dependency set when `cfg.MessageExpiryWindow` is set, showing the override is intended to live in the dependency set.

2. The same runtime code now prefers `depSet` when present instead of always exposing `wb.outFullCfgSet.DependencySet`, which preserves the override in returned runtime state.

3. `op-supernode/supernode/supernode.go` now reads `MessageExpiryWindow()` from a non-nil `DependencySet` in `vnCfgs` and passes that value to `interop.New(...)`.

4. `op-devstack/dsl/eoa.go` adds `PrepareExecTx`, which signs but does not submit an exec transaction and is explicitly described as test support for bypassing mempool filtering.

5. The commit message says the old supernode path used a hardcoded `ExpiryTime` of `604800`, and that this prevented `WithMessageExpiryWindow` from affecting cross-safe validation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-supernode/supernode/supernode.go | 105 | constructs interop activity with the dependency-set message expiry window so cross-safe validation uses configured expiry semantics |
| op-devstack/sysgo/multichain_supernode_runtime.go | 130 | applies message-expiry override to the static dependency set in single-chain supernode runtime setup |
| op-devstack/sysgo/multichain_supernode_runtime.go | 238 | propagates overridden dependency sets into the runtime instead of falling back to the original builder dependency set |
| op-devstack/dsl/eoa.go | 338 | test harness helper that prepares a signed exec transaction for direct block injection, bypassing mempool filtering to exercise the expired-message path |

## Code Snippets

## Snippet 1

Context: `op-devstack/dsl/eoa.go:338` (changes signature or replay validation logic)

Before
```go
}

// SendInvalidExecMessage sends an executing message with an invalid identifier.
// The log index is incremented to reference a non-existent log.
```
After
```go
}

// PrepareExecTx builds and signs an executing-message transaction referencing
// the given init message, but does NOT submit it. Returns the raw signed
// transaction bytes and tx hash. The raw bytes are suitable for injection via
// TestSequencer.SequenceBlockWithTxs, bypassing mempool filtering.
func (u *EOA) PrepareExecTx(initMsg *InitMessage) (rawTx []byte, txHash common.Hash) {
	tx := txintent.NewIntent[*txintent.ExecTrigger, *txintent.InteropOutput](u.Plan())
```

## Snippet 2

Context: `op-devstack/sysgo/multichain_supernode_runtime.go:238` (changes a sensitive control or state-update path)

Before
```go
})

	return &MultiChainRuntime{
		Keys:          keys,
		Migration:     newInteropMigrationState(wb),
		DependencySet: wb.outFullCfgSet.DependencySet,
		L1Network:     l1Net,
		L1EL:          l1EL,
```
After
```go
})

	// Use the potentially-overridden depSet (e.g. with custom message expiry window)
	// if available; otherwise fall back to the original from the world builder.
	var runtimeDepSet depset.DependencySet
	if depSet != nil {
		runtimeDepSet = depSet
	} else {
```

## Snippet 3

Context: `op-supernode/supernode/supernode.go:105` (changes a sensitive control or state-update path)

Before
```go
// If it's nil, don't start interop. If it's non-nil (including 0), do start it.
	if interopActivationTimestamp != nil {
		interopActivity := interop.New(log.New("activity", "interop"), *interopActivationTimestamp, s.chains, cfg.DataDir, s.l1Client)
		s.activities = append(s.activities, interopActivity)
		for _, chain := range s.chains {
```
After
```go
// If it's nil, don't start interop. If it's non-nil (including 0), do start it.
	if interopActivationTimestamp != nil {
		// Extract the message expiry window from the first virtual node's dependency set.
		var msgExpiryWindow uint64
		for _, vnCfg := range vnCfgs {
			if vnCfg.DependencySet != nil {
				msgExpiryWindow = vnCfg.DependencySet.MessageExpiryWindow()
				break
```

## Snippet 4

Context: `op-devstack/sysgo/multichain_supernode_runtime.go:130` (changes a sensitive control or state-update path)

Before
```go
}

	supernode, l2CL := startSingleChainSharedSupernode(t, l1Net, l1EL, l1CL, l2Net, l2EL, depSetStatic, jwtSecret, interopAtGenesis)
	l2Batcher := startMinimalBatcher(t, keys, l2Net, l1EL, l2CL, l2EL, cfg.BatcherOptions...)
```
After
```go
}

	if cfg.MessageExpiryWindow != nil && depSetStatic != nil {
		var overrideErr error
		depSetStatic, overrideErr = depset.NewStaticConfigDependencySetWithMessageExpiryOverride(
			depSetStatic.Dependencies(), *cfg.MessageExpiryWindow)
		require.NoError(overrideErr, "failed to override message expiry window")
	}
```

# Fix Pattern

Replace a hardcoded default with dependency-set-sourced configuration, and propagate override-bearing config objects through runtime construction. Add regression support code to exercise the affected path.

## How It Was Fixed

The patch threads the message expiry window from the dependency set into supernode interop construction and preserves dependency-set overrides in runtime setup. The added transaction-preparation helper supports acceptance testing of expired-message cases but is not evidence of the underlying defect by itself.

# Why It Matters

1. It aligns supernode validation behavior with configured dependency-set values.

2. It avoids test and runtime paths observing different expiry-window settings.

3. It adds coverage for expired-message scenarios that front-door filtering would otherwise block.

4. The provided evidence does not show a demonstrated production exploit or impact beyond configuration inconsistency.

# Evidence Notes

Direct evidence shows configuration wiring changes in `op-supernode/supernode/supernode.go` and `op-devstack/sysgo/multichain_supernode_runtime.go`, plus test support added in `op-devstack/dsl/eoa.go`. The commit message explicitly says the supernode previously used a hardcoded `ExpiryTime` of `604800` and that this made `WithMessageExpiryWindow` ineffective for cross-safe validation. However, the provided snippets do not show the downstream validation logic itself, do not show a production non-default configuration, and do not prove broader on-chain acceptance or exploitability. Protocol security invariant: If a message expiry window is configured in the dependency set, supernode interop validation should use that same window rather than an unrelated hardcoded default. Verification notes: The patch does not prove that production deployments used a non-default message expiry window. The evidence shows a validation-parameter mismatch risk, not a demonstrated cryptographic break or generic replay vulnerability. The patch does not prove expired exec transactions were broadly accepted on-chain; it shows a fault-proof/cross-safe classification inconsistency scenario. Much of the diff is test and runtime scaffolding, so only the supernode expiry-parameter fix is directly security-relevant. No code for `interop.New(...)` or the expiry-checking logic is included, so the exact enforcement path is inferred from the commit message and call-site changes. The evidence supports a configuration mismatch and testability fix, not a confirmed vulnerability. `PrepareExecTx` is helper scaffolding for tests and should not be treated as the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validation-configuration-mismatch`
Final impact type: `validation-bypass-risk`
Final confidence: `medium`
Final tags: `blockchain-core, interop, message-expiry, validation`

The patch evidence supports a security-hardening interpretation, not a confirmed exploitable vulnerability. The implementation changes move message-expiry handling in supernode interop validation from a hardcoded default to dependency-set-derived configuration, and the commit message ties that directly to cross-safe validation behavior. In a blockchain fault-proof and malicious-sequencer context, that is a security-sensitive validation tightening. However, the supplied patch does not prove real-world exploitability, impacted deployments, or a concrete acceptance bypass beyond configuration mismatch and test coverage.

## Security Evidence

1. Commit message says supernode interop used a hardcoded expiry value instead of the dependency set, breaking cross-safe validation overrides.
2. Supernode construction now extracts `MessageExpiryWindow()` from `DependencySet` and passes it into `interop.New(...)`.
3. Runtime setup now preserves overridden dependency sets instead of always using the original builder dependency set.
4. Test support explicitly models a malicious sequencer injecting an expired exec transaction by bypassing mempool filtering.
5. The affected behavior is fault-proof and cross-chain message validation logic, which is security-sensitive in this project context.

## Missing Evidence

1. No downstream expiry-checking logic or `interop.New(...)` implementation is shown.
2. No evidence that production deployments used non-default expiry-window overrides.
3. No proof of concrete exploit, fund loss, chain safety failure, or broad acceptance of expired messages.
4. Much of the diff is test migration and scaffolding rather than direct fix logic.

## Claim Boundaries

1. Supported claim: the patch hardens security-sensitive validation by honoring configured message-expiry parameters.
2. Supported claim: prior behavior could misclassify expired-message scenarios when overrides were intended.
3. Not supported: a confirmed exploitable vulnerability in production.
4. Not supported: a generic replay, signature, or cryptographic flaw.
5. `PrepareExecTx` is test-enabling scaffolding and should not be treated as the vulnerability itself.
