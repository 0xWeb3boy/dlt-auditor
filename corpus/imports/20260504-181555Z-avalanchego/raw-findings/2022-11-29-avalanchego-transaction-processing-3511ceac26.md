---
case_id: case_20221129_3511ceac26
project: avalanchego
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2022-11-29
source_refs:
  - git:3511ceac260429eda0df1bdc1c9bd9584b61eb51
  - "eth/api_backend.go:388"
  - "core/types/transaction_signing_test.go:122"
  - "plugin/evm/config.go:116"
  - "eth/backend.go:238"
bug_class: transaction-replay-policy-hardening
impact_type:
  - replay-risk-reduction
confidence: medium
tags:
  - transaction-processing
  - replay-protection
  - unprotected-transactions
  - allowlist
  - rpc
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes unprotected-transaction handling from a transaction-independent global boolean check to a transaction-aware predicate that also allows configured transaction hashes. This appears to support known intentionally unprotected transactions, such as the EIP-1820 transaction referenced in the commit message, without enabling the global allowUnprotectedTxs switch. The evidence supports a compatibility-oriented narrowing mechanism, but not a confirmed vulnerability fix.

## Observed Patch Facts

1. In `eth/api_backend.go`, the patch replaces `func (b *EthAPIBackend) UnprotectedAllowed() bool {` with `func (b *EthAPIBackend) UnprotectedAllowed(tx *types.Transaction) bool {`.

2. In `core/types/transaction_signing_test.go`, the patch adds `if !tx.Protected() {`.

3. In `plugin/evm/config.go`, the patch replaces `LocalTxsEnabled bool 'json:"local-txs-enabled"'` with `LocalTxsEnabled bool 'json:"local-txs-enabled"'`.

4. In `eth/backend.go`, the patch replaces `extRPCEnabled: stack.Config().ExtRPCEnabled(),` with `allowUnprotectedTxHashes := make(map[common.Hash]struct{})`.

## Project Context

The changed code sits primarily in `core/types`, `plugin/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `plugin/evm/config_test.go`, `plugin/evm/vm.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `plugin/evm/vm.go`, `plugin/evm/config_test.go`. The strongest project-level identifiers around this patch are `json`, `Duration`, `config`, and `allowUnprotectedTxs`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/calltrace_test.go`.

## Before/After Behavior

Before the patch, EthAPIBackend.UnprotectedAllowed() returned only the global allowUnprotectedTxs setting and could not make per-transaction exceptions. After the patch, UnprotectedAllowed(tx) first honors the global setting, then checks whether tx.Hash() is present in allowUnprotectedTxHashes. eth/backend.go builds that map from config.AllowUnprotectedTxHashes during backend initialization. The signing test also adds an assertion that EIP155 test vectors are classified as protected.

# Root Cause

The prior helper represented unprotected-transaction policy as a single global boolean, so it could not allow a specific known intentionally unprotected transaction while rejecting other unprotected transactions. The evidence does not show that this caused arbitrary replay acceptance, fund loss, or remote exploitability.

## Walkthrough

1. The old backend API exposed UnprotectedAllowed() as a no-argument check over allowUnprotectedTxs.

2. The new backend API accepts the transaction being evaluated.

3. If allowUnprotectedTxs is true, the behavior remains a blanket allowance.

4. If the global allowance is false, the new code checks the transaction hash against allowUnprotectedTxHashes.

5. The backend constructor initializes allowUnprotectedTxHashes from configuration and stores it on EthAPIBackend.

6. A code comment documents that the allowlist map is read-only after creation.

7. The test update asserts that EIP155 signing vectors are protected.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/api_backend.go | 388 | Per-transaction gate deciding whether an unprotected transaction is allowed through RPC/backend handling. |
| eth/backend.go | 238 | Initializes the read-only hash allowlist from configuration and wires it into EthAPIBackend. |
| plugin/evm/config.go | 116 | Exposes EVM configuration for unprotected transaction handling and hash allowlist behavior. |
| core/types/transaction_signing_test.go | 122 | Strengthens test baseline that EIP155 signing vectors are treated as protected transactions. |

## Code Snippets

## Snippet 1

Context: `eth/api_backend.go:388` (changes signature or replay validation logic)

Before
```go
}

func (b *EthAPIBackend) UnprotectedAllowed() bool {
	return b.allowUnprotectedTxs
}
```
After
```go
}

func (b *EthAPIBackend) UnprotectedAllowed(tx *types.Transaction) bool {
	if b.allowUnprotectedTxs {
		return true
	}

	// Check for special cased transaction hashes:
```

## Snippet 2

Context: `core/types/transaction_signing_test.go:122` (changes a sensitive control or state-update path)

Before
```go
t.Errorf("%d: expected %x got %x", i, addr, from)
		}
	}
}
```
After
```go
t.Errorf("%d: expected %x got %x", i, addr, from)
		}
		if !tx.Protected() {
			t.Errorf("%d: expected to be protected", i)
		}
	}
}
```

## Snippet 3

Context: `plugin/evm/config.go:116` (changes signature or replay validation logic)

Before
```go
// API Settings
	LocalTxsEnabled         bool     `json:"local-txs-enabled"`
	APIMaxDuration          Duration `json:"api-max-duration"`
	WSCPURefillRate         Duration `json:"ws-cpu-refill-rate"`
	WSCPUMaxStored          Duration `json:"ws-cpu-max-stored"`
	MaxBlocksPerRequest     int64    `json:"api-max-blocks-per-request"`
	AllowUnfinalizedQueries bool     `json:"allow-unfinalized-queries"`
