---
case_id: case_20170512_a5f6a1cb7
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2017-05-12
source_refs:
  - git:a5f6a1cb7c5e5dde130391e9bed7625ef9ff36b5
  - "params/config.go:238"
  - "params/config.go:268"
  - "core/types/transaction_signing.go:109"
  - "params/config.go:177"
bug_class: chain-config-validation
impact_type:
  - consensus-integrity-risk
confidence: medium
tags:
  - consensus
  - chain-config
  - fork-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a correctness fix in chain-configuration compatibility checking: `params/config.go` adds a previously missing `MetropolisBlock` incompatibility check and an `IsMetropolis` helper. That is consensus-relevant code, but the supplied material does not establish a concrete vulnerability, exploit path, or real security impact, so this should be treated as unclear rather than a confirmed security fix.

## Observed Patch Facts

1. In `params/config.go`, the patch adds `if isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head) {`.

2. In `params/config.go`, the patch replaces `func (c *ChainConfig) IsMetropolis(num *big.Int) bool {` with `// ConfigCompatError is raised if the locally-stored blockchain is initialised with a`.

3. In `core/types/transaction_signing.go`, the patch replaces `/*` with `// EIP155Transaction implements TransactionInterface using the`.

4. In `params/config.go`, the patch adds `func (c *ChainConfig) IsMetropolis(num *big.Int) bool {`.

## Project Context

The changed code sits primarily in `core/types`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/types/transaction.go`, `core/types/transaction_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/types/transaction.go`, `core/types/receipt.go`. The strongest project-level identifiers around this patch are `MetropolisBlock`, `newcfg`, `ChainConfig`, and `returns`.

## Before/After Behavior

Before the patch, the shown `checkCompatible` logic rejected incompatible historical settings for earlier forks and the EIP158 chain ID case, then returned `nil` without any visible `MetropolisBlock` check. After the patch, it also rejects incompatible `MetropolisBlock` values relative to `head`, and adds `IsMetropolis(num)` as a fork-state helper.

# Root Cause

`ChainConfig.checkCompatible` enforced historical compatibility for several fork parameters but omitted `MetropolisBlock`, leaving that fork point out of the existing compatibility gate.

## Walkthrough

1. `params/config.go` shows `checkCompatible` as the place where stored and new chain configs are compared against the current head.

2. The pre-change excerpt includes compatibility checks for Homestead, DAO, EIP150, EIP155, EIP158, and the EIP158 chain ID condition, then returns `nil`.

3. The post-change excerpt adds `if isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head) { return newCompatError("Metropolis fork block", c.MetropolisBlock, newcfg.MetropolisBlock) }`.

4. A nearby comment says `ConfigCompatError` is raised when a chain config would alter the past, which grounds the purpose of this check.

5. Another hunk adds `IsMetropolis(num)` returning `isForked(c.MetropolisBlock, num)`, but this only supports the fork-state model; it does not by itself prove a vulnerability.

6. The `core/types/transaction_signing.go` hunk only shows commented EIP86 signer stub removal/isolation in the supplied evidence and should not be used to strengthen the security claim.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| params/config.go | 218 | Chain configuration compatibility gate; newly rejects retroactive `MetropolisBlock` changes against the existing chain head |
| params/config.go | 175 | Metropolis fork activation predicate used to determine whether Metropolis rules are active at a given block |
| core/types/transaction_signing.go | 109 | Ancillary signer-code cleanup/commented stub removal; not the basis for the security classification |

## Code Snippets

## Snippet 1

Context: `params/config.go:238` (changes a consensus- or validator-sensitive branch)

Before
```go
return newCompatError("EIP158 chain ID", c.EIP158Block, newcfg.EIP158Block)
	}
	return nil
}
```
After
```go
return newCompatError("EIP158 chain ID", c.EIP158Block, newcfg.EIP158Block)
	}
	if isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head) {
		return newCompatError("Metropolis fork block", c.MetropolisBlock, newcfg.MetropolisBlock)
	}
	return nil
}
```

## Snippet 2

Context: `params/config.go:268` (changes a sensitive control or state-update path)

Before
```go
}

func (c *ChainConfig) IsMetropolis(num *big.Int) bool {
	if c.MetropolisBlock == nil || num == nil {
		return false
	}
	return num.Cmp(c.MetropolisBlock) >= 0
}
```
After
```go
}

