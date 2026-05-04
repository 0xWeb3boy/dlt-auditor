---
case_id: case_20241113_910a2b2392
project: avalanchego
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: medium
date: 2024-11-13
source_refs:
  - git:910a2b239271a68e780f2c89d46af64a0a53d3f2
  - "vms/platformvm/block/builder/builder.go:550"
  - "vms/platformvm/block/builder/builder.go:284"
  - "vms/platformvm/block/executor/manager.go:124"
  - "vms/platformvm/block/executor/block.go:30"
bug_class: missing-protocol-message-verification
impact_type:
  - protocol-integrity
confidence: medium
tags:
  - blockchain-core
  - platformvm
  - warp-messages
  - validator-state
  - protocol-verification
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch wires Warp message verification into PlatformVM transaction packing, manager-level transaction verification, and block verification. This is security-relevant because Warp messages depend on network identity, validator state, and P-Chain height. However, the commit subject and supplied hunks support an ACP-77 implementation or hardening change, not a confirmed vulnerability fix.

## Observed Patch Facts

1. In `vms/platformvm/block/builder/builder.go`, the patch replaces `txDiff, err := state.NewDiffOn(stateDiff)` with `err := txexecutor.VerifyWarpMessages(`.

2. In `vms/platformvm/block/builder/builder.go`, the patch replaces `return packDurangoBlockTxs(` with `recommendedPChainHeight, err := b.txExecutorBackend.Ctx.ValidatorState.GetMinimumHeig...`.

3. In `vms/platformvm/block/executor/manager.go`, the patch replaces `stateDiff, err := state.NewDiff(m.preferred, m)` with `recommendedPChainHeight, err := m.ctx.ValidatorState.GetMinimumHeight(context.TODO())`.

4. In `vms/platformvm/block/executor/block.go`, the patch replaces `func (b *Block) VerifyWithContext(_ context.Context, ctx *smblock.Context) error {` with `func (b *Block) VerifyWithContext(ctx context.Context, blockContext *smblock.Context)...`.

## Project Context

The changed code sits primarily in `vms/platformvm/block/builder`, `vms/platformvm/block`, `vms/platformvm/block/executor`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `vms/platformvm/block/executor/warp_verifier.go`, `vms/platformvm/block/executor/backend_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vms/platformvm/block/executor/warp_verifier.go`, `vms/platformvm/block/executor/verifier.go`. The strongest project-level identifiers around this patch are `pChainHeight`, `ValidatorState`, `recommendedPChainHeight`, and `VerifyWarpMessages`.

## Before/After Behavior

Before the patch, the shown PlatformVM builder and manager paths proceeded from syntactic or bootstrapped checks into later processing without an observed Warp message verification call. After the patch, those paths call VerifyWarpMessages with network ID, validator state, P-Chain height, and the unsigned transaction before continuing. Block verification now checks Warp messages using ProposerVM PChainHeight context and only reuses prior verification for the same recorded height.

# Root Cause

The grounded issue is an implementation gap: the shown PlatformVM paths did not yet include explicit Warp message verification at transaction and block verification ingress points. The evidence does not prove state corruption, consensus failure, remote exploitability, or production reachability of invalid Warp messages.

## Walkthrough

1. executeTx now calls txexecutor.VerifyWarpMessages before continuing with transaction execution work.

2. If that verification fails, the builder marks the transaction dropped in the mempool and does not pack it through that path.

3. PackAllBlockTxs now obtains a recommended P-Chain height from ValidatorState.GetMinimumHeight before packing logic proceeds.

4. manager.VerifyTx now obtains the validator-state minimum height and calls executor.VerifyWarpMessages after confirming the chain is bootstrapped.

5. Block.VerifyWithContext now uses the ProposerVM block context PChainHeight for block-level Warp verification.

6. Block verification caches successful Warp verification by P-Chain height, so it only skips verification for a height already checked.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vms/platformvm/block/builder/builder.go | 550 | Rejects or drops mempool transactions whose unsigned payload fails Warp message verification at the chosen P-Chain height. |
| vms/platformvm/block/builder/builder.go | 284 | Fetches the validator state's recommended minimum P-Chain height before packing block transactions. |
| vms/platformvm/block/executor/manager.go | 124 | Verifies Warp messages during manager-level transaction verification after bootstrapping. |
| vms/platformvm/block/executor/block.go | 30 | Runs block-level Warp message verification with ProposerVM context and caches verified P-Chain heights. |
| vms/platformvm/block/executor/warp_verifier.go | 8 | Defines block Warp message verification over network ID, validator state, P-Chain height, and block contents. |

## Code Snippets

## Snippet 1

Context: `vms/platformvm/block/builder/builder.go:550` (changes a consensus- or validator-sensitive branch)

Before
```go
// Invariant: [tx] has already been syntactically verified.

	txDiff, err := state.NewDiffOn(stateDiff)
	if err != nil {
```
After
```go
// Invariant: [tx] has already been syntactically verified.

	err := txexecutor.VerifyWarpMessages(
		ctx,
		backend.Ctx.NetworkID,
		backend.Ctx.ValidatorState,
		pChainHeight,
		tx.Unsigned,
```

## Snippet 2

