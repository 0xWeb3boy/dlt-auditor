---
case_id: case_20240405_7d649f96d
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-04-05
source_refs:
  - git:7d649f96dea8604403915995d15c1416e46e010e
  - "go/consensus/cometbft/apps/keymanager/secrets/txs.go:232"
  - "go/consensus/cometbft/apps/keymanager/secrets/txs.go:134"
  - "go/consensus/cometbft/apps/keymanager/secrets/txs.go:22"
  - "go/consensus/cometbft/apps/keymanager/churp/txs.go:300"
bug_class: missing-gas-accounting
impact_type:
  - resource-exhaustion
  - denial-of-service
confidence: medium
tags:
  - blockchain-core
  - consensus
  - transaction-processing
  - gas-accounting
  - resource-metering
  - keymanager
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit gas charging to four key manager consensus transaction handlers and moves the simulation early-return to occur after that charge. The evidence supports a resource-accounting fix, but it does not by itself establish a concrete security vulnerability beyond previously missing handler-local gas accounting.

## Observed Patch Facts

1. In `go/consensus/cometbft/apps/keymanager/secrets/txs.go`, the patch replaces `// Ensure that the runtime exists and is a key manager.` with `// Charge gas for this operation.`.

2. In `go/consensus/cometbft/apps/keymanager/secrets/txs.go`, the patch replaces `// Ensure that the runtime exists and is a key manager.` with `// Charge gas for this operation.`.

3. In `go/consensus/cometbft/apps/keymanager/secrets/txs.go`, the patch replaces `// Ensure that the runtime exists and is a key manager.` with `// Charge gas for this operation.`.

4. In `go/consensus/cometbft/apps/keymanager/churp/txs.go`, the patch replaces `// Ensure that the runtime exists and is a key manager.` with `// Charge gas for this operation.`.

## Project Context

The changed code sits primarily in `go/consensus/cometbft/apps/keymanager/secrets`, `go/consensus/cometbft/apps/keymanager`, `go/consensus/cometbft/apps/keymanager/churp`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `go/consensus/cometbft/apps/keymanager/secrets/txs_test.go`, `go/consensus/cometbft/apps/keymanager/secrets/status_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/cometbft/apps/keymanager/keymanager.go`, `go/consensus/cometbft/apps/keymanager/secrets/txs_test.go`. The strongest project-level identifiers around this patch are `kmParams`, `secrets`, `state`, and `Charge`.

## Before/After Behavior

Before the patch, the shown handlers began with normal state or runtime validation logic and the provided snippets do not show an entry-point gas debit. After the patch, each handler first loads consensus parameters, calls `ctx.Gas().UseGas` with an operation-specific gas identifier, returns on gas error, and then returns early on `ctx.IsSimulation()` so gas estimation includes that charge.

# Root Cause

Several key manager transaction handlers appear to have omitted explicit per-operation gas charging at the start of handler execution. The fix standardizes that charging pattern and aligns simulation behavior with live gas accounting.

## Walkthrough

1. `updatePolicy`, `publishMasterSecret`, `publishEphemeralSecret`, and `confirm` were changed at the top of each handler.

2. Each modified function now fetches consensus parameters with `state.ConsensusParameters(ctx)`.

3. Each handler then calls `ctx.Gas().UseGas(1, <operation GasOp>, kmParams.GasCosts)` and returns any error.

4. Each handler now checks `ctx.IsSimulation()` only after the gas call and returns early for estimation.

5. The before snippets show these handlers previously entered validation or state-preparation logic without the newly added explicit gas-charge block.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/cometbft/apps/keymanager/secrets/txs.go | 19 | consensus tx handler for key manager policy updates |
| go/consensus/cometbft/apps/keymanager/secrets/txs.go | 131 | consensus tx handler for master secret publication |
| go/consensus/cometbft/apps/keymanager/secrets/txs.go | 229 | consensus tx handler for ephemeral secret publication |
| go/consensus/cometbft/apps/keymanager/churp/txs.go | 298 | consensus tx handler for CHURP confirmation requests |

## Code Snippets

## Snippet 1

