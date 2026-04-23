---
case_id: case_20260304_6d99759f0
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2026-03-04
source_refs:
  - git:6d99759f01dc1f8697f424a6baee93621f269069
  - "core/blockchain.go:2287"
  - "eth/api_debug.go:495"
  - "core/blockchain.go:2191"
  - "core/blockchain.go:2086"
bug_class: rpc-persistent-state-side-effect
impact_type:
  - state-integrity
  - resource-exhaustion
confidence: medium
tags:
  - blockchain-core
  - rpc
  - debug-api
  - state-persistence
  - side-effect-isolation
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch separates read-only execution from persistent writes in go-ethereum's block execution path. The evidence supports that the debug ExecutionWitness RPC path could previously execute through ProcessBlock with setHead=false while still reaching writeBlockWithState, and the patch gates those writes behind an explicit WriteState option. The provided evidence does not establish exploitability, consensus impact, or a concrete security vulnerability, so this should not be kept as a confirmed security fix.

## Observed Patch Facts

1. In `core/blockchain.go`, the patch replaces `var (` with `var status WriteStatus`.

2. In `eth/api_debug.go`, the patch replaces `func (api *DebugAPI) ExecutionWitness(bn rpc.BlockNumber) (*stateless.ExtWitness, err...` with `func (api *DebugAPI) ExecutionWitness(bn rpc.BlockNumberOrHash) (*stateless.ExtWitnes...`.

3. In `core/blockchain.go`, the patch replaces `Safe: bc.CurrentSafeBlock(),` with `// Instrument the blockchain tracing`.

4. In `core/blockchain.go`, the patch replaces `// ProcessBlock executes and validates the given block. If there was no error` with `// ExecuteConfig defines optional behaviors during execution.`.

## Project Context

