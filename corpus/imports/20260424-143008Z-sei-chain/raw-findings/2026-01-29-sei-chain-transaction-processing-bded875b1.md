---
case_id: case_20260129_bded875b1
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2026-01-29
source_refs:
  - git:bded875b14ee4d1126828e864f1894dfb9f25119
  - "x/evm/state/mock_balances.go:137"
  - "giga/deps/xevm/state/mock_balances.go:135"
  - "x/evm/state/mock_balances.go:176"
  - "x/evm/state/mock_balances.go:49"
bug_class: mock-balance-mainnet-guard
impact_type:
  - misconfiguration-containment
  - state-accounting
confidence: medium
tags:
  - evm
  - mock-balances
  - mainnet-guard
  - misconfiguration-containment
  - state-accounting
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports security hardening in the mock_balances build-tag implementation. The patch adds direct pacific-1 panic guards around mock balance mutation/top-off paths and removes lazy minting from GetBalance. This is not established as an exploitable production vulnerability because the provided evidence does not show mock_balances is enabled in default production builds or that pacific-1 previously ran with it enabled.

## Observed Patch Facts

1. In `x/evm/state/mock_balances.go`, the patch replaces `// This function is used to mock balance, and is only intended for use in TESTING.` with `// PrepareMockBalance tops off the account with mock funds before fee checks`.

2. In `giga/deps/xevm/state/mock_balances.go`, the patch replaces `// This function is used to mock balance, and is only intended for use in TESTING.` with `// PrepareMockBalance tops off the account with mock funds before fee checks`.

3. In `x/evm/state/mock_balances.go`, the patch replaces `// Lazy initialization: if balance is insufficient for gas operations, mint more` with `if res == nil {`.

4. In `x/evm/state/mock_balances.go`, the patch replaces `// this avoids emitting cosmos events for ephemeral bookkeeping transfers like send_n...` with `// Always ensure account has enough - add coins directly via bank keeper`.

## Project Context

The changed code sits primarily in `x/evm/state`, `x/evm`, `giga/deps/xevm/state`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/state/balance.go`, `giga/deps/xevm/state/balance.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/state/state_test.go`, `x/evm/state/balance.go`. The strongest project-level identifiers around this patch are `mock`, `balance`, `mainnet`, and `panic`. Nearby tests or test-like files include `x/evm/integration_test.go`, `x/evm/blocktest/config.go`.

## Before/After Behavior

Before the patch, the mock_balances implementation used a testing-only mockBalance path with an indirect EVM-chain-ID mainnet check, and GetBalance could lazily mint or top off balances when balances were nil or below a threshold. After the patch, mock funding is moved to explicit PrepareMockBalance/SubBalance behavior, those paths panic directly on s.ctx.ChainID() == "pacific-1", and GetBalance becomes read-only for this purpose by returning the observed balance or zero.

# Root Cause

The risky design was that testing/simulation mock funding could be triggered from a balance read path and was guarded by an indirect mainnet check rather than direct guards on the mock balance mutation paths. The provided evidence supports this as misconfiguration containment and read-path cleanup, not a proven remote exploit path.

## Walkthrough

1. The affected implementation is scoped to x/evm/state/mock_balances.go and the mirrored giga/deps/xevm/state/mock_balances.go mock_balances build-tag files.

2. Before the change, mockBalance was documented as testing-only and checked mainnet via config.GetEVMChainID(s.ctx.ChainID()) == big.NewInt(1329).

3. Before the change, GetBalance could mint or top off balances when the balance was nil or below a 1 ETH threshold.

4. Comments in the old GetBalance path indicate snapshot cache branches could hide prior writes and cause repeated mints, which motivated tracking mocked addresses per block.

5. After the change, PrepareMockBalance is the explicit top-off path before fee checks and panics directly on pacific-1.

6. After the change, SubBalance also panics on pacific-1 before mock-balance subtraction behavior and tops off through the bank keeper only when needed.

7. After the change, GetBalance no longer performs mock minting or top-offs and only returns the observed bank balance or zero.

8. The mirrored giga/deps/xevm/state/mock_balances.go implementation receives matching PrepareMockBalance safety behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/state/mock_balances.go | 35 | SubBalance mock-balance path now panics on pacific-1 before top-off and subtraction bookkeeping |
| x/evm/state/mock_balances.go | 101 | AddBalance and PrepareMockBalance mock funding path, including explicit mainnet safety guard |
| x/evm/state/mock_balances.go | 171 | GetBalance no longer lazily mints or tops off balances during reads |
| giga/deps/xevm/state/mock_balances.go | 100 | Mirrored giga dependency mock-balance PrepareMockBalance safety behavior |

## Code Snippets

## Snippet 1

Context: `x/evm/state/mock_balances.go:137` (updates aggregate accounting or lifecycle state)

Before
```go
}

