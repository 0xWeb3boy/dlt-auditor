---
case_id: case_20250218_1d5770cd93
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: not-security
phase3_validated_as: not-security
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2025-02-18
source_refs:
  - git:1d5770cd93a19797c7af2c0e9981265c3a3df847
  - "op-service/eth/types.go:291"
  - "op-service/sources/types.go:166"
  - "op-service/eth/types.go:267"
  - "op-service/eth/ssz.go:86"
bug_class: incomplete-block-hash-verification
impact_type:
  - integrity-validation-bypass
confidence: medium
tags:
  - blockchain-core
  - block-verification
  - block-hash
  - rpc
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports an Isthmus/BlockV4 correctness fix in local block verification and serialization handling, not a demonstrated security fix. The patch adds missing fork-specific header inputs to block-hash recomputation, makes implied requests-root semantics explicit, and treats L2 genesis as L2 for withdrawals validation.

## Observed Patch Facts

1. In `op-service/eth/types.go`, the patch replaces `if payload.IsthmusBlock() {` with `WithdrawalsHash: nil, // set below`.

2. In `op-service/sources/types.go`, the patch replaces `// Withdrawals validation is different between L1 and L2. It is possible to determine...` with `// Withdrawals validation is different between L1 and L2.`.

3. In `op-service/eth/types.go`, the patch replaces `func (payload *ExecutionPayload) CanyonBlock() bool {` with `// CheckBlockHash recomputes the block hash and returns if the embedded block hash ma...`.

4. In `op-service/eth/ssz.go`, the patch replaces `if version == BlockV4 {` with `// ImpliesRequestsRoot returns whether an empty requests-root should be assumed to be...`.

## Project Context

The changed code sits primarily in `op-service/eth`, `op-service/sources`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-service/sources/types_test.go`, `op-service/sources/l2_client.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-service/sources/types_test.go`, `op-service/sources/l2_client.go`. The strongest project-level identifiers around this patch are `block`, `payload`, `Withdrawals`, and `Transactions`. Nearby tests or test-like files include `op-service/sources/batching/test/generic_stub.go`, `op-service/sources/batching/test/erc20.go`.

## Before/After Behavior

Before the patch, `ExecutionPayloadEnvelope.CheckBlockHash()` rebuilt the header without some Isthmus-era fields now shown in the header literal, and `RPCBlock.Verify()` identified L2 blocks only by checking whether the first transaction was a deposit, which excluded genesis. `BlockVersion` also lacked a helper expressing that `BlockV4` implies a requests root even when not encoded. After the patch, block-hash recomputation includes the missing header attributes, withdrawals-hash handling is keyed off field presence, L2 genesis is recognized for withdrawals validation, and `ImpliesRequestsRoot()` makes the BlockV4 rule explicit.

# Root Cause

Incomplete modeling of fork-specific block fields and special-case validation rules in local verification helpers. The provided code shows version/canonicalization mismatches, not a clearly established security boundary failure.

## Walkthrough

1. `op-service/eth/types.go` recomputes a block hash from a reconstructed `types.Header` in `ExecutionPayloadEnvelope.CheckBlockHash()`.

2. The patch expands that header construction to include additional fork-specific fields such as `BlobGasUsed`, `ExcessBlobGas`, and `RequestsHash`, while still carrying `ParentBeaconRoot`.

3. The same function changes withdrawals-hash assignment to depend on `payload.WithdrawalsRoot != nil`, with fallback handling for older cases.

4. `op-service/eth/ssz.go` adds `ImpliesRequestsRoot()` for `BlockV4`, with a comment stating that an empty requests-root should be assumed even when not encoded.

5. `op-service/sources/types.go` updates `RPCBlock.Verify()` so block `0` with `SequencerFeeVaultAddr` coinbase is treated as L2, allowing genesis to use L2 withdrawals validation.

6. These changes align local verification and serialization behavior with protocol-version rules; the provided evidence does not show a new authorization check or a proven exploit path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-service/eth/types.go | 291 | Recomputes execution-payload block hash from header fields; now includes missing Isthmus-era attributes such as requests hash and blob-gas-related fields and adjusts withdrawals-hash handling. |
| op-service/sources/types.go | 166 | Verifies RPC block integrity and chooses L1 vs L2 withdrawals validation; now recognizes L2 genesis as an L2 block. |
| op-service/eth/ssz.go | 86 | Defines BlockV4 serialization semantics by treating requests root as implied even when not explicitly encoded. |

## Code Snippets

## Snippet 1

Context: `op-service/eth/types.go:291` (changes a sensitive control or state-update path)

Before
```go
Nonce:            types.BlockNonce{}, // zeroed, proof-of-work legacy
		BaseFee:          (*uint256.Int)(&payload.BaseFeePerGas).ToBig(),
		ParentBeaconRoot: envelope.ParentBeaconBlockRoot,
	}

	if payload.IsthmusBlock() {
		header.WithdrawalsHash = payload.WithdrawalsRoot
	} else if payload.CanyonBlock() {
```
After
```go
Nonce:            types.BlockNonce{}, // zeroed, proof-of-work legacy
		BaseFee:          (*uint256.Int)(&payload.BaseFeePerGas).ToBig(),
		WithdrawalsHash:  nil, // set below
		BlobGasUsed:      (*uint64)(payload.BlobGasUsed),
		ExcessBlobGas:    (*uint64)(payload.ExcessBlobGas),
		ParentBeaconRoot: envelope.ParentBeaconBlockRoot,
		RequestsHash:     envelope.RequestsHash,
	}
