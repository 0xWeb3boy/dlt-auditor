---
case_id: case_20260420_9b49413a
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
  - git:9b49413ab71ee42c3c9153df6d2b1ae926fbfaec
  - "runtime/runtime_test.go:146"
  - "txpool/tx_pool.go:713"
  - "runtime/runtime.go:115"
  - "consensus/validator.go:213"
bug_class: missing-chain-id-validation
impact_type:
  - replay-domain-weakening
confidence: medium
tags:
  - transaction-processing
  - consensus
  - txpool
  - runtime
  - chain-id
  - eip-1559
  - replay-protection
  - fork-gating
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds INTERSTELLAR-aware Ethereum chain ID handling in txpool validation, consensus block validation, and runtime EVM configuration. The evidence shows security-relevant replay-domain checks, but it does not establish that the previous behavior was practically exploitable or that this commit was fixing a vulnerability rather than implementing a fork/migration requirement.

## Observed Patch Facts

1. In `runtime/runtime_test.go`, the patch replaces `assert.Equal(t, ctx.chain.GenesisID(), thor.BytesToBytes32(out.Data))` with `expectedChainID := forkFromStart.GetEthChainID(ctx.chain.GenesisID())`.

2. In `txpool/tx_pool.go`, the patch adds `// Validate that EIP-1559 transactions carry the correct Ethereum chain ID.`.

3. In `runtime/runtime.go`, the patch replaces `// use genesis id as chain id` with `if thor.IsForked(ctx.Number, forkConfig.INTERSTELLAR) {`.

4. In `consensus/validator.go`, the patch adds `// Ethereum EIP-1559 transactions require the INTERSTELLAR fork.`.

## Project Context

Historical context from `txpool/tx_pool_test.go`, `consensus/pos_validator_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/pos_validator_test.go`, `consensus/consensus_test.go`. The strongest project-level identifiers around this patch are `chain`, `Ethereum`, `thor`, and `forkConfig`. Nearby tests or test-like files include `consensus/consensus_integration_test.go`.

## Before/After Behavior

Before the patch, runtime ChainID was derived from chain.GenesisID(), and the provided txpool and consensus snippets do not show EIP-1559 Ethereum chain ID validation. After the patch, runtime.New uses forkConfig.GetEthChainID(chain.GenesisID()) after INTERSTELLAR and preserves genesis-derived CHAINID before it. TxPool and consensus validation now reject TypeEthTyped1559 before INTERSTELLAR and reject post-fork EIP-1559 transactions whose EthChainID does not match the configured network Ethereum chain ID.

# Root Cause

The pre-patch code shown did not consistently apply the configured Ethereum chain ID across EIP-1559 transaction validation and runtime-visible CHAINID after the INTERSTELLAR fork. However, the provided evidence does not prove this inconsistency created an exploitable vulnerability.

## Walkthrough

1. A TypeEthTyped1559 transaction enters txpool validation.

2. The shown code bypasses legacy chain-tag validation for Ethereum typed transactions because they use chain ID for replay protection.

3. The patch rejects TypeEthTyped1559 before INTERSTELLAR.

4. After INTERSTELLAR, txpool validation compares trx.EthChainID() with p.ethChainID.

5. Consensus block validation now applies the same fork gate and chain ID comparison for TypeEthTyped1559 transactions in blocks.

6. Runtime.New now exposes the configured Ethereum chain ID through CHAINID after INTERSTELLAR and preserves the genesis-derived value before the fork.

7. Tests were updated to cover post-fork configured chain ID behavior and pre-fork historical behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/validator.go | 213 | Consensus block-body validation rejects EIP-1559 transactions before INTERSTELLAR and rejects post-fork EIP-1559 transactions whose embedded Ethereum chain ID does not match the network value. |
| txpool/tx_pool.go | 713 | Mempool basic validation rejects unsupported pre-INTERSTELLAR EIP-1559 transactions and post-fork transactions with mismatched Ethereum chain ID. |
| runtime/runtime.go | 115 | EVM chain configuration makes CHAINID return the configured Ethereum chain ID after INTERSTELLAR while preserving genesis-derived behavior before the fork. |
| runtime/runtime_test.go | 146 | Regression coverage verifies post-fork CHAINID uses GetEthChainID and pre-fork CHAINID remains genesis-derived. |

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

Add fork-gated validation and configuration alignment for Ethereum chain ID handling across mempool admission, consensus validation, and EVM runtime configuration.

