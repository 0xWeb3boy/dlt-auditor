---
case_id: case_20221129_652572ecf7
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
  - git:652572ecf7627229da6ce3c76f0603cb8205149f
  - "eth/api_backend.go:393"
  - "core/types/transaction_signing_test.go:122"
  - "plugin/evm/config.go:120"
  - "eth/backend.go:239"
bug_class: replay-protection-bypass-hardening
impact_type:
  - replay-protection-hardening
confidence: medium
tags:
  - transaction-processing
  - evm
  - rpc
  - replay-protection
  - configuration-hardening
  - allowlist
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to harden EVM transaction admission around unprotected transactions by adding transaction-hash-specific exceptions while preserving the existing global allow-all setting. The evidence supports a replay-protection-related compatibility and hardening change, but not a confirmed vulnerability fix.

## Observed Patch Facts

1. In `eth/api_backend.go`, the patch replaces `func (b *EthAPIBackend) UnprotectedAllowed() bool {` with `func (b *EthAPIBackend) UnprotectedAllowed(tx *types.Transaction) bool {`.

2. In `core/types/transaction_signing_test.go`, the patch adds `if !tx.Protected() {`.

3. In `plugin/evm/config.go`, the patch replaces `LocalTxsEnabled bool 'json:"local-txs-enabled"'` with `LocalTxsEnabled bool 'json:"local-txs-enabled"'`.

4. In `eth/backend.go`, the patch replaces `extRPCEnabled: stack.Config().ExtRPCEnabled(),` with `allowUnprotectedTxHashes := make(map[common.Hash]struct{})`.

## Project Context