```
After
```go
// API Settings
	LocalTxsEnabled          bool          `json:"local-txs-enabled"`
	APIMaxDuration           Duration      `json:"api-max-duration"`
	WSCPURefillRate          Duration      `json:"ws-cpu-refill-rate"`
	WSCPUMaxStored           Duration      `json:"ws-cpu-max-stored"`
	MaxBlocksPerRequest      int64         `json:"api-max-blocks-per-request"`
	AllowUnfinalizedQueries  bool          `json:"allow-unfinalized-queries"`
```

## Snippet 4

Context: `eth/backend.go:238` (changes signature or replay validation logic)

Before
```go
eth.miner = miner.New(eth, &config.Miner, chainConfig, eth.EventMux(), eth.engine, clock)

	eth.APIBackend = &EthAPIBackend{
		extRPCEnabled:       stack.Config().ExtRPCEnabled(),
		allowUnprotectedTxs: config.AllowUnprotectedTxs,
		eth:                 eth,
	}
	if config.AllowUnprotectedTxs {
```
After
```go
eth.miner = miner.New(eth, &config.Miner, chainConfig, eth.EventMux(), eth.engine, clock)

	allowUnprotectedTxHashes := make(map[common.Hash]struct{})
	for _, txHash := range config.AllowUnprotectedTxHashes {
		allowUnprotectedTxHashes[txHash] = struct{}{}
	}

	eth.APIBackend = &EthAPIBackend{
```

# Fix Pattern

Add a transaction-scoped allowlist for known unprotected transaction hashes while preserving the existing global override.

## How It Was Fixed

The patch changed UnprotectedAllowed from a global-only boolean method into a transaction-aware method. It added an allowUnprotectedTxHashes map to EthAPIBackend, initialized from configuration, and checks tx.Hash() against that map when the global allowUnprotectedTxs flag is disabled.

# Why It Matters

1. Allows narrow compatibility exceptions for known intentionally unprotected transactions.

2. Avoids requiring the global unprotected-transaction switch for those specific hashes.

3. Does not prove a prior exploitable replay vulnerability from the provided evidence.

4. Does not justify keeping this as a confirmed security fix.

# Evidence Notes

Grounded evidence comes from eth/api_backend.go, where UnprotectedAllowed(tx *types.Transaction) checks allowUnprotectedTxs and allowUnprotectedTxHashes[tx.Hash()], and eth/backend.go, where the hash map is built from config.AllowUnprotectedTxHashes. The commit message references adding the EIP-1820 transaction hash to default allowed unprotected transaction hashes. The snippets do not show the full transaction submission path, default configuration values, exploitability, or any prior acceptance of attacker-controlled replayed transactions. Protocol security invariant: Transaction admission policy distinguishes replay-protected transactions from unprotected transactions; any exception for intentionally unprotected transactions should be explicit and narrow. The provided evidence shows a hash-based exception mechanism, but does not establish that the prior behavior created an exploitable vulnerability. Verification notes: The patch does not prove that arbitrary replayed transactions were previously accepted under default configuration. The patch does not prove remote exploitability or fund loss. The patch does not remove the global allowUnprotectedTxs override. The evidence supports a narrow allowlist hardening, not a general signature-validation rewrite. The provided snippets do not show the full RPC submission path or all default configuration values. Verified only against the provided snippets and commit metadata. No external code inspection was performed. Security relevance is plausible because the code handles replay-sensitive transaction admission. The vulnerability thesis is not established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-replay-policy-hardening`
Final impact type: `replay-risk-reduction`
Final confidence: `medium`
Final tags: `transaction-processing, replay-protection, unprotected-transactions, allowlist, rpc`

The evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The patch changes unprotected transaction admission from a transaction-independent global flag into a transaction-aware predicate with an explicit hash allowlist for known intentionally unprotected transactions. Because unprotected transactions are replay-sensitive and the change enables narrow exceptions instead of requiring a blanket allowance, it meaningfully tightens security-sensitive behavior. The supplied evidence does not prove prior exploitability, attacker control, fund loss, or a concrete replay vulnerability, so security-fix would be too strong.

## Security Evidence

1. UnprotectedAllowed now receives the transaction and can make per-transaction decisions.
2. The new logic preserves the global allowUnprotectedTxs override but otherwise only allows hashes present in allowUnprotectedTxHashes.
3. Backend initialization builds a read-only allowUnprotectedTxHashes map from configuration.
4. Commit metadata explicitly references adding the EIP-1820 transaction hash to the default allowed unprotected transaction hashes.
5. The touched code governs replay-sensitive unprotected transaction handling.

## Missing Evidence

1. No full transaction submission or RPC admission path is shown.
2. No evidence shows arbitrary replayed transactions were accepted under default configuration before the patch.
3. No exploit scenario, advisory, CVE, or demonstrated attacker impact is provided.
4. No evidence shows the global allowUnprotectedTxs setting was previously enabled by default or required in production.

## Claim Boundaries

1. Classify as security hardening rather than a confirmed security fix.
2. Do not claim arbitrary replay, fund loss, or remote exploitability from the supplied patch alone.
3. Do not claim the patch removes all unprotected transaction risk because the global override remains.
4. The supported claim is narrow: explicit hash allowlisting reduces reliance on a blanket unprotected-transaction allowance.