Historical context from `core/stateless.go`, `core/blockchain_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cmd/utils/flags.go`, `core/types.go`. The strongest project-level identifiers around this patch are `block`, `logger`, `stateless`, and `ExtWitness`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/supply_test.go`, `eth/tracers/internal/tracetest/selfdestruct_state_test.go`.

## Before/After Behavior

Before the patch, ExecutionWitness called ProcessBlock for witness generation with head updates disabled, but the shown ProcessBlock branch still called writeBlockWithState when setHead was false. After the patch, ProcessBlock uses ExecuteConfig and only calls writeBlockWithState or writeBlockAndSetHead when WriteState is true; tracing is also made explicitly configurable.

# Root Cause

ProcessBlock mixed normal import side effects with debug/RPC execution use cases. The old boolean controls distinguished head updates and witness generation, but did not clearly express a read-only mode, allowing a non-head-updating execution path to still persist block/state data.

## Walkthrough

1. DebugAPI.ExecutionWitness obtains a block and executes it to produce a stateless witness.

2. The pre-patch call used ProcessBlock with setHead=false and witness generation enabled.

3. The shown pre-patch ProcessBlock write path still called writeBlockWithState in the non-head-updating branch.

4. The patch introduces ExecuteConfig with WriteState, WriteHead, and EnableTracer controls.

5. The patched write path performs persistent block/state writes only when config.WriteState is true.

6. The BlockNumberOrHash API change is incidental and not evidence of a security fix by itself.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/blockchain.go | 2086 | defines execution configuration separating persistent writes from read-only execution/tracing behavior |
| core/blockchain.go | 2191 | gates tracing instrumentation under explicit execution config instead of always running it during ProcessBlock |
| core/blockchain.go | 2287 | persists block/state only when WriteState is true, preventing read-only execution from flushing state |
| eth/api_debug.go | 495 | debug ExecutionWitness RPC executes a block to derive an execution witness and must remain read-only |

## Code Snippets

## Snippet 1

Context: `core/blockchain.go:2287` (changes a sensitive control or state-update path)

Before
```go
// Write the block to the chain and get the status.
	var (
		wstart = time.Now()
		status WriteStatus
	)
	if !setHead {
		// Don't set the head, only insert the block
```
After
```go
// Write the block to the chain and get the status.
	var status WriteStatus
	if config.WriteState {
		wstart := time.Now()
		if !config.WriteHead {
			// Don't set the head, only insert the block
			err = bc.writeBlockWithState(block, res.Receipts, statedb)
```

## Snippet 2

Context: `eth/api_debug.go:495` (changes signature or replay validation logic)

Before
```go
}

func (api *DebugAPI) ExecutionWitness(bn rpc.BlockNumber) (*stateless.ExtWitness, error) {
	bc := api.eth.blockchain
	block, err := api.eth.APIBackend.BlockByNumber(context.Background(), bn)
	if err != nil {
		return &stateless.ExtWitness{}, fmt.Errorf("block number %v not found", bn)
	}
```
After
```go
}

func (api *DebugAPI) ExecutionWitness(bn rpc.BlockNumberOrHash) (*stateless.ExtWitness, error) {
	bc := api.eth.blockchain
	block, err := api.eth.APIBackend.BlockByNumberOrHash(context.Background(), bn)
	if err != nil {
		return &stateless.ExtWitness{}, fmt.Errorf("block %v not found", bn)
	}
```

## Snippet 3

Context: `core/blockchain.go:2191` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	if bc.logger != nil && bc.logger.OnBlockStart != nil {
		bc.logger.OnBlockStart(tracing.BlockEvent{
			Block:     block,
			Finalized: bc.CurrentFinalBlock(),
			Safe:      bc.CurrentSafeBlock(),
		})
```
After
```go
}

	// Instrument the blockchain tracing
	if config.EnableTracer {
		if bc.logger != nil && bc.logger.OnBlockStart != nil {
			bc.logger.OnBlockStart(tracing.BlockEvent{
				Block:     block,
				Finalized: bc.CurrentFinalBlock(),
```

## Snippet 4

Context: `core/blockchain.go:2086` (changes signature or replay validation logic)

Before
```go
}

// ProcessBlock executes and validates the given block. If there was no error
// it writes the block and associated state to database.
func (bc *BlockChain) ProcessBlock(ctx context.Context, parentRoot common.Hash, block *types.Block, setHead bool, makeWitness bool) (result *blockProcessingResult, blockEndErr error) {
	var (
		err       error
```
After
```go
}

// ExecuteConfig defines optional behaviors during execution.
type ExecuteConfig struct {
	// WriteState controls whether the computed state changes are persisted to
	// the underlying storage. If false, execution is performed in-memory only.
	WriteState bool
```

# Fix Pattern

Replace ambiguous boolean execution controls with explicit configuration flags and gate persistent write operations behind a dedicated WriteState option.

## How It Was Fixed

core/blockchain.go adds ExecuteConfig and changes ProcessBlock so persistent writes occur only under config.WriteState, with head updates controlled separately by WriteHead. The debug witness path can therefore execute for witness derivation without necessarily flushing state.

# Why It Matters

1. Prevents debug/RPC execution from unintentionally causing persistent storage side effects.

2. Reduces coupling between normal block import and analysis-oriented execution paths.

3. Evidence supports a side-effect isolation fix, not a proven consensus or exploit fix.

# Evidence Notes

Supported by the shown core/blockchain.go hunks adding ExecuteConfig and gating writeBlockWithState/writeBlockAndSetHead under WriteState, plus eth/api_debug.go showing ExecutionWitness as an RPC/debug execution path. The commit subject says "prevent state flushing in RPC." Unsupported claims include canonical chain corruption, consensus-rule changes, cryptographic or replay fixes, and remote exploitability. Protocol security invariant: Debug/RPC execution paths used for witness generation or inspection should not persist computed block/state data unless the caller explicitly requests normal chain-import side effects. Verification notes: The patch does not prove an attacker can corrupt canonical chain state. The patch does not prove consensus validation rules changed. The patch does not prove remote exploitability without RPC exposure and method access assumptions. The patch does not show cryptographic or replay protection logic being fixed. The BlockNumberOrHash API change alone is not security-relevant. No evidence provided that an attacker can invoke this path in a harmful deployment configuration. No evidence provided of consensus divergence, fund loss, or canonical chain corruption. Tests are mentioned in the commit file list, but no specific regression assertions are provided in the input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rpc-persistent-state-side-effect`
Final impact type: `state-integrity, resource-exhaustion`
Final confidence: `medium`
Final tags: `blockchain-core, rpc, debug-api, state-persistence, side-effect-isolation, hardening`

The patch evidence supports a security-hardening classification: an RPC/debug witness-generation path previously executed through ProcessBlock with head updates disabled but still reached persistent state/block writes, and the fix adds explicit WriteState gating so read-only execution remains in memory. The evidence does not prove exploitability, consensus divergence, canonical chain corruption, or unauthenticated remote access, so it should not be elevated to a confirmed security-fix.

## Security Evidence

1. Commit subject explicitly says it prevents state flushing in RPC.
2. ExecutionWitness is an RPC/debug API path that calls ProcessBlock to generate a stateless witness.
3. Pre-patch ProcessBlock with setHead=false still called writeBlockWithState, indicating persistent storage side effects without updating the head.
4. Post-patch ExecuteConfig adds WriteState and only performs writeBlockWithState/writeBlockAndSetHead when WriteState is true.
5. The changed code is in blockchain state execution/storage paths, which are security-sensitive in a node implementation.

## Missing Evidence

1. No evidence that the RPC method is exposed without authentication in affected deployments.
2. No proof of attacker-controlled invocation or practical exploit path.
3. No demonstrated consensus divergence, canonical head corruption, fund loss, or chain rule bypass.
4. No specific regression test assertions are provided in the supplied input.
5. No evidence that the BlockNumberOrHash change is security-relevant.

## Claim Boundaries

1. Treat as hardening against unintended persistent side effects from RPC/debug execution, not as a proven vulnerability fix.
2. Do not claim cryptographic, replay-protection, validator, or consensus-rule fixes from the supplied evidence.
3. Do not claim canonical chain corruption; the shown pre-patch path disables head updates.
4. Resource-exhaustion impact is plausible from unintended flushing but not proven as an exploit.
