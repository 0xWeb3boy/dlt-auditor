---
case_id: case_20241024_dd27f4b6
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2024-10-24
source_refs:
  - git:dd27f4b640f228228e775e81bd771cc184a5413c
  - "x/evm/keeper/erc20.go:182"
  - "x/evm/keeper/erc20.go:211"
  - "x/evm/keeper/msg_server.go:93"
  - "x/evm/keeper/erc20.go:152"
bug_class: evm-gas-resource-control-hardening
impact_type:
  - resource-exhaustion
  - state-integrity
confidence: medium
tags:
  - evm
  - erc20
  - gas-accounting
  - resource-control
  - state-reversion
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes `CallContractWithInput` in the EVM/ERC20 helper path: it stops deriving a commit-specific gas limit, keeps the default eth-call gas limit, switches transaction config construction, and runs EVM execution through a cached context. Comments reference malicious gas-intensive contract code and avoiding state modification on revert, so the change may be security relevant. However, the provided evidence does not prove a concrete vulnerability, exploit path, consensus issue, funds loss, or specific defect in `computeCommitGasLimit`. Treat this as unclear security relevance rather than a confirmed or likely security fix.

## Observed Patch Facts

1. In `x/evm/keeper/erc20.go`, the patch replaces `gasLimit, err = computeCommitGasLimit(` with `// Gas cap sufficient for all "honest" ERC20 calls without malicious (gas`.

2. In `x/evm/keeper/erc20.go`, the patch replaces `txConfig := statedb.NewEmptyTxConfig(gethcommon.BytesToHash(ctx.HeaderHash()))` with `// Generating TxConfig with an empty tx hash as there is no actual eth tx`.

3. In `x/evm/keeper/msg_server.go`, the patch replaces `// reset the gas meter for current cosmos transaction` with `// reset the gas meter for current TxMsg (EthereumTx)`.

4. In `x/evm/keeper/erc20.go`, the patch replaces `// CallContractWithInput invokes a smart contract with the given [contractInput].` with `// CallContractWithInput invokes a smart contract with the given [contractInput]`.

## Project Context

The changed code sits primarily in `x/evm/keeper`, `x/evm`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `x/evm/keeper/statedb.go`, `x/evm/keeper/grpc_query_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/keeper/statedb.go`, `x/evm/keeper/grpc_query_test.go`. The strongest project-level identifiers around this patch are `contract`, `commit`, `txConfig`, and `fromAcc`. Nearby tests or test-like files include `x/evm/evmtest/smart_contract.go`, `x/evm/evmtest/tx.go`.

## Before/After Behavior

Before the patch, `CallContractWithInput` initialized `gasLimit` to `serverconfig.DefaultEthCallGasLimit`, then replaced it via `computeCommitGasLimit(...)` and returned on error. It built `txConfig` with `statedb.NewEmptyTxConfig(gethcommon.BytesToHash(ctx.HeaderHash()))` and applied the EVM message against the original context. After the patch, it keeps `serverconfig.DefaultEthCallGasLimit`, comments that the cap is sufficient for honest ERC20 calls without malicious gas-intensive code, builds `txConfig` through `k.TxConfig(ctx, gethcommon.BigToHash(big.NewInt(0)))`, creates `tmpCtx, commitCtx := ctx.CacheContext()`, and applies the EVM message against `tmpCtx`.

# Root Cause

The exact root cause is not established by the supplied evidence. The grounded concern is that the prior ERC20 helper execution path combined computed gas-limit selection with direct execution on the main context, while the patched path uses a fixed cap and cached context. Without the implementation of `computeCommitGasLimit`, the full error-handling diff, or tests demonstrating prior bad behavior, stronger claims about undercharging, denial of service, state corruption, or exploitable rollback failure are unsupported.

## Walkthrough

1. `CallContract` packs ABI arguments and forwards them to `CallContractWithInput`.

2. `CallContractWithInput` builds an EVM message using the caller, target contract, nonce, input data, and selected gas limit.

3. Before the patch, the helper called `computeCommitGasLimit(...)` after setting the default gas limit.