## How It Was Fixed

The patch adds TypeEthTyped1559 checks in txpool/tx_pool.go and consensus/validator.go, rejecting unsupported pre-INTERSTELLAR EIP-1559 transactions and post-fork transactions with mismatched Ethereum chain IDs. It also updates runtime/runtime.go so EVM ChainID switches to forkConfig.GetEthChainID after INTERSTELLAR while retaining the old genesis-derived value before the fork.

# Why It Matters

1. EIP-1559 transactions bypass the legacy chain-tag check in the shown validation paths.

2. Chain ID is relevant to Ethereum typed transaction replay-domain separation.

3. Consensus validation is needed so the rule is enforced for blocks, not only local mempool admission.

4. Runtime CHAINID consistency matters for contracts and off-chain signature domains.

5. The evidence supports security relevance, but not a confirmed vulnerability.

# Evidence Notes

Grounded evidence comes from consensus/validator.go, txpool/tx_pool.go, runtime/runtime.go, and runtime/runtime_test.go. The comments and code support a chain-ID consistency and validation change. Unsupported claims removed: practical cross-chain replay, theft, consensus failure, and confirmed vulnerability impact are not established by the supplied evidence. The commit subject reads as fork feature work, so this should not be retained as a confirmed security fix. Protocol security invariant: After the INTERSTELLAR fork, Ethereum EIP-1559 transactions and the EVM CHAINID opcode should use the configured Ethereum chain ID; before the fork, EIP-1559 transactions should not be accepted and the prior genesis-derived CHAINID behavior should remain unchanged. Verification notes: The patch does not prove that cross-chain replay was practically exploitable on deployed networks. The patch does not prove theft, unauthorized balance movement, or consensus failure occurred. The patch does not show whether other transaction validation layers already rejected some mismatched transactions. The patch does not establish impact for non-EIP-1559 transaction types. The patch does not prove any issue before INTERSTELLAR beyond unsupported typed transaction acceptance being guarded. No evidence proves practical exploitation on a deployed network. No evidence shows whether other validation layers already rejected mismatched EIP-1559 transactions. No evidence establishes impact for non-EIP-1559 transaction types. Regression tests verify intended fork-boundary behavior, not exploitability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-chain-id-validation`
Final impact type: `replay-domain-weakening`
Final confidence: `medium`
Final tags: `transaction-processing, consensus, txpool, runtime, chain-id, eip-1559, replay-protection, fork-gating`

The supplied patch evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The changes add fork-gated rejection of Ethereum EIP-1559 transactions before INTERSTELLAR, enforce that post-fork EIP-1559 transactions carry the configured Ethereum chain ID in both txpool and consensus validation, and align the EVM CHAINID opcode with that configured value. Because chain ID is replay-domain sensitive and the pre-patch snippets show Ethereum typed transactions bypassing the legacy chain-tag check, the patch clearly tightens security-sensitive validation. However, the evidence does not prove practical exploitability, deployed exposure, or successful replay, so it should not be labeled a security-fix.

## Security Evidence

1. Consensus validation now rejects pre-INTERSTELLAR TypeEthTyped1559 transactions.
2. Consensus validation now rejects post-INTERSTELLAR TypeEthTyped1559 transactions with mismatched EthChainID.
3. Txpool validation now applies the same configured Ethereum chain ID check for TypeEthTyped1559 transactions.
4. The shown validation path bypasses legacy chain-tag checks for Ethereum typed transactions because they rely on chain ID replay protection.
5. Runtime CHAINID now returns the configured Ethereum chain ID after INTERSTELLAR, aligning on-chain and off-chain signature domains.

## Missing Evidence

1. No proof that mismatched-chain-ID transactions were accepted on a deployed network.
2. No proof of practical cross-chain replay, theft, or unauthorized transaction execution.
3. No evidence that other validation layers failed to reject the same transactions.
4. No advisory, CVE, incident report, or explicit security-fix commit message is provided.

## Claim Boundaries

1. Classify as security hardening rather than a confirmed security fix.
2. Do not claim demonstrated exploitability or real-world replay.
3. Limit impact to replay-domain weakening for Ethereum EIP-1559 transaction handling.
4. Do not extend the finding to non-EIP-1559 transaction types.
5. Treat the runtime CHAINID change as security-relevant consistency hardening, not proof of a standalone vulnerability.
