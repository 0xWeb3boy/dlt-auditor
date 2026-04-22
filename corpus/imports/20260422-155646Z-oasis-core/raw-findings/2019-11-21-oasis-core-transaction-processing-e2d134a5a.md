---
case_id: case_20191121_e2d134a5a
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2019-11-21
source_refs:
  - git:e2d134a5af0474341549a9d0ac129145eafb28c7
  - "go/consensus/tendermint/apps/registry/transactions.go:407"
  - "go/consensus/tendermint/apps/registry/transactions.go:332"
  - "go/consensus/tendermint/apps/registry/transactions.go:75"
  - "go/consensus/tendermint/apps/registry/transactions.go:168"
bug_class: missing-gas-accounting
impact_type:
  - denial-of-service
  - fee-bypass
confidence: medium
tags:
  - blockchain-core
  - consensus
  - transaction-processing
  - gas-metering
  - resource-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit gas charging to several registry transaction handlers. The code supports a missing-gas-accounting interpretation, but the provided evidence does not establish a concrete vulnerability or exploitation path, so this is security-relevant at most and should remain classified as unclear.

## Observed Patch Facts

1. In `go/consensus/tendermint/apps/registry/transactions.go`, the patch replaces `// If TEE is required, check if runtime provided at least one enclave ID.` with `// Charge gas for this transaction.`.

2. In `go/consensus/tendermint/apps/registry/transactions.go`, the patch replaces `// Fetch node descriptor.` with `// Charge gas for this transaction.`.

3. In `go/consensus/tendermint/apps/registry/transactions.go`, the patch replaces `id := ctx.TxSigner()` with `// Charge gas for this transaction.`.

4. In `go/consensus/tendermint/apps/registry/transactions.go`, the patch replaces `// Re-check that the entity has at sufficient stake to still be an entity.` with `// Charge gas for node registration if signed by entity. For node-signed`.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/apps/registry`, `go/consensus/tendermint/apps`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `go/consensus/tendermint/apps/registry/registry.go`, `go/consensus/tendermint/apps/staking/transactions.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/tendermint/apps/staking/transactions.go`, `go/consensus/tendermint/apps/registry/registry.go`. The strongest project-level identifiers around this patch are `params`, `transaction`, `Charge`, and `state`.

## Before/After Behavior

Before the patch, the shown handlers proceeded from early guards or prior validation into their normal logic without the newly added handler-level gas-charging block at those exact points. After the patch, deregisterEntity, unfreezeNode, and registerRuntime fetch consensus parameters and call ctx.Gas().UseGas(...) before continuing, while registerNode adds a conditional gas charge for the entity-signed case and leaves the node-signed case documented as prepaid.

# Root Cause

Some registry transaction handlers did not perform the now-shown explicit per-operation gas charge before continuing with stateful processing. The evidence supports inconsistent or absent handler-level metering, not a signature or replay-validation defect.

## Walkthrough

1. deregisterEntity now charges gas immediately after the check-only return path and before reading the transaction signer.

2. unfreezeNode now charges gas before fetching the node descriptor and continuing with the unfreeze flow.

3. registerRuntime now charges gas after runtime argument verification and before later runtime-specific checks.

4. registerNode already loads consensus parameters, and the patch adds a conditional UseGas call for the entity-signed registration path.

5. The new registerNode comment states that node-signed registrations are prepaid by the entity, so the change explicitly encodes that payer distinction rather than showing a new signature-validation rule.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/apps/registry/transactions.go | 72 | registry transaction handler now charging gas before `deregisterEntity` state changes |
| go/consensus/tendermint/apps/registry/transactions.go | 123 | registry transaction handler charging gas for entity-signed `registerNode`, with node-signed path treated as prepaid |
| go/consensus/tendermint/apps/registry/transactions.go | 325 | registry transaction handler now charging gas before `unfreezeNode` processing |
| go/consensus/tendermint/apps/registry/transactions.go | 395 | registry transaction handler now charging gas before `registerRuntime` processing |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/apps/registry/transactions.go:407` (changes signature or replay validation logic)

Before
```go
}

	// If TEE is required, check if runtime provided at least one enclave ID.
	if rt.TEEHardware != node.TEEHardwareInvalid {
```
After
```go
}

	// Charge gas for this transaction.
	params, err := state.ConsensusParameters()
	if err != nil {
		app.logger.Error("RegisterRuntime: failed to fetch consensus parameters",
			"err", err,
		)
```

## Snippet 2

Context: `go/consensus/tendermint/apps/registry/transactions.go:332` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	// Fetch node descriptor.
	node, err := state.Node(unfreeze.NodeID)
