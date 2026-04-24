---
case_id: case_20250818_d35634422
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-08-18
source_refs:
  - git:d35634422ac8c7c18fb2cb3a72e8e67b21f27379
  - "x/evm/ante/preprocess.go:171"
  - "x/evm/ante/preprocess.go:60"
  - "app/app.go:1710"
  - "aclmapping/evm/mappings.go:39"
bug_class: unsafe-legacy-transaction-acceptance
impact_type:
  - replay-risk
confidence: medium
tags:
  - evm
  - transaction-processing
  - transaction-admission
  - legacy-transaction
  - replay-protection
  - signature-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes EVM transaction preprocessing so unprotected legacy Ethereum transactions are rejected during normal operation. Previously, when `ethTx.Protected()` was false, `Preprocess` still computed the transaction hash with `ethtypes.FrontierSigner{}.Hash(ethTx)` and continued to sender derivation. After the patch, that fallback is allowed only when `isBlockTest` is enabled; otherwise preprocessing returns `unsupported tx type: unsafe legacy tx`.

## Observed Patch Facts

1. In `x/evm/ante/preprocess.go`, the patch replaces `evmAddr, seiAddr, seiPubkey, err := helpers.GetAddresses(V, R, S, txHash)` with `if isBlockTest {`.

2. In `x/evm/ante/preprocess.go`, the patch replaces `if err := Preprocess(ctx, msg, p.evmKeeper.ChainID(ctx)); err != nil {` with `if err := Preprocess(ctx, msg, p.evmKeeper.ChainID(ctx), p.evmKeeper.EthBlockTestConf...`.

3. In `app/app.go`, the patch replaces `if err := evmante.Preprocess(ctx, msg, app.EvmKeeper.ChainID(ctx)); err != nil {` with `if err := evmante.Preprocess(ctx, msg, app.EvmKeeper.ChainID(ctx), app.EvmKeeper.EthB...`.

4. In `aclmapping/evm/mappings.go`, the patch replaces `if err := ante.Preprocess(ctx, evmMsg, evmKeeper.ChainID(ctx)); err != nil {` with `if err := ante.Preprocess(ctx, evmMsg, evmKeeper.ChainID(ctx), evmKeeper.EthBlockTest...`.

## Project Context

The changed code sits primarily in `x/evm/ante`, `x/evm`, `aclmapping/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/ante/preprocess_test.go`, `x/evm/ante/sig_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/ante/sig_test.go`, `x/evm/keeper/msg_server_test.go`. The strongest project-level identifiers around this patch are `Preprocess`, `evmKeeper`, `ChainID`, and `txHash`. Nearby tests or test-like files include `x/evm/integration_test.go`, `x/evm/blocktest/config.go`.

## Before/After Behavior

Before: unprotected legacy transactions could proceed through preprocessing via the Frontier signer hash path. After: that path is blocked in normal mode and preserved only for explicit block-test mode, with updated callers passing `EthBlockTestConfig.Enabled` into preprocessing.

# Root Cause

`Preprocess` treated the unprotected legacy transaction case as acceptable by default, using Frontier signer hashing and continuing into address derivation. The fix makes that behavior test-only and rejects it in normal transaction handling.

## Walkthrough

1. An EVM transaction enters `Preprocess` and is converted into an Ethereum transaction object.

2. The function selects chain configuration and signer state, then checks the transaction type.

3. For protected transactions, the existing signer hash path remains unchanged.

4. Before the patch, unprotected legacy transactions used `ethtypes.FrontierSigner{}.Hash(ethTx)` and continued to `helpers.GetAddresses`.

5. After the patch, the unprotected branch checks `isBlockTest`.

6. When `isBlockTest` is true, the old Frontier signer path remains for block-test coverage.

7. When `isBlockTest` is false, preprocessing returns `unsupported tx type: unsafe legacy tx` before sender derivation.

