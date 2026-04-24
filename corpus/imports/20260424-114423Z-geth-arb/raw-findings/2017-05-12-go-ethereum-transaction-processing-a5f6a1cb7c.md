---
case_id: case_20170512_a5f6a1cb7c
project: go-ethereum
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
bug_class: consensus-config-compatibility-hardening
impact_type:
  - consensus-configuration-integrity
confidence: medium
tags:
  - infrastructure
  - chain-config
  - consensus
  - fork-activation
  - compatibility-check
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded change is that params/config.go now checks MetropolisBlock in ChainConfig.checkCompatible, matching existing checks for earlier fork blocks. This may be consensus-safety hardening, but the supplied evidence does not prove that the prior omission caused an exploitable security vulnerability. The transaction_signing.go hunk appears to remove commented EIP86 stub code and should not be treated as a cryptographic or replay fix.

## Observed Patch Facts

1. In `params/config.go`, the patch adds `if isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head) {`.

2. In `params/config.go`, the patch replaces `func (c *ChainConfig) IsMetropolis(num *big.Int) bool {` with `// ConfigCompatError is raised if the locally-stored blockchain is initialised with a`.

3. In `core/types/transaction_signing.go`, the patch replaces `/*` with `// EIP155Transaction implements TransactionInterface using the`.

4. In `params/config.go`, the patch adds `func (c *ChainConfig) IsMetropolis(num *big.Int) bool {`.

## Project Context

The changed code sits primarily in `core/types`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/types/transaction.go`, `core/types/transaction_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/types/transaction.go`, `core/types/receipt.go`. The strongest project-level identifiers around this patch are `MetropolisBlock`, `newcfg`, `ChainConfig`, and `returns`.

## Before/After Behavior

Before the patch, checkCompatible rejected incompatible historical changes for several fork fields, then returned nil after the EIP158 chain ID check; the shown snippet has no MetropolisBlock compatibility check. After the patch, checkCompatible returns a ConfigCompatError labeled "Metropolis fork block" when c.MetropolisBlock and newcfg.MetropolisBlock are incompatible at the current head. IsMetropolis is present as return isForked(c.MetropolisBlock, num).

# Root Cause

The ChainConfig compatibility gate omitted MetropolisBlock from the same historical fork incompatibility checks already applied to earlier fork activation fields. The evidence supports a configuration-consistency gap, not a proven vulnerability root cause.

## Walkthrough

1. ChainConfig.checkCompatible compares the stored chain configuration with a replacement configuration at a given head block.

2. Existing code already checked several earlier fork activation fields for historical incompatibility.

3. The before snippet returned nil without a visible MetropolisBlock check after the EIP158 chain ID check.

4. The patch adds isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head).

5. If incompatible, the function now returns newCompatError("Metropolis fork block", c.MetropolisBlock, newcfg.MetropolisBlock).

6. The IsMetropolis predicate shows MetropolisBlock controls whether Metropolis rules apply at a block number.

7. The evidence supports possible consensus-configuration hardening, but not remote exploitability, a demonstrated chain split, or a transaction-signing vulnerability.

8. The transaction_signing.go change is cleanup of commented EIP86 code in the provided evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| params/config.go | 218 | ChainConfig compatibility gate that rejects new configs which would alter past fork activation rules |
| params/config.go | 175 | Metropolis fork activation predicate used to decide whether Metropolis rules apply at a block number |
| core/types/transaction_signing.go | 78 | Signer interface area; shown hunk removes/comment-cleans unused EIP86 signer stub without proving a security behavior change |

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

Add the new fork activation field to the existing ChainConfig compatibility checks so replacement configs are evaluated consistently with earlier fork fields.

## How It Was Fixed

The patch adds a MetropolisBlock incompatibility check to params/config.go checkCompatible and returns a ConfigCompatError when the stored and new Metropolis fork blocks conflict with the current head. It also keeps IsMetropolis on the shared isForked helper path. No functional security change is established for transaction_signing.go from the shown hunk.

# Why It Matters

1. Fork activation blocks affect which consensus rules apply.

2. Compatibility checks reduce the risk of reinterpreting stored chain history under changed fork settings.

3. The patch is plausibly security relevant, but the provided evidence does not establish a vulnerability.

4. No transaction replay or signature-validation fix is supported by the shown evidence.

# Evidence Notes

Strongest evidence is params/config.go around checkCompatible and IsMetropolis. The code shows a missing MetropolisBlock compatibility check being added. The claim should stay limited to chain configuration consistency. The provided evidence does not prove exploitability, a concrete consensus failure, normal-operation impact, or any security impact from the commented EIP86 signer cleanup. Protocol security invariant: A node should reject a replacement ChainConfig that would change fork activation history at or before the current head. The patch extends the existing compatibility check pattern to MetropolisBlock, but the provided evidence does not establish a concrete vulnerability or exploit path. Verification notes: No remote exploitability is proven by the patch evidence. No transaction replay or signature-validation vulnerability is proven by the shown transaction_signing.go cleanup. No evidence shows consensus failure in normal operation absent a mismatched ChainConfig update. Other touched files are listed in the commit metadata, but no concrete security-relevant hunks from them are provided. Downgraded security_verdict from likely to unclear because vulnerability impact is not established. Downgraded keep_in_security_corpus to false under the instruction for unclear security relevance. Changed subsystem from transaction-processing to chain-config. Removed unsupported transaction replay and cryptographic-fix implications. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-config-compatibility-hardening`
Final impact type: `consensus-configuration-integrity`
Final confidence: `medium`
Final tags: `infrastructure, chain-config, consensus, fork-activation, compatibility-check, hardening`

The evidence supports retaining this as security hardening, not a proven vulnerability fix. The patch adds MetropolisBlock to ChainConfig compatibility checks that prevent a stored blockchain from being used with a configuration that would alter past fork activation rules. Because fork activation controls consensus behavior, this is a clear tightening of consensus-sensitive configuration validation. The transaction-signing hunk is only commented-code cleanup and should not contribute to the security claim.

## Security Evidence

1. Adds isForkIncompatible check for MetropolisBlock in ChainConfig.checkCompatible.
2. New failure path returns ConfigCompatError labeled "Metropolis fork block".
3. Surrounding checks already reject incompatible historical fork activation fields.
4. ConfigCompatError is documented as applying when a stored blockchain is initialized with a ChainConfig that would alter the past.
5. IsMetropolis derives Metropolis rule activation from MetropolisBlock.

## Missing Evidence

1. No demonstrated exploit path or remote attacker influence is shown.
2. No evidence of an observed chain split or consensus failure is provided.
3. No test or incident context proves the prior omission was exploitable.
4. No security-relevant transaction-signing behavior change is shown.

## Claim Boundaries

1. Treat as consensus configuration hardening only.
2. Do not claim a transaction replay or cryptographic signature validation fix.
3. Do not claim confirmed exploitability or a concrete consensus failure.
4. Impact should be limited to preventing incompatible fork-activation configuration from altering historical rule interpretation.