Context: `vms/platformvm/block/builder/builder.go:284` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	if !b.txExecutorBackend.Config.UpgradeConfig.IsEtnaActivated(timestamp) {
		return packDurangoBlockTxs(
			preferredID,
			preferredState,
```
After
```go
}

	recommendedPChainHeight, err := b.txExecutorBackend.Ctx.ValidatorState.GetMinimumHeight(context.TODO())
	if err != nil {
		return nil, err
	}

	if !b.txExecutorBackend.Config.UpgradeConfig.IsEtnaActivated(timestamp) {
```

## Snippet 3

Context: `vms/platformvm/block/executor/manager.go:124` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	stateDiff, err := state.NewDiff(m.preferred, m)
	if err != nil {
```
After
```go
}

	recommendedPChainHeight, err := m.ctx.ValidatorState.GetMinimumHeight(context.TODO())
	if err != nil {
		return err
	}
	err = executor.VerifyWarpMessages(
		context.TODO(),
```

## Snippet 4

Context: `vms/platformvm/block/executor/block.go:30` (changes a consensus- or validator-sensitive branch)

Before
```go
}

func (b *Block) VerifyWithContext(_ context.Context, ctx *smblock.Context) error {
	pChainHeight := uint64(0)
	if ctx != nil {
		pChainHeight = ctx.PChainHeight
	}
```
After
```go
}

func (b *Block) VerifyWithContext(ctx context.Context, blockContext *smblock.Context) error {
	blkID := b.ID()
	blkState, previouslyExecuted := b.manager.blkIDToState[blkID]
	warpAlreadyVerified := previouslyExecuted && blkState.verifiedHeights.Contains(blockContext.PChainHeight)

	// If the chain is bootstrapped and the warp messages haven't been verified,
```

# Fix Pattern

Add explicit Warp message verification to PlatformVM transaction and block acceptance paths, using network ID, validator state, and P-Chain height, and fail closed when verification returns an error.

## How It Was Fixed

The patch adds VerifyWarpMessages calls in builder transaction execution, manager transaction verification, and block VerifyWithContext. It also retrieves validator-state-derived P-Chain heights for transaction checks and tracks block verification by P-Chain height.

# Why It Matters

1. Warp messages are validator-state-dependent protocol data.

2. Verification now uses network ID and P-Chain height context.

3. Invalid Warp messages are rejected by the shown builder path.

4. Block verification avoids reusing a result across unchecked P-Chain heights.

5. Exploitability is not established by the supplied evidence.

# Evidence Notes

The evidence supports that Warp message verification was added in vms/platformvm/block/builder/builder.go, vms/platformvm/block/executor/manager.go, and vms/platformvm/block/executor/block.go, with supporting verifier code in vms/platformvm/block/executor/warp_verifier.go. It does not support the stronger claims of proven state corruption, syntactic verification bypass, consensus exploitability, or a confirmed vulnerability fix. Protocol security invariant: PlatformVM transactions and blocks that carry Warp messages should be verified against the local network ID, validator state, and relevant P-Chain height before they are packed or accepted by verification paths. The provided evidence shows this invariant being implemented, but does not establish that the prior behavior was an exploitable vulnerability. Verification notes: The patch does not by itself prove remote exploitability. The evidence does not show whether invalid Warp messages could reach consensus before ACP-77 activation. The commit subject indicates implementation of ACP-77, not an explicit vulnerability fix. No state corruption mechanism is proven from the provided hunks. No bypass of syntactic transaction verification is shown. No advisory, CVE, exploit scenario, or vulnerability label is provided. The commit subject says ACP-77 implementation, not vulnerability remediation. Tests were added or updated, but the provided input does not show a failing security regression test. Security relevance is plausible, but the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-protocol-message-verification`
Final impact type: `protocol-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, platformvm, warp-messages, validator-state, protocol-verification, security-hardening`

The supplied patch evidence supports a security-hardening classification, not a confirmed vulnerability fix. The commit appears to implement ACP-77 behavior rather than remediate a disclosed bug, but it clearly adds fail-closed verification of Warp messages in PlatformVM transaction packing, manager transaction verification, and block verification paths using network ID, validator state, and P-Chain height. That is security-sensitive protocol validation, while claims of state corruption or a concrete exploit are not proven.

## Security Evidence

1. Builder executeTx now calls txexecutor.VerifyWarpMessages before continuing and drops the transaction on verification error.
2. manager.VerifyTx now retrieves validator-state minimum height and calls executor.VerifyWarpMessages before accepting the transaction.
3. Block.VerifyWithContext now verifies Warp messages when bootstrapped and avoids reusing verification across unchecked P-Chain heights.
4. Verifier context includes network ID, ValidatorState, and P-Chain height, which are security-sensitive inputs for Warp message validation.

## Missing Evidence

1. No advisory, CVE, exploit description, or vulnerability label is supplied.
2. Commit subject says ACP-77 implementation, not security remediation.
3. No evidence proves invalid Warp messages were accepted in production before this patch.
4. No supplied test demonstrates an exploitable regression or concrete consensus/state corruption outcome.

## Claim Boundaries

1. Validated only as security hardening for protocol message verification.
2. Do not claim a confirmed vulnerability fix from this evidence.
3. Do not claim state corruption, consensus compromise, or remote exploitability.
4. Original p2p-networking and database/state-corruption framing is too specific for the supplied patch evidence.