The changed code sits primarily in `core/types`, `plugin/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `plugin/evm/config_test.go`, `plugin/evm/vm.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `plugin/evm/vm.go`, `plugin/evm/config_test.go`. The strongest project-level identifiers around this patch are `json`, `Duration`, `config`, and `allowUnprotectedTxs`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/calltrace_test.go`.

## Before/After Behavior

Before the patch, `EthAPIBackend.UnprotectedAllowed()` returned only the backend-wide `allowUnprotectedTxs` flag. After the patch, `UnprotectedAllowed(tx *types.Transaction)` still allows all unprotected transactions when that flag is enabled, but otherwise checks whether the submitted transaction hash is present in `allowUnprotectedTxHashes`. The backend constructor now builds that hash set from configuration. A signing test also now asserts that EIP-155 test vectors are classified as protected.

# Root Cause

The prior API shape exposed only a coarse backend-wide policy for allowing unprotected transactions. The supplied evidence does not prove this caused unsafe default behavior or an exploitable bypass, but it did not support narrow compatibility exceptions keyed to specific transactions.

## Walkthrough

1. `eth/api_backend.go` changes `UnprotectedAllowed()` into `UnprotectedAllowed(tx *types.Transaction)`.

2. The patched method first preserves the existing global `allowUnprotectedTxs` behavior.

3. If the global flag is false, the patched method checks `allowUnprotectedTxHashes[tx.Hash()]`.

4. `eth/backend.go` initializes the hash set from `config.AllowUnprotectedTxHashes`.

5. The code comment says the map is read-only after creation, supporting concurrent reads.

6. `core/types/transaction_signing_test.go` adds an assertion that EIP-155 vectors are protected.

7. The supplied evidence does not show a remote attack path, default unsafe configuration, fund loss, or consensus validation bypass.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/api_backend.go | 393 | enforces whether an unprotected EVM transaction is allowed, now using the transaction hash allowlist |
| eth/backend.go | 239 | initializes the read-only set of configured unprotected transaction hashes for the API backend |
| plugin/evm/config.go | 120 | exposes/migrates EVM plugin configuration controlling unprotected transaction handling |
| core/types/transaction_signing_test.go | 122 | asserts EIP-155 test-vector transactions are treated as protected |

## Code Snippets

## Snippet 1

Context: `eth/api_backend.go:393` (changes signature or replay validation logic)

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

Context: `plugin/evm/config.go:120` (changes signature or replay validation logic)

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

Context: `eth/backend.go:239` (changes signature or replay validation logic)

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

Narrow a coarse transaction-admission exception into an explicit per-transaction allowlist while retaining the existing operator-controlled global override.

## How It Was Fixed

The backend admission check now accepts the transaction being evaluated, uses the existing allow-all flag first, and otherwise allows only configured exact transaction hashes. The constructor prepares the allowlist map at startup from configuration.

# Why It Matters

1. Reduces reliance on a broad unprotected-transaction allowance for compatibility cases.

2. Makes replay-protection exceptions more explicit and auditable.

3. Does not by itself prove that prior releases were vulnerable.

# Evidence Notes

Grounded evidence is limited to API/backend admission policy, configuration support for `AllowUnprotectedTxHashes`, and a test assertion for EIP-155 protection classification. Claims of exploitability, unsafe defaults, consensus bypass, or direct user fund impact are unsupported by the provided input. The Nick's Method Signature case is supported only by the commit subject and inferred from hash-specific handling. Protocol security invariant: Unprotected EVM transactions should not be admitted unless the node is explicitly configured to allow them, or the submitted transaction exactly matches a configured compatibility exception. The supplied evidence shows a move from a backend-wide boolean check to a transaction-specific hash allowlist, but does not establish that the previous behavior created an exploitable vulnerability. Verification notes: The patch does not prove that unprotected transactions were accepted by default. The patch does not prove remote exploitability or fund loss. The patch does not show consensus-state validation being bypassed, only API/backend admission policy changes. The named Nick's Method Signature compatibility case is inferred from the commit subject and hash allowlist behavior, not fully reconstructed from the supplied diff. Supported: transaction-specific hash allowlist was added to `UnprotectedAllowed`. Supported: global `allowUnprotectedTxs` behavior remains. Supported: backend initializes the hash allowlist from config. Unsupported: previous behavior was exploitable by remote attackers. Unsupported: consensus validation was bypassed. Unsupported: unprotected transactions were accepted by default. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `replay-protection-bypass-hardening`
Final impact type: `replay-protection-hardening`
Final confidence: `medium`
Final tags: `transaction-processing, evm, rpc, replay-protection, configuration-hardening, allowlist`

The supplied evidence supports treating this as security hardening, not a confirmed vulnerability fix. The patch changes unprotected EVM transaction admission from a coarse backend-wide boolean check toward transaction-aware handling with exact hash exceptions, in a replay-protection-sensitive path. However, the evidence does not prove unsafe defaults, remote exploitability, consensus bypass, or direct user impact, so stronger claims should be avoided.

## Security Evidence

1. `UnprotectedAllowed` now receives the transaction being evaluated instead of returning only a global boolean policy.
2. When the global unprotected-transaction flag is false, the patched path checks an exact transaction hash allowlist.
3. Backend initialization builds a read-only `allowUnprotectedTxHashes` map from configuration.
4. A transaction signing test now asserts EIP-155 test vectors are classified as protected.
5. The commit subject explicitly references migrating a replay protection bypass for specific transactions.

## Missing Evidence

1. No evidence that unprotected transactions were accepted by default.
2. No demonstrated remote attacker path or exploit scenario.
3. No proof of consensus validation bypass or state corruption.
4. No shown user fund loss or request forgery impact.
5. No complete before/after configuration showing the exact migration semantics for Nick's Method Signature transactions.

## Claim Boundaries

1. Validate only as security hardening around replay-protection-sensitive transaction admission.
2. Do not claim a confirmed exploitable vulnerability.
3. Do not claim consensus-layer transaction validation was broken.
4. Do not claim the patch fully removed unprotected transaction support, since the global allow flag remains.
5. Do not infer impact beyond narrower, auditable handling of configured unprotected transaction exceptions.