8. The ante handler, concurrent decode path, and ACL dependency generator now pass `EthBlockTestConfig.Enabled` into `Preprocess`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/ante/preprocess.go | 171 | Rejects unprotected legacy EVM transactions during preprocessing unless block-test mode is enabled. |
| x/evm/ante/preprocess.go | 60 | Ante handler invokes preprocessing with chain ID and block-test configuration before continuing transaction handling. |
| app/app.go | 1710 | Concurrent transaction decode path applies the same preprocessing rejection before retaining an EVM transaction. |
| aclmapping/evm/mappings.go | 39 | ACL dependency generation preprocesses EVM transactions with the same legacy-transaction policy before deriving access operations. |

## Code Snippets

## Snippet 1

Context: `x/evm/ante/preprocess.go:171` (changes signature or replay validation logic)

Before
```go
txHash = signer.Hash(ethTx)
	} else {
		txHash = ethtypes.FrontierSigner{}.Hash(ethTx)
	}
	evmAddr, seiAddr, seiPubkey, err := helpers.GetAddresses(V, R, S, txHash)
```
After
```go
txHash = signer.Hash(ethTx)
	} else {
		if isBlockTest {
			// need to allow unprotected legacy txs in blocktest
			// to not lose coverage for other parts of the code
			txHash = ethtypes.FrontierSigner{}.Hash(ethTx)
		} else {
			return errors.New("unsupported tx type: unsafe legacy tx")
```

## Snippet 2

Context: `x/evm/ante/preprocess.go:60` (changes a sensitive control or state-update path)

Before
```go
func (p *EVMPreprocessDecorator) AnteHandle(ctx sdk.Context, tx sdk.Tx, simulate bool, next sdk.AnteHandler) (sdk.Context, error) {
	msg := evmtypes.MustGetEVMTransactionMessage(tx)
	if err := Preprocess(ctx, msg, p.evmKeeper.ChainID(ctx)); err != nil {
		return ctx, err
	}
```
After
```go
func (p *EVMPreprocessDecorator) AnteHandle(ctx sdk.Context, tx sdk.Tx, simulate bool, next sdk.AnteHandler) (sdk.Context, error) {
	msg := evmtypes.MustGetEVMTransactionMessage(tx)
	if err := Preprocess(ctx, msg, p.evmKeeper.ChainID(ctx), p.evmKeeper.EthBlockTestConfig.Enabled); err != nil {
		return ctx, err
	}
```

## Snippet 3

Context: `app/app.go:1710` (changes a sensitive control or state-update path)

Before
```go
if isEVM, _ := evmante.IsEVMMessage(typedTx); isEVM {
					msg := evmtypes.MustGetEVMTransactionMessage(typedTx)
					if err := evmante.Preprocess(ctx, msg, app.EvmKeeper.ChainID(ctx)); err != nil {
						ctx.Logger().Error(fmt.Sprintf("error preprocessing EVM tx due to %s", err))
						typedTxs[idx] = nil
```
After
```go
if isEVM, _ := evmante.IsEVMMessage(typedTx); isEVM {
					msg := evmtypes.MustGetEVMTransactionMessage(typedTx)
					if err := evmante.Preprocess(ctx, msg, app.EvmKeeper.ChainID(ctx), app.EvmKeeper.EthBlockTestConfig.Enabled); err != nil {
						ctx.Logger().Error(fmt.Sprintf("error preprocessing EVM tx due to %s", err))
						typedTxs[idx] = nil
```

## Snippet 4

Context: `aclmapping/evm/mappings.go:39` (changes a sensitive control or state-update path)

Before
```go
}

	if err := ante.Preprocess(ctx, evmMsg, evmKeeper.ChainID(ctx)); err != nil {
		return []sdkacltypes.AccessOperation{}, err
	}
```
After
```go
}

	if err := ante.Preprocess(ctx, evmMsg, evmKeeper.ChainID(ctx), evmKeeper.EthBlockTestConfig.Enabled); err != nil {
		return []sdkacltypes.AccessOperation{}, err
	}
```

# Fix Pattern

Reject unsafe legacy transaction formats at preprocessing/admission time, while keeping any compatibility exception behind an explicit test-mode flag.

