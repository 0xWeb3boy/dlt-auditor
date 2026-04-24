---
case_id: case_20240509_b36bfe41b
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
bug_class: replay-or-signature-validation
impact_type:
  - request-forgery-or-replay
source_quality: high
date: 2024-05-09
source_refs:
  - git:b36bfe41bb7dcf935d338bebf82e412589dfeec2
  - "x/evm/ante/sig.go:40"
  - "x/evm/ante/sig.go:2"
confidence: medium
tags:
  - security-hardening
  - transaction-processing
  - evm
  - chain-id-validation
  - replay-protection
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit chain ID checks in `x/evm/ante/sig.go` within `EVMSigVerifyDecorator.AnteHandle`. It reads the configured EVM chain ID from the keeper, reads `ethTx.ChainId()`, switches on the Ethereum transaction type, and for legacy transactions allows either chain ID zero or the configured chain ID while rejecting other nonzero chain IDs with `sdkerrors.ErrInvalidChainID`. This is security-relevant hardening around the EVM transaction replay/signature domain, but the supplied evidence does not establish an exploitable vulnerability or prove that invalid-chain-ID transactions previously reached execution in production.

## Observed Patch Facts

1. In `x/evm/ante/sig.go`, the patch replaces `if ctx.IsCheckTx() {` with `chainID := svd.evmKeeper.ChainID(ctx)`.

2. In `x/evm/ante/sig.go`, the patch replaces `tmtypes "github.com/tendermint/tendermint/types"` with `ethtypes "github.com/ethereum/go-ethereum/core/types"`.

## Project Context

The changed code sits primarily in `x/evm/ante`, `x/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/ante/sig_test.go`, `x/evm/ante/preprocess_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/ante/sig_test.go`, `x/evm/keeper/msg_server_test.go`. The strongest project-level identifiers around this patch are `types`, `cosmos`, `ethTx`, and `chainID`. Nearby tests or test-like files include `x/evm/blocktest/config.go`.

## Before/After Behavior

Before the patch, the provided ante-handler snippet shows EVM context fields being set and then flow moving into `if ctx.IsCheckTx() {`, with no visible chain ID comparison at that point. After the patch, the handler obtains `chainID := svd.evmKeeper.ChainID(ctx)` and `txChainID := ethTx.ChainId()`, then performs a transaction-type switch before the shown check-tx nonce logic. For legacy transactions, the visible code rejects nonzero chain IDs that differ from the configured chain ID. The supplied diff does not show the full default branch for non-legacy transaction types.

# Root Cause

The grounded issue is missing or incomplete explicit chain ID validation in the shown `EVMSigVerifyDecorator.AnteHandle` path before later ante processing. The evidence does not prove the check was absent everywhere, does not prove production exploitability, and does not establish fund theft, unauthorized signing, or consensus compromise.

## Walkthrough

1. `EVMSigVerifyDecorator.AnteHandle` extracts the EVM transaction and sender information from the Cosmos SDK transaction.

2. The handler reads nonce information and sets EVM-related context fields, including sender address and transaction hash.

3. The before snippet then proceeds toward check-tx nonce handling without showing a chain ID validation gate in this location.

4. The after code reads the current EVM chain ID from `svd.evmKeeper.ChainID(ctx)` and the transaction chain ID from `ethTx.ChainId()`.

5. The new code switches on `ethTx.Type()` using go-ethereum transaction type constants.

6. For `ethtypes.LegacyTxType`, the new code permits chain ID zero or the configured chain ID.

7. For legacy transactions with a mismatched nonzero chain ID, the handler logs `chainID mismatch` and returns `sdkerrors.ErrInvalidChainID`.

8. The visible evidence supports a localized validation hardening in the EVM ante path, not a confirmed vulnerability narrative.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/ante/sig.go | 28 | EVM ante handler extracts transaction, sender, nonce, and now validates transaction chain ID before continuing |
| x/evm/ante/sig.go | 40 | chain ID validation switch allowing legacy zero-or-current chain ID and rejecting legacy mismatches |
| x/evm/ante/sig.go | 2 | imports Ethereum transaction type constants and big integer comparison support for chain ID validation |

## Code Snippets

## Snippet 1

Context: `x/evm/ante/sig.go:40` (changes a sensitive control or state-update path)

Before
```go
ctx = ctx.WithEVMTxHash(ethTx.Hash().Hex())

	if ctx.IsCheckTx() {
		if txNonce < nextNonce {
```
After
```go
ctx = ctx.WithEVMTxHash(ethTx.Hash().Hex())

	chainID := svd.evmKeeper.ChainID(ctx)
	txChainID := ethTx.ChainId()

	// validate chain ID on the transaction
	switch ethTx.Type() {
	case ethtypes.LegacyTxType:
```