// ConfigCompatError is raised if the locally-stored blockchain is initialised with a
// ChainConfig that would alter the past.
```

## Snippet 3

Context: `core/types/transaction_signing.go:109` (changes signature or replay validation logic)

Before
```go
}

/*
// WithSignature returns a new transaction with the given signature. This signature
// needs to be in the [R || S || V] format where V is 0 or 1.
func (s EIP86Signer) WithSignature(tx *Transaction, sig []byte) (*Transaction, error) {
}
```
After
```go
}

// EIP155Transaction implements TransactionInterface using the
// EIP155 rules
```

## Snippet 4

Context: `params/config.go:177` (changes a sensitive control or state-update path)

Before
```go
}

// GasTable returns the gas table corresponding to the current phase (homestead or homestead reprice).
//
```
After
```go
}

func (c *ChainConfig) IsMetropolis(num *big.Int) bool {
	return isForked(c.MetropolisBlock, num)
}

// GasTable returns the gas table corresponding to the current phase (homestead or homestead reprice).
//
```

# Fix Pattern

Add the missing fork-parameter validation to the central chain-config compatibility gate.

## How It Was Fixed

The patch extends `ChainConfig.checkCompatible` with the same incompatibility-check pattern already used for earlier forks, now applied to `MetropolisBlock`, and adds a small `IsMetropolis` helper that delegates to shared fork-state logic.

# Why It Matters

1. It prevents one specific fork parameter from bypassing historical config-compatibility checks.

2. It reduces the chance of reinterpreting already-processed history under a changed fork schedule.

3. The evidence supports a consensus/config correctness issue, not a demonstrated attacker-triggerable exploit.

# Evidence Notes

The strongest evidence is confined to `params/config.go`. It directly shows a missing-then-added `MetropolisBlock` check in `checkCompatible`, plus an added `IsMetropolis` helper. The nearby `ConfigCompatError` comment supports the interpretation that this code prevents past-altering config changes. The supplied `core/types/transaction_signing.go` hunk does not substantiate a cryptographic, replay, or transaction-processing vulnerability. No provided evidence shows remote reachability, adversarial trigger conditions, exploitation, or an observed consensus split. Protocol security invariant: A node's stored chain configuration should not be changed in a way that retroactively moves fork activation points for blocks at or below the current head. Verification notes: The patch does not prove a remotely exploitable vulnerability. The evidence does not show an actual consensus split occurring in the field. The provided hunks support hardening of fork-config validation, not a broad transaction-signing vulnerability. Other touched files are not evidenced enough here to justify a stronger security claim. Verified from the provided diff that `checkCompatible` gained a new `MetropolisBlock` incompatibility check. Verified that the input includes no direct evidence of exploitation or attacker control. Excluded the `transaction_signing.go` hunk from the main finding because the supplied snippet does not support a security claim there. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `chain-config-validation`
Final impact type: `consensus-integrity-risk`
Final confidence: `medium`
Final tags: `consensus, chain-config, fork-validation, security-hardening`

The patch evidence shows a missing `MetropolisBlock` compatibility check being added to `ChainConfig.checkCompatible`, which prevents retroactive fork-schedule changes from being accepted for already-synced history. That is a security-sensitive consensus guardrail, so the change fits `security-hardening`. However, the supplied hunks do not prove an exploitable vulnerability, attacker control, or an observed consensus break, so this should not be elevated to a confirmed `security-fix`.

## Security Evidence

1. `checkCompatible` gained a new `isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head)` check.
2. The new branch returns `ConfigCompatError` for a mismatched historical `Metropolis fork block`.
3. Nearby context states `ConfigCompatError` is used when a chain config would `alter the past`.
4. The change is in fork activation and chain configuration logic, which is consensus-sensitive.
5. `IsMetropolis` was added as a shared fork-state helper, reinforcing explicit handling of that fork boundary.

## Missing Evidence

1. No evidence shows an external attacker can influence local chain configuration.
2. No exploit, incident, or consensus split is demonstrated in the supplied material.
3. No test or report is provided showing unsafe behavior before the patch.
4. The `transaction_signing.go` snippet does not substantiate a signature or replay-security flaw.

## Claim Boundaries

1. Supported: the commit adds missing validation for historical `MetropolisBlock` compatibility.
2. Supported: the change hardens consensus/fork-configuration handling.
3. Not supported: a concrete exploitable vulnerability was definitively fixed.
4. Not supported: the commit fixes transaction-signing, replay, or cryptographic validation bugs.
