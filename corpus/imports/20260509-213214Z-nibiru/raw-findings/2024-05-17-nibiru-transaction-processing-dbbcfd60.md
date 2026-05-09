---
case_id: case_20240517_dbbcfd60
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-05-17
source_refs:
  - git:dbbcfd60f9a58446edbb5be419b315fadeb14cb3
  - "x/evm/keeper/keeper.go:90"
  - "x/evm/keeper/msg_server.go:32"
  - "x/evm/keeper/msg_ethereum_tx_test.go:119"
  - "x/evm/keeper/gas_fees.go:28"
bug_class: missing-transaction-validation
impact_type:
  - input-validation-hardening
confidence: medium
tags:
  - evm
  - transaction-processing
  - input-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an explicit msg.ValidateBasic() check at the start of Keeper.EthereumTx before context unwrap, transaction conversion, and ApplyEvmTx. This is plausibly security-relevant hardening of a sensitive EVM transaction path, but the supplied evidence does not prove an exploitable bug, consensus failure, replay issue, or remotely triggerable crash. The chain ID change and intrinsic gas hunk do not have a demonstrated security impact in the provided evidence.

## Observed Patch Facts

1. In `x/evm/keeper/keeper.go`, the patch replaces `// SetEvmChainID sets the chain id to the local variable in the keeper` with `func (k Keeper) EthChainID(ctx sdk.Context) *big.Int {`.

2. In `x/evm/keeper/msg_server.go`, the patch adds `if err := msg.ValidateBasic(); err != nil {`.

3. In `x/evm/keeper/msg_ethereum_tx_test.go`, the patch adds `s.Equal(ethTxMsg.GetGas(), gasLimit)`.

4. In `x/evm/keeper/gas_fees.go`, the patch replaces `return core.IntrinsicGas(msg.Data(), msg.AccessList(), isContractCreation, homestead,...` with `return core.IntrinsicGas(`.

## Project Context

The changed code sits primarily in `x/evm/keeper`, `x/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/keeper/grpc_query_test.go`, `x/evm/keeper/grpc_query.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/keeper/grpc_query_test.go`, `x/evm/keeper/grpc_query.go`. The strongest project-level identifiers around this patch are `resp`, `ethTxMsg`, `deps`, and `core`. Nearby tests or test-like files include `x/evm/evmtest/test_deps.go`, `x/evm/evmtest/smart_contract_test.go`.

## Before/After Behavior

Before the patch, the shown Keeper.EthereumTx body began by unwrapping the SDK context and then proceeded toward sender extraction, msg.AsTransaction(), block transaction indexing, and ApplyEvmTx without a visible local msg.ValidateBasic() guard. After the patch, Keeper.EthereumTx first calls msg.ValidateBasic() and returns a wrapped error if validation fails. The keeper.go evidence also shows removal of SetEvmChainID cached setter logic and use of EthChainID(ctx), but no concrete security consequence is demonstrated. The gas_fees.go hunk appears to be formatting only.

# Root Cause

The grounded issue is that the keeper-level EthereumTx entry point did not visibly enforce MsgEthereumTx.ValidateBasic() before later transaction handling in the provided before snippet. The evidence does not establish that this omission led to exploitable invalid state, crash, replay, or consensus divergence.

## Walkthrough

1. A MsgEthereumTx enters Keeper.EthereumTx in x/evm/keeper/msg_server.go.

2. Before the patch, the extracted handler starts with sdk.UnwrapSDKContext(goCtx) and does not show a ValidateBasic() call before later transaction handling.

3. After the patch, the handler calls msg.ValidateBasic() immediately and returns a wrapped error on failure.

4. Only after validation succeeds does the handler unwrap context, read sender data, convert the message with AsTransaction(), and call ApplyEvmTx.

5. Tests were expanded around contract creation, sufficient gas, insufficient gas, explicit ValidateBasic() checks, and expected intrinsic-gas failure behavior.

6. The keeper.go chain ID change is observable, but the supplied evidence does not prove a replay or consensus-security bug from the removed cached setter.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/keeper/msg_server.go | 32 | adds MsgEthereumTx ValidateBasic check before transaction conversion and EVM execution |
| x/evm/keeper/keeper.go | 90 | replaces cached SetEvmChainID behavior with EthChainID derived from ctx.ChainID |
| x/evm/keeper/msg_ethereum_tx_test.go | 73 | adds EVM transaction happy-path and intrinsic-gas failure coverage |
| x/evm/keeper/gas_fees.go | 28 | intrinsic gas helper touched, but shown change is formatting only |

## Code Snippets

## Snippet 1

Context: `x/evm/keeper/keeper.go:90` (changes a sensitive control or state-update path)

Before
```go
}

// SetEvmChainID sets the chain id to the local variable in the keeper
func (k *Keeper) SetEvmChainID(ctx sdk.Context) {
	newEthChainID, err := eth.ParseEthChainID(ctx.ChainID())
	if err != nil {
		panic(err)
	}
```
After
```go
}

func (k Keeper) EthChainID(ctx sdk.Context) *big.Int {
	ethChainID, err := eth.ParseEthChainID(ctx.ChainID())
```

## Snippet 2

Context: `x/evm/keeper/msg_server.go:32` (changes a sensitive control or state-update path)