```
After
```go
}

	// Charge gas for this transaction.
	params, err := state.ConsensusParameters()
	if err != nil {
		app.logger.Error("UnfreezeNode: failed to fetch consensus parameters",
			"err", err,
		)
```

## Snippet 3

Context: `go/consensus/tendermint/apps/registry/transactions.go:75` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	id := ctx.TxSigner()
```
After
```go
}

	// Charge gas for this transaction.
	params, err := state.ConsensusParameters()
	if err != nil {
		app.logger.Error("DeregisterEntity: failed to fetch consensus parameters",
			"err", err,
		)
```

## Snippet 4

Context: `go/consensus/tendermint/apps/registry/transactions.go:168` (changes signature or replay validation logic)

Before
```go
}

	// Re-check that the entity has at sufficient stake to still be an entity.
	var (
```
After
```go
}

	// Charge gas for node registration if signed by entity. For node-signed
	// registrations, the gas charges are pre-paid by the entity.
	if sigNode.Signature.PublicKey.Equal(untrustedNode.EntityID) {
		if err = ctx.Gas().UseGas(1, registry.GasOpRegisterNode, params.GasCosts); err != nil {
			return err
		}
```

# Fix Pattern

Add explicit handler-level gas metering by loading consensus gas parameters and invoking ctx.Gas().UseGas(...) before further state-mutating processing; where fee payment depends on signing mode, make that charging condition explicit in code.

## How It Was Fixed

The fix inserts gas-accounting code into the affected registry handlers. Each added block fetches consensus parameters, returns on error, and invokes ctx.Gas().UseGas with the relevant registry gas operation. In registerNode, the charge is applied only when the registration is entity-signed, matching the comment that node-signed registrations are prepaid.

# Why It Matters

1. It prevents the shown registry write paths from skipping the explicit gas charge added by this patch.

2. It makes transaction-cost accounting more consistent across these handlers.

3. It clarifies who is charged for node registration in the two signing modes.

# Evidence Notes

The strongest direct evidence is the added ConsensusParameters() retrieval and ctx.Gas().UseGas(...) calls in go/consensus/tendermint/apps/registry/transactions.go for deregisterEntity, unfreezeNode, registerRuntime, and registerNode. The draft's stronger replay/signature thesis is not supported by the shown diff. The commit subject and hunks support a gas-metering change; they do not, by themselves, prove an exploitable security flaw. Protocol security invariant: Registry transactions that mutate on-chain state should apply the configured gas charges before continuing, and the node-registration charging path should remain consistent with the stated fee-payer model for entity-signed versus prepaid node-signed registrations. Verification notes: The patch does not prove consensus corruption, signature forgery, or replay acceptance. The diff does not show that unpaid registry calls were exploited in production. The evidence is limited to listed registry handlers and does not establish whether every other transaction path was already correctly metered. The node-signed registration path is explicitly described as prepaid; this patch does not show that prepaid logic was previously bypassable. The provided excerpts directly show new gas-charging blocks in four registry handlers. The provided excerpts do not show an exploit, incident, or concrete impact beyond previously missing metering at these call sites. No test excerpt was provided, so effectiveness beyond the visible code change cannot be independently confirmed from the input alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-gas-accounting`
Final impact type: `denial-of-service, fee-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, transaction-processing, gas-metering, resource-accounting`

The patch consistently adds explicit gas charging to registry transaction handlers that mutate consensus state, and it clarifies the payer model for one registration path. In a blockchain consensus path, missing gas metering is a security-sensitive weakness because it can permit underpriced or free state-changing operations and weaken anti-abuse controls. The evidence does not prove a concrete exploit or incident, so this is better classified as security hardening rather than a confirmed security bug fix, but it is strong enough to retain in a security-focused corpus.

## Security Evidence

1. Multiple registry handlers now call `ctx.Gas().UseGas(...)` before continuing with stateful transaction processing.
2. The affected methods are consensus-facing registry operations such as entity deregistration, node unfreeze, runtime registration, and node registration.
3. The commit message explicitly says `Charge gas for registry method calls`, aligning with missing metering rather than product cleanup.
4. `registerNode` adds a specific charge rule for entity-signed registrations and documents the prepaid exception for node-signed registrations, showing intentional tightening of fee enforcement.

## Missing Evidence

1. No proof that these handlers previously allowed exploitable spam, state-bloat, or consensus-level DoS in practice.
2. No advisory, bug report, or commit message text explicitly frames the issue as a security vulnerability.
3. No test excerpts are provided showing abuse prevention or regression coverage for an attack scenario.
4. The patch does not quantify whether the missing gas was materially bypassing fees or only correcting accounting consistency.

## Claim Boundaries

1. The evidence supports missing or inconsistent gas metering, not replay or signature-validation flaws.
2. The patch shows security-relevant hardening of resource accounting on consensus transactions.
3. It is not proven from the diff alone that the issue was exploitable or previously abused.
4. The strongest justified claim is that the commit closes under-metered registry write paths in a security-sensitive subsystem.
