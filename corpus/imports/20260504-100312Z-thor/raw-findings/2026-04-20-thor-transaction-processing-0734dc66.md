---
case_id: case_20260420_0734dc66
project: thor
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-04-20
source_refs:
  - git:0734dc6675aceeb4c389ac965b39de175ba55d8e
  - "runtime/runtime_test.go:146"
  - "txpool/tx_pool.go:713"
  - "runtime/runtime.go:115"
  - "consensus/validator.go:213"
bug_class: chain-id-validation-hardening
impact_type:
  - replay-risk-reduction
confidence: medium
tags:
  - transaction-processing
  - consensus
  - txpool
  - chain-id
  - eip-1559
  - replay-protection
  - fork-gating
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds fork-aware Ethereum chain ID handling for INTERSTELLAR: txpool and consensus reject EthTyped1559 transactions before the fork and reject post-fork EthTyped1559 transactions with a mismatched Ethereum chain ID, while runtime CHAINID switches from the genesis-derived value to the configured Ethereum chain ID after the fork. This is security-relevant because chain ID is domain-separation material, but the provided evidence does not establish an actual vulnerability or practical replay scenario, so it should not be kept as a confirmed vulnerability fix.

## Observed Patch Facts

1. In `runtime/runtime_test.go`, the patch replaces `assert.Equal(t, ctx.chain.GenesisID(), thor.BytesToBytes32(out.Data))` with `expectedChainID := forkFromStart.GetEthChainID(ctx.chain.GenesisID())`.

2. In `txpool/tx_pool.go`, the patch adds `// Validate that EIP-1559 transactions carry the correct Ethereum chain ID.`.

3. In `runtime/runtime.go`, the patch replaces `// use genesis id as chain id` with `if thor.IsForked(ctx.Number, forkConfig.INTERSTELLAR) {`.

4. In `consensus/validator.go`, the patch adds `// Ethereum EIP-1559 transactions require the INTERSTELLAR fork.`.

## Project Context

Historical context from `txpool/tx_pool_test.go`, `consensus/pos_validator_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/pos_validator_test.go`, `consensus/consensus_test.go`. The strongest project-level identifiers around this patch are `chain`, `Ethereum`, `thor`, and `forkConfig`. Nearby tests or test-like files include `consensus/consensus_integration_test.go`.

## Before/After Behavior

Before the patch, the provided snippets show runtime.New setting the EVM ChainID from the genesis ID whenever a chain was present, and the shown txpool and consensus paths did not include INTERSTELLAR-specific EthTyped1559 rejection or Ethereum chain ID mismatch checks. After the patch, txpool and consensus reject EthTyped1559 transactions before INTERSTELLAR, validate EthChainID against the configured network value after INTERSTELLAR, and runtime.New exposes the configured Ethereum chain ID through CHAINID after the fork while preserving genesis-derived CHAINID before it.

# Root Cause

The grounded issue is incomplete INTERSTELLAR-specific chain ID handling for the newly supported Ethereum transaction path and VM chain configuration. The evidence supports a consistency and validation gap, but not a proven exploitable replay or signature-validation vulnerability.

## Walkthrough

1. EthTyped1559 transactions are exempted from the legacy chain-tag mismatch check because they are expected to carry replay protection through Ethereum chain ID.

2. The supplied before snippets do not show an equivalent Ethereum chain ID validation check in txpool or consensus.

3. The patch adds an INTERSTELLAR fork boundary so EthTyped1559 transactions are rejected before that fork in both txpool admission and consensus block validation.

4. The patch adds post-fork checks comparing trx.EthChainID() or tr.EthChainID() with the configured Ethereum chain ID.

5. runtime.New now switches CHAINID to forkConfig.GetEthChainID(chain.GenesisID()) after INTERSTELLAR instead of always using the genesis-derived value.

