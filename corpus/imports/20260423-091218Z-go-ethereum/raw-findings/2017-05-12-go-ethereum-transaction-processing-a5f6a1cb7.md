---
case_id: case_20170512_a5f6a1cb7
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2017-05-12
source_refs:
  - git:a5f6a1cb7c5e5dde130391e9bed7625ef9ff36b5
  - "params/config.go:238"
  - "params/config.go:268"
  - "core/types/transaction_signing.go:109"
  - "params/config.go:177"
bug_class: consensus-configuration-hardening
impact_type:
  - consensus-configuration-mismatch
tags:
  - infrastructure
  - consensus
  - chain-config
  - fork-compatibility
  - metropolis
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded security-relevant change is in params/config.go: ChainConfig.checkCompatible now rejects incompatible MetropolisBlock settings, matching the existing compatibility checks for earlier fork blocks. The evidence supports consensus-configuration hardening, not a confirmed exploitable vulnerability, transaction replay flaw, or VM execution bug.

## Observed Patch Facts

1. In `params/config.go`, the patch adds `if isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head) {`.

2. In `params/config.go`, the patch replaces `func (c *ChainConfig) IsMetropolis(num *big.Int) bool {` with `// ConfigCompatError is raised if the locally-stored blockchain is initialised with a`.

3. In `core/types/transaction_signing.go`, the patch replaces `/*` with `// EIP155Transaction implements TransactionInterface using the`.

4. In `params/config.go`, the patch adds `func (c *ChainConfig) IsMetropolis(num *big.Int) bool {`.

## Project Context

The changed code sits primarily in `core/types`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/types/transaction.go`, `core/types/transaction_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/types/transaction.go`, `core/types/receipt.go`. The strongest project-level identifiers around this patch are `MetropolisBlock`, `newcfg`, `ChainConfig`, and `returns`.

## Before/After Behavior

Before the patch, checkCompatible checked several prior fork fields and EIP158 chain ID, then returned nil without a MetropolisBlock incompatibility check. After the patch, it calls isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head) and returns a ConfigCompatError labelled "Metropolis fork block" on conflict. The IsMetropolis helper was also moved/aligned to call isForked(c.MetropolisBlock, num). The transaction_signing.go hunk removes commented-out EIP86Signer skeleton code and shows no active transaction behavior change.

# Root Cause

MetropolisBlock was omitted from the same chain configuration compatibility boundary used for earlier consensus fork blocks. Based on the shown code, that meant a replacement ChainConfig could avoid rejection solely because the changed field was the Metropolis activation height.

## Walkthrough

1. ChainConfig.checkCompatible compares a stored chain configuration with a new configuration at a given head block.

2. Existing logic rejected incompatible historical settings for Homestead, DAO, EIP150, EIP155, and EIP158-related fields.

3. The pre-patch function returned nil after the EIP158 chain ID check, with no shown MetropolisBlock check.

4. The patch adds an isForkIncompatible check for c.MetropolisBlock and newcfg.MetropolisBlock.

5. When incompatible, the patched code returns newCompatError("Metropolis fork block", c.MetropolisBlock, newcfg.MetropolisBlock).

6. The IsMetropolis helper is implemented through the shared isForked predicate, aligning it with nearby fork helpers.

7. The transaction_signing.go change is inactive commented-code cleanup and is not evidence of a signature or replay fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| params/config.go | 218 | Adds MetropolisBlock to ChainConfig compatibility checks so a stored chain is not accepted under an incompatible past Metropolis fork height. |
| params/config.go | 175 | Defines IsMetropolis through the shared isForked predicate, aligning fork activation checks with other fork helpers. |
| core/types/transaction_signing.go | 109 | Removes commented-out EIP86 signer skeleton code; no active transaction validation behavior is shown changing in the provided evidence. |

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

Extend fork-configuration compatibility checks to cover the newly supported fork boundary, using the same shared predicates already used for earlier forks.

## How It Was Fixed

The patch added an explicit MetropolisBlock incompatibility branch to ChainConfig.checkCompatible and implemented IsMetropolis through isForked.

# Why It Matters

1. Prevents accepting a replacement configuration that changes the Metropolis fork boundary after it matters to the stored chain.

2. Keeps Metropolis compatibility behavior aligned with earlier consensus fork checks.

3. Reduces risk of local chain reinterpretation or consensus configuration mismatch.

4. Does not establish direct exploitability from the supplied evidence.

# Evidence Notes

Primary evidence is the params/config.go checkCompatible hunk adding the MetropolisBlock isForkIncompatible branch. Supporting evidence is the IsMetropolis helper alignment with isForked. The transaction_signing.go hunk removes commented-out EIP86Signer code only and should not be used to claim transaction replay, signature validation, or active cryptographic behavior changes. VM-related claims are unsupported by the supplied hunks. Protocol security invariant: A node with an existing local chain should reject a replacement ChainConfig that would change consensus fork boundaries already relevant at the current head. The patch extends that compatibility invariant to MetropolisBlock. Verification notes: No direct exploitability is proven by the patch evidence. No transaction replay vulnerability is shown in active code paths. No VM execution vulnerability is established from the provided hunks. The transaction_signing.go change appears to be inactive commented-code cleanup. The evidence supports consensus configuration hardening, not a confirmed externally triggerable vulnerability. Verified from provided evidence only; no external context used. Security classification is hardening/likely, not confirmed vulnerability. No evidence supports an externally triggerable exploit path. No evidence supports transaction-processing or VM bug claims. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-configuration-hardening`
Final impact type: `consensus-configuration-mismatch`
Final tags: `infrastructure, consensus, chain-config, fork-compatibility, metropolis, security-hardening`

The supplied evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The active patch adds MetropolisBlock to ChainConfig compatibility checks, preventing acceptance of a new chain configuration that would alter an already-relevant consensus fork boundary. That is security-sensitive consensus configuration hardening. The transaction/signature-related evidence is inactive commented-code cleanup and should not drive the classification.

## Security Evidence

1. checkCompatible now rejects incompatible MetropolisBlock settings using isForkIncompatible.
2. The new error path labels the mismatch as "Metropolis fork block", aligning it with existing fork compatibility checks.
3. ConfigCompatError is described as protecting against a ChainConfig that would alter the past.
4. IsMetropolis is aligned with the shared isForked helper for fork activation checks.

## Missing Evidence

1. No exploit path or externally triggerable attack is shown.
2. No evidence shows an active transaction replay or signature validation bug.
3. No VM execution vulnerability is supported by the provided hunks.
4. No tests or commit body demonstrate an observed consensus failure.

## Claim Boundaries

1. Classify as consensus configuration hardening, not a confirmed security fix.
2. Do not claim transaction-processing, signature, replay, or VM impact from this evidence.
3. Impact should be limited to preventing incompatible fork configuration or chain reinterpretation risk.
4. The evidence supports likelihood of security relevance because consensus fork boundaries are security-sensitive.