```

## Snippet 2

Context: `op-service/sources/types.go:166` (changes a sensitive control or state-update path)

Before
```go
}

	// Withdrawals validation is different between L1 and L2. It is possible to determine that it is an L2 block
	// if the first transaction is a deposit.
	isL2 := len(block.Transactions) > 0 && block.Transactions[0].IsDepositTx()
	if isL2 {
		if err := block.validateL2Withdrawals(block.Withdrawals, block.WithdrawalsRoot); err != nil {
```
After
```go
}

	// Withdrawals validation is different between L1 and L2.
	// It is possible to determine that it is an L2 block if the first transaction is a deposit.
	// The genesis block does not have transactions, but does have a known fee-recipient predeploy address.
	isL2 := (len(block.Transactions) > 0 && block.Transactions[0].IsDepositTx()) ||
		(block.Number == 0 && block.Coinbase == predeploys.SequencerFeeVaultAddr)
	if isL2 {
```

## Snippet 3

Context: `op-service/eth/types.go:267` (changes a sensitive control or state-update path)

Before
```go
}

func (payload *ExecutionPayload) CanyonBlock() bool {
	return payload.Withdrawals != nil
}

func (payload *ExecutionPayload) IsthmusBlock() bool {
	return payload.WithdrawalsRoot != nil
```
After
```go
}

// CheckBlockHash recomputes the block hash and returns if the embedded block hash matches.
func (envelope *ExecutionPayloadEnvelope) CheckBlockHash() (actual common.Hash, ok bool) {
```

## Snippet 4

Context: `op-service/eth/ssz.go:86` (changes a sensitive control or state-update path)

Before
```go
}

func executionPayloadFixedPart(version BlockVersion) uint32 {
	if version == BlockV4 {
```
After
```go
}

// ImpliesRequestsRoot returns whether an empty requests-root should be assumed to be there, but not encoded.
func (v BlockVersion) ImpliesRequestsRoot() bool {
	return v == BlockV4
}

func executionPayloadFixedPart(version BlockVersion) uint32 {
```

# Fix Pattern

Version-specific canonicalization repair: include all fork-defined fields in local hash/verification logic and make implied serialization rules explicit.

## How It Was Fixed

The patch updates local block-hash reconstruction to use the missing Isthmus-era header fields, adds an explicit helper for implied requests-root semantics in BlockV4, and corrects L2 genesis classification in RPC block verification so the proper withdrawals-validation path is used.

# Why It Matters

1. Prevents local verification from drifting from fork-specific protocol rules.

2. Avoids rejecting or mishandling valid Isthmus/BlockV4 data due to missing canonical fields.

3. Makes implied serialization behavior explicit instead of leaving it implicit in callers.

4. The shown impact is correctness and compatibility, not an established security bypass.

# Evidence Notes

Grounded evidence exists in three runtime areas: `op-service/eth/types.go` (`CheckBlockHash()` header reconstruction), `op-service/sources/types.go` (`RPCBlock.Verify()` L2 detection for genesis), and `op-service/eth/ssz.go` (`ImpliesRequestsRoot()`). The commit message matches those changes. The provided material does not show that malformed attacker-controlled blocks were previously accepted, does not demonstrate fund impact, and does not establish a concrete exploit. The safest reading is protocol-version correctness repair rather than a supported vulnerability finding. Protocol security invariant: Local verification must reconstruct and validate block data using the exact fork/version-specific fields and rules the protocol expects. The shown patch aligns those rules, but the provided evidence does not establish a vulnerability beyond verification/canonicalization correctness. Verification notes: The patch does not prove that malformed blocks were previously accepted; it may only fix false verification failures for valid Isthmus blocks. No concrete exploit path, fund impact, or consensus-split outcome is demonstrated by the provided diff alone. The shown `op-node` changes are test updates, not direct evidence of an exploitable runtime flaw. The evidence supports protocol-version handling bugs more strongly than a security boundary bypass. The evidence directly shows missing fields were added to local header reconstruction. The evidence directly shows genesis is newly recognized as L2 for withdrawals validation. The evidence directly shows BlockV4 gained an explicit implied-requests-root helper. No provided evidence demonstrates prior acceptance of invalid blocks or another concrete security failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incomplete-block-hash-verification`
Final impact type: `integrity-validation-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, block-verification, block-hash, rpc, security-hardening`

The patch directly strengthens integrity checking in block verification code by adding previously omitted header attributes (`BlobGasUsed`, `ExcessBlobGas`, `RequestsHash`, and withdrawals-root handling) to `CheckBlockHash()` and by making BlockV4 requests-root semantics explicit. In a blockchain client, leaving protocol-defined header fields out of hash-based verification is a security-sensitive validation gap because inconsistent block metadata can evade local integrity checks. The evidence does not prove a concrete exploit or show prior acceptance of malicious blocks in production, so this is best retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `CheckBlockHash()` reconstructs the header used for integrity verification, and the patch adds previously missing fields to that hash input.
2. The commit message explicitly calls out `fix withdrawals-root verification` and `missing check-block-hash attributes`.
3. `RequestsHash` handling is added both in header reconstruction and via `ImpliesRequestsRoot()`, tightening version-specific verification semantics.
4. `RPCBlock.Verify()` is a validation path for block data, and the patch adjusts L2/genesis handling inside that verification flow.

## Missing Evidence

1. No proof is shown that attackers could previously supply malformed blocks that passed all relevant production checks.
2. No test or narrative demonstrates acceptance of invalid blocks, only that verification logic was incomplete.
3. No concrete impact such as consensus split, fund loss, or trust-boundary bypass is established from the patch alone.
4. The evidence does not show how broadly reachable `CheckBlockHash()` is on untrusted inputs in deployed configurations.

## Claim Boundaries

1. This supports a security-hardening classification around incomplete integrity verification of block/header fields.
2. It does not justify claiming a proven exploitable vulnerability from the patch alone.
3. The genesis/L2 withdrawals change may be partly correctness-focused; the strongest security signal is the hash-verification tightening.
4. Do not label this as theft, RCE, authentication bypass, or a confirmed consensus-break without additional evidence.