6. Tests assert the post-fork configured Ethereum chain ID and the preserved pre-fork genesis-derived behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/validator.go | 213 | Consensus block validation rejects unsupported pre-fork Ethereum EIP-1559 transactions and post-fork transactions with mismatched Ethereum chain ID. |
| txpool/tx_pool.go | 713 | Mempool basic validation rejects EthTyped1559 transactions with the wrong Ethereum chain ID and rejects them before INTERSTELLAR. |
| runtime/runtime.go | 115 | EVM chain configuration switches CHAINID from genesis-derived value to configured Ethereum chain ID after INTERSTELLAR. |
| runtime/runtime_test.go | 146 | Regression coverage asserts post-fork CHAINID uses configured Ethereum chain ID while pre-fork behavior remains historical. |

## Code Snippets

## Snippet 1

Context: `runtime/runtime_test.go:146` (changes a consensus- or validator-sensitive branch)

Before
```go
assert.Nil(t, out.VMErr)

				assert.Equal(t, ctx.chain.GenesisID(), thor.BytesToBytes32(out.Data))
			},
		},
```
After
```go
assert.Nil(t, out.VMErr)

				expectedChainID := forkFromStart.GetEthChainID(ctx.chain.GenesisID())
				expectedBI := new(big.Int).SetUint64(expectedChainID)
				assert.Equal(t, thor.BytesToBytes32(expectedBI.Bytes()), thor.BytesToBytes32(out.Data))

				// Pre-INTERSTELLAR: SoloFork has INTERSTELLAR = 1, so block 0 has not
				// yet crossed the fork. The CHAINID opcode must still return the old
```

## Snippet 2

Context: `txpool/tx_pool.go:713` (changes a consensus- or validator-sensitive branch)

Before
```go
return badTxError{"tx gas limit exceeds the maximum allowed"}
		}
	}
```
After
```go
return badTxError{"tx gas limit exceeds the maximum allowed"}
		}
		// Validate that EIP-1559 transactions carry the correct Ethereum chain ID.
		if trx.Type() == tx.TypeEthTyped1559 {
			if trx.EthChainID() != p.ethChainID {
				return badTxError{fmt.Sprintf("Ethereum chain ID %d does not match network chain ID %d",
					trx.EthChainID(), p.ethChainID)}
			}
```

## Snippet 3

Context: `runtime/runtime.go:115` (changes a consensus- or validator-sensitive branch)

Before
```go
currentChainConfig.OsakaBlock = big.NewInt(int64(forkConfig.INTERSTELLAR))
	if chain != nil {
		// use genesis id as chain id
		currentChainConfig.ChainID = new(big.Int).SetBytes(chain.GenesisID().Bytes())
	}
```
After
```go
currentChainConfig.OsakaBlock = big.NewInt(int64(forkConfig.INTERSTELLAR))
	if chain != nil {
		if thor.IsForked(ctx.Number, forkConfig.INTERSTELLAR) {
			// From INTERSTELLAR onward: use the configured Ethereum chain ID.
			// All tx types (VeChain-native and Ethereum) see the same CHAINID opcode
			// value, which is required for EIP-712 consistency — block.chainid inside
			// contracts must match the chain ID wallets embed in off-chain signatures.
			currentChainConfig.ChainID = new(big.Int).SetUint64(
```

## Snippet 4

Context: `consensus/validator.go:213` (changes a consensus- or validator-sensitive branch)

Before
```go
case !thor.IsForked(header.Number(), c.forkConfig.GALACTICA) && tr.Type() != tx.TypeLegacy:
			return consensusError("invalid tx: " + tx.ErrTxTypeNotSupported.Error())
		}
```
After
```go
case !thor.IsForked(header.Number(), c.forkConfig.GALACTICA) && tr.Type() != tx.TypeLegacy:
			return consensusError("invalid tx: " + tx.ErrTxTypeNotSupported.Error())
		// Ethereum EIP-1559 transactions require the INTERSTELLAR fork.
		case !thor.IsForked(header.Number(), c.forkConfig.INTERSTELLAR) && tr.Type() == tx.TypeEthTyped1559:
			return consensusError("invalid tx: " + tx.ErrTxTypeNotSupported.Error())
		// After INTERSTELLAR: validate the Ethereum chain ID embedded in the transaction.
		case thor.IsForked(header.Number(), c.forkConfig.INTERSTELLAR) && tr.Type() == tx.TypeEthTyped1559 && tr.EthChainID() != ethChainID:
			return consensusError(fmt.Sprintf("tx Ethereum chain ID %d does not match network chain ID %d",
```