Before
```go
goCtx context.Context, msg *evm.MsgEthereumTx,
) (resp *evm.MsgEthereumTxResponse, err error) {
	ctx := sdk.UnwrapSDKContext(goCtx)
```
After
```go
goCtx context.Context, msg *evm.MsgEthereumTx,
) (resp *evm.MsgEthereumTxResponse, err error) {
	if err := msg.ValidateBasic(); err != nil {
		return resp, errors.Wrap(err, "EthereumTx validate basic failed")
	}
	ctx := sdk.UnwrapSDKContext(goCtx)
```

## Snippet 3

Context: `x/evm/keeper/msg_ethereum_tx_test.go:119` (changes the branch that decides whether execution stops or continues)

Before
```go
s.NoError(err)
				s.Require().NoError(ethTxMsg.ValidateBasic())
			},
		},
```
After
```go
s.NoError(err)
				s.Require().NoError(ethTxMsg.ValidateBasic())
				s.Equal(ethTxMsg.GetGas(), gasLimit)

				resp, err := deps.Chain.EvmKeeper.EthereumTx(deps.GoCtx(), ethTxMsg)
				s.Require().ErrorContains(err, core.ErrIntrinsicGas.Error(), "resp: %s\nblock header: %s", resp, deps.Ctx.BlockHeader().ProposerAddress)
			},
		},
```

## Snippet 4

Context: `x/evm/keeper/gas_fees.go:28` (changes a sensitive control or state-update path)

Before
```go
istanbul := cfg.IsIstanbul(height)

	return core.IntrinsicGas(msg.Data(), msg.AccessList(), isContractCreation, homestead, istanbul)
}
```
After
```go
istanbul := cfg.IsIstanbul(height)

	return core.IntrinsicGas(
		msg.Data(), msg.AccessList(),
		isContractCreation, homestead, istanbul,
	)
}
```

# Fix Pattern

Add an explicit basic-validation guard at the keeper transaction entry point before conversion or execution. Treat invalid messages as ordinary returned errors.

## How It Was Fixed

Keeper.EthereumTx now calls msg.ValidateBasic() before sdk.UnwrapSDKContext(goCtx), msg.AsTransaction(), and k.ApplyEvmTx(ctx, tx). On validation failure it returns errors.Wrap(err, "EthereumTx validate basic failed"). Tests were added or expanded for EVM contract-creation transaction paths and intrinsic-gas failure behavior.

# Why It Matters

1. Keeper EVM transaction handling is a sensitive validation boundary.

2. The patch makes basic transaction validation explicit at that boundary.

3. Invalid messages now have a visible ordinary error path in this handler.

4. The evidence does not prove an actual exploit or consensus failure.

5. The gas_fees.go change is formatting-only in the supplied hunk.

# Evidence Notes

Primary evidence is the added msg.ValidateBasic() guard in x/evm/keeper/msg_server.go. Tests exercise valid contract-creation messages and an intrinsic-gas failure path. The keeper.go chain ID change is visible but not tied by the supplied evidence to a concrete security bug. No provided evidence proves malformed input previously caused node crash, state corruption, replay, or consensus failure. Protocol security invariant: EVM transaction messages handled by the keeper should satisfy MsgEthereumTx basic validation before conversion to a go-ethereum transaction and execution. The provided evidence shows this validation boundary was added, but does not establish a concrete vulnerability from its absence. Verification notes: No concrete exploit path is proven by the provided patch evidence. No evidence shows malformed EthereumTx input could previously cause consensus state corruption. No evidence shows a remotely triggerable node crash, despite the added validation guard. No evidence proves an EIP-155 replay vulnerability from the chain ID change. Intrinsic gas behavior appears tested, but the shown gas_fees.go implementation change is formatting only. No concrete exploit path is shown. No remotely triggerable crash is established. No consensus corruption or replay vulnerability is established. Intrinsic gas implementation behavior is not changed in the shown hunk. Because the vulnerability thesis is unproven, this should not be kept in the security corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-transaction-validation`
Final impact type: `input-validation-hardening`
Final confidence: `medium`
Final tags: `evm, transaction-processing, input-validation, security-hardening`

The strongest supplied evidence is the new msg.ValidateBasic() guard at the start of Keeper.EthereumTx, before transaction conversion and EVM execution. That is a clear tightening of a sensitive transaction-processing boundary, but the patch does not prove a concrete exploit, consensus failure, replay issue, or remotely triggerable crash. This should be retained only as a conservative security-hardening case, not as a proven security fix or liveness vulnerability.

## Security Evidence

1. Keeper.EthereumTx now rejects messages that fail MsgEthereumTx.ValidateBasic() before further handling.
2. The changed path is an EVM transaction entry point that proceeds to AsTransaction() and ApplyEvmTx.
3. Tests were expanded around EthereumTx execution and intrinsic gas failure behavior.

## Missing Evidence

1. No evidence shows invalid messages were remotely accepted before this patch.
2. No demonstrated exploit, consensus divergence, state corruption, replay, or crash is provided.
3. No test excerpt directly shows a previously accepted invalid MsgEthereumTx is now rejected.
4. The chain ID and intrinsic gas hunks do not independently demonstrate security impact.

## Claim Boundaries

1. Classify as validation hardening, not a confirmed vulnerability fix.
2. Do not claim liveness impact from the supplied evidence.
3. Do not claim replay protection from the chain ID refactor.
4. Do not treat the formatting-only intrinsic gas hunk as a behavior change.