## Snippet 2

Context: `x/evm/ante/sig.go:2` (changes a sensitive control or state-update path)

Before
```go
import (
	sdk "github.com/cosmos/cosmos-sdk/types"
	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
	abci "github.com/tendermint/tendermint/abci/types"
	tmtypes "github.com/tendermint/tendermint/types"
```
After
```go
import (
	"math/big"

	sdk "github.com/cosmos/cosmos-sdk/types"
	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
	ethtypes "github.com/ethereum/go-ethereum/core/types"
	abci "github.com/tendermint/tendermint/abci/types"
```

# Fix Pattern

Add explicit validation of a replay-domain field in the transaction admission path, while preserving legacy transaction compatibility and failing closed on mismatches.

## How It Was Fixed

The patch imports `math/big` and go-ethereum transaction type constants, reads the configured chain ID and transaction chain ID in `EVMSigVerifyDecorator.AnteHandle`, and adds a transaction-type switch. The visible legacy branch allows zero or matching chain IDs and returns `ErrInvalidChainID` when a legacy transaction carries a different nonzero chain ID.

# Why It Matters

1. Chain ID is part of the EVM transaction replay/signature domain.

2. Rejecting mismatched chain IDs earlier reduces ambiguity in transaction admission behavior.

3. The patch creates a clearer regression target for legacy EVM transaction handling.

4. The evidence is security-relevant but insufficient to confirm a vulnerability.

# Evidence Notes

Primary evidence is limited to `x/evm/ante/sig.go`. The changed lines show added chain ID reads, a switch on `ethTx.Type()`, a legacy transaction case, comparison against zero and the configured chain ID, logging of a mismatch, and return of `sdkerrors.ErrInvalidChainID`. Import changes support this implementation. Commit metadata mentions additional chain-id validation and tests, but the supplied evidence does not include the full test assertions or the complete non-legacy default branch. Claims of practical replay, asset loss, unauthorized signing, or consensus impact are unsupported. Protocol security invariant: EVM transaction admission should reject transactions whose chain ID is invalid for the current chain before deeper ante or execution processing. The supplied evidence shows this invariant being made explicit for at least legacy EVM transactions in the ante signature verification path. Verification notes: The patch does not prove that invalid-chain-ID transactions were exploitable in production. The patch does not prove fund theft, unauthorized signing, or consensus compromise. The visible diff does not fully show the default branch behavior for non-legacy transaction types. The evidence supports replay-protection validation, not a broader EVM execution bug. Confirmed by provided diff excerpts only; no repository inspection was performed. Treat helper test and script changes as support code, not root cause evidence. Downgraded from likely security-hardening kept in corpus to unclear because exploitability and prior acceptance behavior are not established by the supplied evidence. Non-legacy transaction behavior should not be asserted beyond the existence of a switch/default branch in the visible diff. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final confidence: `medium`
Final tags: `security-hardening, transaction-processing, evm, chain-id-validation, replay-protection`

The supplied patch evidence shows a focused addition of chain ID validation in the EVM ante signature verification path, rejecting legacy transactions with a mismatched nonzero chain ID. That is a clear tightening of replay-domain validation in transaction admission, but the evidence does not prove that mismatched-chain transactions were exploitable or reached execution before the patch. This supports security-hardening rather than a confirmed security-fix.

## Security Evidence

1. Adds configured chain ID lookup via evmKeeper.ChainID(ctx) in EVMSigVerifyDecorator.AnteHandle.
2. Reads ethTx.ChainId() and validates it before later ante processing.
3. Rejects legacy transactions whose nonzero chain ID differs from the configured chain ID with ErrInvalidChainID.
4. Touches EVM transaction signature/admission logic, a replay-sensitive subsystem.

## Missing Evidence

1. No proof that invalid-chain-ID transactions were accepted through execution before the patch.
2. No exploit scenario, advisory, or demonstrated cross-chain replay impact is supplied.
3. The visible evidence does not show the full default branch for non-legacy transaction types.
4. Test changes are mentioned but not shown in enough detail to prove a concrete vulnerability regression.

## Claim Boundaries

1. Classify as security hardening, not a confirmed exploitable vulnerability fix.
2. Limit the claim to explicit chain ID validation in the EVM ante path.
3. Do not claim fund loss, unauthorized signing, consensus compromise, or practical replay exploitation.
4. Do not infer non-legacy transaction behavior beyond the supplied switch/default evidence.