Context: `go/consensus/cometbft/apps/keymanager/secrets/txs.go:232` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
secret *secrets.SignedEncryptedEphemeralSecret,
) error {
	// Ensure that the runtime exists and is a key manager.
	kmRt, err := common.KeyManagerRuntime(ctx, secret.Secret.ID)
```
After
```go
secret *secrets.SignedEncryptedEphemeralSecret,
) error {
	// Charge gas for this operation.
	kmParams, err := state.ConsensusParameters(ctx)
	if err != nil {
		return err
	}
	if err = ctx.Gas().UseGas(1, secrets.GasOpPublishEphemeralSecret, kmParams.GasCosts); err != nil {
```

## Snippet 2

Context: `go/consensus/cometbft/apps/keymanager/secrets/txs.go:134` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
secret *secrets.SignedEncryptedMasterSecret,
) error {
	// Ensure that the runtime exists and is a key manager.
	kmRt, err := common.KeyManagerRuntime(ctx, secret.Secret.ID)
```
After
```go
secret *secrets.SignedEncryptedMasterSecret,
) error {
	// Charge gas for this operation.
	kmParams, err := state.ConsensusParameters(ctx)
	if err != nil {
		return err
	}
	if err = ctx.Gas().UseGas(1, secrets.GasOpPublishMasterSecret, kmParams.GasCosts); err != nil {
```

## Snippet 3

Context: `go/consensus/cometbft/apps/keymanager/secrets/txs.go:22` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
sigPol *secrets.SignedPolicySGX,
) error {
	// Ensure that the runtime exists and is a key manager.
	regState := registryState.NewMutableState(ctx.State())
```
After
```go
sigPol *secrets.SignedPolicySGX,
) error {
	// Charge gas for this operation.
	kmParams, err := state.ConsensusParameters(ctx)
	if err != nil {
		return err
	}
	if err = ctx.Gas().UseGas(1, secrets.GasOpUpdatePolicy, kmParams.GasCosts); err != nil {
```

## Snippet 4

Context: `go/consensus/cometbft/apps/keymanager/churp/txs.go:300` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
state := churpState.NewMutableState(ctx.State())

	// Ensure that the runtime exists and is a key manager.
	kmRt, err := common.KeyManagerRuntime(ctx, req.Confirmation.RuntimeID)
```
After
```go
state := churpState.NewMutableState(ctx.State())

	// Charge gas for this operation.
	kmParams, err := state.ConsensusParameters(ctx)
	if err != nil {
		return err
	}
	if err = ctx.Gas().UseGas(1, churp.GasOpConfirm, kmParams.GasCosts); err != nil {
```

# Fix Pattern

Add explicit, operation-specific gas charging at handler entry and place simulation short-circuiting after that charge so estimation and execution use the same accounting point.

## How It Was Fixed

The patch inserts the same sequence into each affected handler: load consensus gas parameters, debit gas with the matching `GasOp` constant, fail on charging error, then return early for simulation. This makes the handlers consistently enforce their configured gas cost before further processing.

# Why It Matters

1. Improves consistency of gas accounting in these transaction paths.

2. Makes simulation-based fee estimation include the handler's explicit gas cost.

3. Reduces confidence that these handlers could execute work without their intended per-operation charge.

4. The evidence does not show authentication, authorization, secrecy, or integrity impact.

# Evidence Notes

The supplied diff excerpts only show newly added gas-charge logic and post-charge simulation returns in four handlers. They support a missing-gas-charge thesis for those specific functions, but they do not prove broader exploitability, chain impact, or that no other gas accounting existed elsewhere. Protocol security invariant: These consensus handlers are expected to account for operation-specific gas before deeper processing, and simulation should reflect the same accounting for fee estimation. Verification notes: The patch does not prove authentication, signature, or authorization bypass. The patch does not show secret disclosure, key compromise, or integrity failure. The patch does not prove mainnet exploitation or quantify any denial-of-service impact. The evidence shows missing charging in specific handlers, not that global gas pricing policy was wrong. The commit subject explicitly says `Fix gas charge`, which aligns with the code change. All shown changes are in consensus-path handler functions under the key manager subsystem. No provided test diff or incident evidence demonstrates an actual attack or measured denial-of-service outcome. Because the security consequence is inferred rather than established by the provided evidence, the verdict is `unclear` rather than `confirmed`. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-gas-accounting`
Final impact type: `resource-exhaustion, denial-of-service`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, transaction-processing, gas-accounting, resource-metering, keymanager`

The patch consistently adds explicit gas charging at the start of four consensus transaction handlers in the key manager subsystem and moves simulation return paths so estimation includes that charge. In a blockchain consensus path, missing handler-level gas accounting is a security-relevant weakness because it can leave expensive operations underpriced and weaken resource-exhaustion defenses. The evidence does not prove a concrete exploit or chain impact, so this is better classified as security hardening rather than a confirmed security fix.

## Security Evidence

1. Four consensus transaction handlers now call ctx.Gas().UseGas with operation-specific GasOp values.
2. The added checks occur before deeper validation or state-processing logic, tightening resource control on entry.
3. The simulation early-return was moved after gas charging, aligning fee estimation with actual execution accounting.
4. The affected code is in consensus/keymanager transaction handlers, a security-sensitive resource-management path.

## Missing Evidence

1. No proof that these handlers previously had zero effective gas charging from another layer.
2. No test, incident, or benchmark evidence showing exploitable underpricing or denial-of-service in practice.
3. No quantitative evidence about operation cost, attacker leverage, or network impact.

## Claim Boundaries

1. The patch supports a missing or incomplete gas-accounting weakness in specific handlers, not a broader consensus-integrity flaw.
2. The evidence supports security hardening for resource metering, not authentication, authorization, secrecy, or signature bypass.
3. The patch alone does not establish successful exploitation or a confirmed production denial-of-service event.