4. After the patch, the helper keeps `DefaultEthCallGasLimit` and documents it as a cap for honest ERC20 calls without malicious gas-intensive code.

5. Before the patch, the helper created an empty statedb transaction config from the block header hash.

6. After the patch, it creates transaction config through `k.TxConfig` with an empty transaction hash because no user Ethereum transaction exists.

7. After the patch, it executes the EVM message against a cached context so reverted or failed execution need not directly modify canonical state.

8. The supplied `msg_server.go` evidence is adjacent gas-accounting and event-emission context, but does not independently establish the vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/keeper/erc20.go | 168 | ERC20 helper path that builds and applies an EVM message for contract calls or deployment |
| x/evm/keeper/erc20.go | 182 | gas limit selection for ERC20 contract execution, changed from computed commit gas limit to a fixed default cap |
| x/evm/keeper/erc20.go | 211 | EVM application path using TxConfig and cached context to avoid committing state on revert or failure |
| x/evm/keeper/msg_server.go | 93 | normal EthereumTx gas accounting and event emission path, adjacent reference for gas meter reset semantics |

## Code Snippets

## Snippet 1

Context: `x/evm/keeper/erc20.go:182` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
nonce := k.GetAccNonce(ctx, fromAcc)

	gasLimit := serverconfig.DefaultEthCallGasLimit
	gasLimit, err = computeCommitGasLimit(
		commit, gasLimit, &fromAcc, contract, contractInput, k, ctx,
	)
	if err != nil {
		return nil, err
```
After
```go
nonce := k.GetAccNonce(ctx, fromAcc)

	// Gas cap sufficient for all "honest" ERC20 calls without malicious (gas
	// intensive) code in contracts
	gasLimit := serverconfig.DefaultEthCallGasLimit

	unusedBigInt := big.NewInt(0)
```

## Snippet 2

Context: `x/evm/keeper/erc20.go:211` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	txConfig := statedb.NewEmptyTxConfig(gethcommon.BytesToHash(ctx.HeaderHash()))
	evmResp, err = k.ApplyEvmMsg(
		ctx, evmMsg, evm.NewNoOpTracer(), commit, evmCfg, txConfig,
	)
	if err != nil {
		return nil, errors.Wrapf(err, "failed to apply EVM message")
```
After
```go
}

	// Generating TxConfig with an empty tx hash as there is no actual eth tx
	// sent by a user
	txConfig := k.TxConfig(ctx, gethcommon.BigToHash(big.NewInt(0)))

	// Using tmp context to not modify the state in case of evm revert
	tmpCtx, commitCtx := ctx.CacheContext()
```

## Snippet 3

Context: `x/evm/keeper/msg_server.go:93` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	// reset the gas meter for current cosmos transaction
	k.ResetGasMeterAndConsumeGas(ctx, totalGasUsed)

	err = k.EmitEthereumTxEvents(ctx, tx, msg, evmResp, contractAddr)
	if err != nil {
		return nil, errors.Wrap(err, "error emitting ethereum tx events")
```
After
```go
}

	// reset the gas meter for current TxMsg (EthereumTx)
	k.ResetGasMeterAndConsumeGas(ctx, totalGasUsed)

	err = k.EmitEthereumTxEvents(ctx, tx.To(), tx.Type(), evmMsg, evmResp)
	if err != nil {
		return nil, errors.Wrap(err, "error emitting ethereum tx events")
```

## Snippet 4

Context: `x/evm/keeper/erc20.go:152` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

// CallContractWithInput invokes a smart contract with the given [contractInput].
//
// Parameters:
//   - ctx: The SDK context for the transaction.
//   - fromAcc: The Ethereum address of the account initiating the contract call.
//   - contract: Pointer to the Ethereum address of the contract to be called.
```
After
```go
}

// CallContractWithInput invokes a smart contract with the given [contractInput]
// or deploys a new contract.
//
// Parameters:
//   - ctx: The SDK context for the transaction.
//   - fromAcc: The Ethereum address of the account initiating the contract call.
```

# Fix Pattern

Replace commit-specific gas-limit computation with a bounded default gas cap for ERC20 helper execution, use the keeper transaction config path, and run EVM execution in a cached context before committing successful state changes.

## How It Was Fixed

The patch removed the visible `computeCommitGasLimit(...)` call from `CallContractWithInput`, retained `serverconfig.DefaultEthCallGasLimit`, switched transaction config construction to `k.TxConfig` with an empty transaction hash, and introduced `ctx.CacheContext()` so EVM execution occurs against `tmpCtx`. The evidence also includes a comment about consuming the gas limit when actual gas used is unknown, but the full surrounding code is not supplied, so exact charging behavior should not be overstated.

# Why It Matters

1. Gas handling in EVM execution is security-sensitive.

2. ERC20 helper calls can execute contract code.

3. Cached execution reduces risk of persisting state after revert or error.

4. The evidence does not prove an exploitable vulnerability.

5. This should not be kept as a confirmed security fix without more proof.

# Evidence Notes

Strongest evidence is in `x/evm/keeper/erc20.go` around `CallContractWithInput`. The changed comments explicitly mention malicious gas-intensive contract code, an empty transaction hash because there is no user-sent Ethereum transaction, and cached context use to avoid state modification on EVM revert. The heuristic baseline's serialization/state-representation theory is unsupported and should be discarded. The draft's broader gas-undercharging and fail-closed claims are plausible but not fully proven by the excerpts alone. Protocol security invariant: System-driven ERC20/EVM helper calls should run under a bounded gas budget and should not commit intermediate EVM state when execution reverts or errors. The supplied evidence shows this behavior being adjusted, but does not establish that the prior behavior was exploitable. Verification notes: The patch does not prove unauthorized access, signature bypass, replay, or cryptographic failure. The patch does not prove a concrete exploit transaction or economic loss scenario. The provided evidence does not show the full implementation of computeCommitGasLimit, so its exact failure mode is inferred only from surrounding changes. The msg_server.go changes appear mostly refactor/semantic cleanup and are not independently proven security-sensitive. This is best treated as gas/resource-control hardening unless additional evidence shows an exploitable consensus or funds-impacting bug. Need the full diff around `ApplyEvmMsg` error handling to verify gas charging on failure. Need `computeCommitGasLimit` implementation or removal context to identify the actual prior defect. Need tests using the malicious ERC20 contracts to confirm the intended failing behavior. No supplied evidence proves unauthorized access, replay, cryptographic failure, consensus failure, or funds loss. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `evm-gas-resource-control-hardening`
Final impact type: `resource-exhaustion, state-integrity`
Final confidence: `medium`
Final tags: `evm, erc20, gas-accounting, resource-control, state-reversion, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a confirmed security fix. The change is in an EVM/ERC20 helper that executes contract code, removes commit-specific gas-limit computation in favor of a fixed eth-call gas cap, explicitly references malicious gas-intensive contracts, and executes through a cached context to avoid state modification on EVM revert. That is security-sensitive resource-control and state-isolation tightening, but the evidence does not prove a concrete exploitable vulnerability.

## Security Evidence

1. ERC20 helper execution path runs EVM contract code, which is security-sensitive.
2. Patch comment explicitly distinguishes honest ERC20 calls from malicious gas-intensive contract code.
3. Gas handling changes from computed commit gas limit to a fixed default cap.
4. EVM execution is moved to a cached context with a comment about avoiding state modification on revert.
5. Commit subject specifically says it fixes gas consumption within ERC20 contract execution.

## Missing Evidence

1. No full implementation or removal context for computeCommitGasLimit is provided.
2. No full error-handling diff shows exact gas charging behavior on failure.
3. No test output or test diff demonstrates the malicious ERC20 behavior being fixed.
4. No exploit path, funds impact, consensus failure, or denial-of-service scenario is proven.

## Claim Boundaries

1. Do not classify this as a confirmed security-fix from the provided evidence alone.
2. Do not retain the original serialization-or-state-representation / rpc-client-api framing; it is unsupported by the patch excerpts.
3. Supported claim is limited to EVM/ERC20 gas/resource-control and revert-state hardening.
4. No claim of unauthorized access, replay, cryptographic failure, or concrete economic loss is supported.