// This function is used to mock balance, and is only intended for use in TESTING.
func (s *DBImpl) mockBalance(evmAddr common.Address) *uint256.Int {
	// Prevent calling mockBalance on sei mainnet
	if config.GetEVMChainID(s.ctx.ChainID()) == big.NewInt(1329) {
		panic("Prevent mock balance from ever being called on mainnet")
	}
```
After
```go
}

// PrepareMockBalance tops off the account with mock funds before fee checks
// This is called before BuyGas to ensure the account has sufficient balance
func (s *DBImpl) PrepareMockBalance(evmAddr common.Address) {
	// SAFETY: Never allow mock balances on mainnet
	if s.ctx.ChainID() == "pacific-1" {
		panic("FATAL: mock_balances build tag enabled on pacific-1 mainnet - this is a critical misconfiguration")
```

## Snippet 2

Context: `giga/deps/xevm/state/mock_balances.go:135` (updates aggregate accounting or lifecycle state)

Before
```go
}

// This function is used to mock balance, and is only intended for use in TESTING.
func (s *DBImpl) mockBalance(evmAddr common.Address) *uint256.Int {
	// Prevent calling mockBalance on sei mainnet
	if config.GetEVMChainID(s.ctx.ChainID()) == big.NewInt(1329) {
		panic("Prevent mock balance from ever being called on mainnet")
	}
```
After
```go
}

// PrepareMockBalance tops off the account with mock funds before fee checks
// This is called before BuyGas to ensure the account has sufficient balance
func (s *DBImpl) PrepareMockBalance(evmAddr common.Address) {
	// SAFETY: Never allow mock balances on mainnet
	if s.ctx.ChainID() == "pacific-1" {
		panic("FATAL: mock_balances build tag enabled on pacific-1 mainnet - this is a critical misconfiguration")
```

## Snippet 3

Context: `x/evm/state/mock_balances.go:176` (updates aggregate accounting or lifecycle state)

Before
```go
panic("balance overflow")
	}
	// Lazy initialization: if balance is insufficient for gas operations, mint more
	minRequiredBalance := uint256.NewInt(1_000_000_000_000_000_000) // 1 ETH worth of wei for gas
	if res == nil || res.Cmp(minRequiredBalance) < 0 {
		// Check if we've already mocked this address in the current block.
		// This is needed because Snapshot() creates new cache branches that don't
		// see prior writes, causing repeated GetBalance calls to trigger repeated mints.
```
After
```go
panic("balance overflow")
	}
	if res == nil {
		return uint256.NewInt(0)
	}
	return res
```

## Snippet 4

Context: `x/evm/state/mock_balances.go:49` (updates aggregate accounting or lifecycle state)

Before
```go
ctx := s.ctx

	// this avoids emitting cosmos events for ephemeral bookkeeping transfers like send_native
	if s.eventsSuppressed {
		ctx = ctx.WithEventManager(sdk.NewEventManager())
	}
```
After
```go
ctx := s.ctx
	if s.eventsSuppressed {
		ctx = ctx.WithEventManager(sdk.NewEventManager())
	}

	// Always ensure account has enough - add coins directly via bank keeper
	// This avoids cache visibility issues by using the same ctx for both add and sub
```

# Fix Pattern

Move testing-only mock balance funding out of observational read paths into explicit preparation or mutation paths, and place direct mainnet safety guards on those paths.

## How It Was Fixed

The patch replaces the old mockBalance helper with PrepareMockBalance, adds direct s.ctx.ChainID() == "pacific-1" panic checks, removes lazy top-off logic from GetBalance, and adds same-context SubBalance top-off behavior to avoid cache visibility issues. The same pattern is mirrored in the giga dependency copy.

# Why It Matters

1. Mock balance code can add funds, so accidental mainnet execution would be high impact.

2. Direct pacific-1 guards reduce the risk from a bad mock_balances build or deployment configuration.

3. Removing minting from GetBalance prevents hidden state mutation during ordinary balance reads.

4. The evidence supports hardening, not a confirmed remote exploit.

# Evidence Notes

Grounded evidence comes from x/evm/state/mock_balances.go lines 35, 101, and 171, plus mirrored changes in giga/deps/xevm/state/mock_balances.go. Related !mock_balances balance.go files indicate this should be scoped to the mock_balances build-tag implementation. The evidence does not prove the tag is enabled in production, does not show pacific-1 was affected, and does not demonstrate an attacker-controlled exploit path. Protocol security invariant: Mock balance code capable of topping off or minting account funds for testing or simulation must not execute on pacific-1 mainnet, and ordinary balance reads should not create funds. Verification notes: No evidence shows mock_balances is enabled in the default production build. No exploit path is demonstrated from remote transaction input to unauthorized mainnet minting. No evidence proves pacific-1 previously ran with this build tag enabled. The patch also fixes simulation/cache behavior, but that alone is not a security issue. Do not classify as a confirmed vulnerability from the provided evidence. Do not claim default production builds were vulnerable. Do not claim unauthorized mainnet minting occurred. The strongest supported classification is security hardening for mock-balance misconfiguration containment. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `mock-balance-mainnet-guard`
Final impact type: `misconfiguration-containment, state-accounting`
Final confidence: `medium`
Final tags: `evm, mock-balances, mainnet-guard, misconfiguration-containment, state-accounting, security-hardening`

The supplied patch evidence clearly supports security hardening: testing-only mock balance code that can mint or top off account balances gains explicit pacific-1 mainnet panic guards, and GetBalance is changed to stop lazily minting during reads. However, the evidence does not prove that mock_balances was enabled in production, that pacific-1 was exposed, or that an attacker could exploit the behavior, so this should not be treated as a confirmed security vulnerability.

## Security Evidence

1. Mock balance mutation/top-off paths add explicit `s.ctx.ChainID() == "pacific-1"` panic checks with comments describing mainnet safety and critical misconfiguration.
2. The affected code is under `mock_balances` build-tag files and can add funds via bank keeper balance operations.
3. `GetBalance` no longer performs lazy minting or top-offs when balances are nil or below a threshold.
4. The same mainnet guard pattern is mirrored in the giga xevm mock balance implementation.

## Missing Evidence

1. No evidence shows the `mock_balances` build tag is enabled in default or production builds.
2. No evidence shows pacific-1 previously ran with this mock balance implementation enabled.
3. No attacker-controlled path from transaction input to unauthorized minting is demonstrated.
4. No evidence shows exploitation, loss, or production state corruption.

## Claim Boundaries

1. Keep as security hardening for mainnet misconfiguration containment, not as a proven exploitable vulnerability.
2. Do not claim unauthorized mainnet minting occurred.
3. Do not claim production builds were vulnerable by default.
4. Do not rely on the `replay` tag; replay-specific security impact is not supported by the supplied evidence.