## How It Was Fixed

`Preprocess` was extended with an `isBlockTest bool` parameter. The unprotected legacy branch now returns an error in normal mode and only uses `FrontierSigner` hashing when block-test mode is enabled. Callers in the ante decorator, concurrent transaction decoding, and ACL dependency generation were updated to pass the block-test configuration flag.

# Why It Matters

1. Normal transaction admission no longer accepts the unsafe legacy fallback path.

2. Rejection happens before sender derivation and later transaction handling in the shown paths.

3. The block-test compatibility behavior is separated from normal operation.

4. The evidence supports a security fix, but not a demonstrated exploit or complete ingress-path proof.

# Evidence Notes

Strong evidence comes from `x/evm/ante/preprocess.go`, where the unprotected legacy branch changes from unconditional Frontier signer hashing to rejection outside block-test mode. Supporting evidence shows relevant callers passing `EthBlockTestConfig.Enabled`. The evidence does not prove an exploited replay incident, does not show nonce or fee validation changes, and does not prove every possible ingress path is covered. Protocol security invariant: Normal EVM transaction preprocessing should not admit unprotected legacy transactions through the Frontier signer fallback; transaction admission should require the protected or typed signing path unless explicitly running Ethereum block-test compatibility mode. Verification notes: The patch shows rejection of unprotected legacy transactions, but does not prove a demonstrated cross-chain replay exploit occurred. The block-test exception is explicit and should not be treated as production acceptance unless that configuration can be enabled in production. The evidence does not show changes to nonce handling, fee validation, or signature verification beyond the legacy transaction hash/replay-protection boundary. The patch does not prove that all transaction ingress paths outside the shown preprocessing callers are covered. Code evidence directly shows rejection of `ethTx.Protected() == false` transactions outside block-test mode. The error string explicitly labels the rejected case as `unsafe legacy tx`. The block-test exception is supported by the changed code and comment. Security verdict is `likely` rather than `confirmed` because the provided evidence establishes unsafe acceptance and a fix, but not exploitability details or full production configuration guarantees. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unsafe-legacy-transaction-acceptance`
Final impact type: `replay-risk`
Final confidence: `medium`
Final tags: `evm, transaction-processing, transaction-admission, legacy-transaction, replay-protection, signature-validation`

The supplied patch evidence supports retaining this as security hardening: normal EVM preprocessing previously accepted unprotected legacy transactions by hashing them with FrontierSigner, and the patch now rejects that path outside explicit block-test mode with an error labeling it an unsafe legacy transaction. The evidence is strong enough for replay-protection hardening, but not strong enough to claim a demonstrated exploitable replay bug or complete production ingress coverage, so the original security-fix/high-confidence framing should be softened.

## Security Evidence

1. Preprocess now rejects ethTx.Protected() == false unless isBlockTest is enabled.
2. The old normal path used ethtypes.FrontierSigner{}.Hash(ethTx) for unprotected legacy transactions and continued sender derivation.
3. The rejection happens in EVM transaction preprocessing, a transaction admission and signature-derived identity path.
4. Callers in ante handling, concurrent decode, and ACL dependency generation now pass the block-test flag into Preprocess.
5. The new error string explicitly describes the rejected case as unsafe legacy tx.

## Missing Evidence

1. No evidence of an exploited incident or concrete replay attack is provided.
2. No proof is provided that every possible transaction ingress path is covered by these callers.
3. No evidence shows whether EthBlockTestConfig.Enabled can or cannot be enabled in production.
4. No tests are shown that directly assert production rejection of pre-155 transactions.

## Claim Boundaries

1. This validates rejection of unsafe unprotected legacy EVM transactions in shown preprocessing paths.
2. This should be treated as replay-protection hardening, not a proven request-forgery or replay exploit.
3. Do not infer changes to nonce validation, fee checks, or broader signature verification beyond the shown legacy transaction branch.
4. The block-test exception should be described as test compatibility unless production configuration evidence is supplied.