# Fix Pattern

Add fork-aware validation and configuration alignment for a new Ethereum transaction domain across txpool admission, consensus validation, and VM-visible CHAINID behavior.

## How It Was Fixed

The fix adds EthTyped1559 fork gating and chain ID mismatch rejection in txpool/tx_pool.go and consensus/validator.go. It updates runtime/runtime.go to use the configured Ethereum chain ID after INTERSTELLAR and keeps the historical genesis-derived value before the fork. Regression tests document both sides of the fork boundary.

# Why It Matters

1. EthTyped1559 transactions bypass the legacy chain-tag check, so a replacement chain ID validation path is important.

2. Consensus and txpool now enforce the same INTERSTELLAR boundary for Ethereum transaction support.

3. Contract-visible CHAINID now matches the configured Ethereum chain ID after the fork.

4. The evidence supports security-relevant hardening, not a demonstrated exploit.

# Evidence Notes

Primary evidence comes from consensus/validator.go line 213, txpool/tx_pool.go line 713, runtime/runtime.go line 115, and runtime/runtime_test.go line 146. The strongest supported claim is fork-aware chain ID validation and CHAINID consistency. The evidence does not prove live cross-chain replay, funds loss, consensus split, denial of service, or EthTyped1559 signature/hash internals. Protocol security invariant: From the INTERSTELLAR fork onward, EthTyped1559 transactions should be accepted only when their embedded Ethereum chain ID matches the network-configured Ethereum chain ID, and the EVM CHAINID value should match that configured value. Before INTERSTELLAR, EthTyped1559 transactions should not be accepted and the historical genesis-derived CHAINID behavior is preserved. Verification notes: The patch does not prove that a cross-chain replay was practical on a live network. The evidence does not show signature recovery or transaction hashing internals for EthTyped1559. The change may also be part of INTERSTELLAR protocol enablement, not solely a vulnerability fix. No impact is shown for non-Ethereum transaction types beyond shared CHAINID opcode behavior. The patch does not demonstrate funds loss, consensus split, or remote denial of service by itself. No practical exploit path is shown in the supplied evidence. No security advisory or explicit vulnerability statement is provided. The change may be protocol enablement for INTERSTELLAR rather than a vulnerability fix. Classification is downgraded from likely security-hardening kept in corpus to unclear security relevance not kept in corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `chain-id-validation-hardening`
Final impact type: `replay-risk-reduction`
Final confidence: `medium`
Final tags: `transaction-processing, consensus, txpool, chain-id, eip-1559, replay-protection, fork-gating, security-hardening`

The patch clearly tightens security-sensitive transaction domain validation: EthTyped1559 transactions bypass the legacy chain-tag check, and the change adds fork gating plus explicit Ethereum chain ID checks in both txpool admission and consensus validation. The evidence supports security hardening around replay/domain separation, but not a confirmed exploitable vulnerability or demonstrated replay attack.

## Security Evidence

1. EthTyped1559 transactions are exempt from the legacy chain tag mismatch check because they rely on Ethereum chain ID for replay protection.
2. Txpool now rejects EthTyped1559 transactions with an Ethereum chain ID that does not match the configured network chain ID.
3. Consensus validation now rejects pre-INTERSTELLAR EthTyped1559 transactions and post-fork EthTyped1559 transactions with mismatched Ethereum chain ID.
4. Runtime CHAINID now returns the configured Ethereum chain ID after INTERSTELLAR, aligning contract-visible domain data with transaction signing expectations.

## Missing Evidence

1. No advisory, CVE, or explicit vulnerability statement is provided.
2. No proof is shown that mismatched-chain EthTyped1559 transactions could be accepted on a live network before the patch.
3. No transaction hashing, signature recovery, or replay exploit path is included in the supplied evidence.
4. No demonstrated impact such as funds loss, consensus split, or denial of service is shown.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed security-fix.
2. Supported claim is fork-aware Ethereum chain ID validation and CHAINID consistency.
3. Do not claim a proven practical cross-chain replay vulnerability.
4. Do not claim impact beyond EthTyped1559 handling and VM-visible CHAINID behavior shown in the patch.
