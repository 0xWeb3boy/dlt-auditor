---
case_id: case_20260217_d9fac7a4c
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
bug_class: input-validation
impact_type:
  - correctness-or-hardening
source_quality: high
date: 2026-02-17
source_refs:
  - git:d9fac7a4ce401dc9d2cac972e2dd9fb1bcb5cd6d
  - "consensus/clique/clique.go:353"
  - "consensus/bor/bor.go:508"
  - "crypto/crypto.go:204"
  - "consensus/misc/eip1559/eip1559.go:44"
confidence: medium
tags:
  - consensus
  - cryptography
  - input-validation
  - malformed-input
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a set of validation hardening changes in consensus and crypto code, especially replacing `Uint64()`-based block-number continuity checks with explicit `big.Int` arithmetic in Clique and Bor. That is a real correctness improvement in sensitive code, but the provided material does not establish a concrete vulnerability, exploit path, or security impact, so the change should be treated as security-relevant hardening at most, not a confirmed security fix.

## Observed Patch Facts

1. In `consensus/clique/clique.go`, the patch replaces `if parent == nil || parent.Number.Uint64() != number-1 || parent.Hash() != header.Par...` with `if parent == nil || parent.Hash() != header.ParentHash {`.

2. In `consensus/bor/bor.go`, the patch replaces `if parent == nil || parent.Number.Uint64() != number-1 || parent.Hash() != header.Par...` with `if parent == nil || parent.Hash() != header.ParentHash {`.

3. In `crypto/crypto.go`, the patch adds `// Check coordinates are < P, to protect against potential misses in Unmarshal implem...`.

4. In `consensus/misc/eip1559/eip1559.go`, the patch adds `// Verify the parent header is not malformed`.

## Project Context

The changed code sits primarily in `consensus/clique`, `consensus/bor`, `consensus/misc/eip1559`, which anchors the finding in the `cryptography` area of the project. Historical context from `consensus/misc/eip1559/eip1559_test.go`, `consensus/clique/snapshot_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/misc/eip1559/eip1559_test.go`, `consensus/clique/snapshot_test.go`. The strongest project-level identifiers around this patch are `parent`, `header`, `Number`, and `Verify`. Nearby tests or test-like files include `crypto/signify/signify_fuzz.go`, `crypto/blake2b/blake2b_f_fuzz_test.go`.

## Before/After Behavior

Before the patch, Clique and Bor combined parent existence, parent-hash match, and block-number continuity into one condition using `parent.Number.Uint64() != number-1`, and returned `ErrUnknownAncestor` for any failure. After the patch, they first require a known parent with matching hash, then separately require `header.Number - parent.Number == 1` using `big.Int`, returning `ErrInvalidNumber` for bad continuity. Separately, EIP-1559 header verification now rejects a London parent with missing `BaseFee` before fee calculation, and public-key unmarshalling now rejects coordinates `>= P` before `IsOnCurve`.

# Root Cause

Validation logic relied on implicit or narrower checks instead of explicit structural validation. In the clearest case, consensus code used a `Uint64()` comparison for block-number continuity rather than full-precision arithmetic; adjacent changes likewise add explicit malformed-input checks that were previously assumed away.

## Walkthrough

1. `consensus/clique/clique.go` stops using `parent.Number.Uint64() != number-1` inside the ancestor check and instead performs a separate `big.Int` continuity check.

2. `consensus/bor/bor.go` makes the same change, so the behavior is not isolated to one consensus engine.

3. That change also separates error cases: an unknown or mismatched parent still yields `ErrUnknownAncestor`, while a known parent with the wrong number now yields `ErrInvalidNumber`.

4. `consensus/misc/eip1559/eip1559.go` adds an explicit guard against a London parent header with `BaseFee == nil` before calling `CalcBaseFee(config, parent)`.

5. `crypto/crypto.go` adds `x < P` and `y < P` checks before `IsOnCurve`, with the code comment stating this protects against possible misses in unmarshal implementations.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/clique/clique.go | 353 | Clique header validation: parent linkage and exact block-number continuity |
| consensus/bor/bor.go | 508 | Bor header validation: parent linkage and exact block-number continuity |
| consensus/misc/eip1559/eip1559.go | 44 | EIP-1559 header validation: reject malformed London parent without base fee |
| crypto/crypto.go | 204 | Public-key parsing: reject secp256k1 coordinates outside field modulus |

## Code Snippets

## Snippet 1

Context: `consensus/clique/clique.go:353` (changes signature or replay validation logic)

Before
```go
}

	if parent == nil || parent.Number.Uint64() != number-1 || parent.Hash() != header.ParentHash {
		return consensus.ErrUnknownAncestor
	}

	if parent.Time+c.config.Period > header.Time {
		return errInvalidTimestamp
```
After
```go
}

	if parent == nil || parent.Hash() != header.ParentHash {
		return consensus.ErrUnknownAncestor
	}

	// Verify block number continuity
	if diff := new(big.Int).Sub(header.Number, parent.Number); diff.Cmp(big.NewInt(1)) != 0 {
```

## Snippet 2

Context: `consensus/bor/bor.go:508` (changes signature or replay validation logic)

Before
```go
}

	if parent == nil || parent.Number.Uint64() != number-1 || parent.Hash() != header.ParentHash {
		return consensus.ErrUnknownAncestor
	}

	// Verify that the gasUsed is <= gasLimit
	if header.GasUsed > header.GasLimit {
```
After
```go
}

	if parent == nil || parent.Hash() != header.ParentHash {
		return consensus.ErrUnknownAncestor
	}

	// Verify block number continuity
	if diff := new(big.Int).Sub(header.Number, parent.Number); diff.Cmp(big.NewInt(1)) != 0 {
```

## Snippet 3

Context: `crypto/crypto.go:204` (changes a sensitive control or state-update path)

Before
```go
return nil, errInvalidPubkey
	}
	if !S256().IsOnCurve(x, y) {
		return nil, errInvalidPubkey
```
After
```go
return nil, errInvalidPubkey
	}
	// Check coordinates are < P, to protect against potential misses in Unmarshal implementations.
	if x.Cmp(S256().Params().P) >= 0 || y.Cmp(S256().Params().P) >= 0 {
		return nil, errInvalidPubkey
	}
	if !S256().IsOnCurve(x, y) {
		return nil, errInvalidPubkey
```

## Snippet 4

Context: `consensus/misc/eip1559/eip1559.go:44` (changes a sensitive control or state-update path)

Before
```go
return errors.New("header is missing baseFee")
	}
	// Verify the baseFee is correct based on the parent header.
	expectedBaseFee := CalcBaseFee(config, parent)
```
After
```go
return errors.New("header is missing baseFee")
	}
	// Verify the parent header is not malformed
	if config.IsLondon(parent.Number) && parent.BaseFee == nil {
		return errors.New("parent header is missing baseFee")
	}
	// Verify the baseFee is correct based on the parent header.
	expectedBaseFee := CalcBaseFee(config, parent)
```

# Fix Pattern

Add explicit structural validation at trust boundaries and use exact representations for numeric checks instead of truncated conversions or downstream assumptions.

## How It Was Fixed

The patch rewrites block-number continuity checks in Clique and Bor to use `big.Int` subtraction and a strict `== 1` comparison, adds a malformed-parent check in EIP-1559 fee validation, and adds field-bound checks for unmarshalled secp256k1 public-key coordinates.

# Why It Matters

1. Exact arithmetic avoids ambiguity from narrowed integer comparisons.

2. Malformed inputs are rejected earlier and with more specific error handling.

3. The code no longer assumes parent fee data or parsed key coordinates were already sanitized.

4. The evidence shows stronger validation, but not a demonstrated exploit.

# Evidence Notes

The strongest evidence is the direct replacement of `parent.Number.Uint64() != number-1` with a `big.Int` difference check in `consensus/clique/clique.go` and `consensus/bor/bor.go`. The EIP-1559 and public-key changes are also directly supported by the snippets. However, the provided material does not show any exploit, consensus split, signature bypass, or concrete attacker-controlled path, and it provides no substantive evidence for the p2p-related files listed in the commit metadata. Protocol security invariant: Header and key-processing paths should reject structurally malformed inputs before deeper processing: parent linkage must be exact, block-number continuity must be checked with full-precision arithmetic, London fee logic must not read a parent missing required fee data, and parsed secp256k1 points must stay within field bounds. Verification notes: The patch does not prove an end-to-end exploitable attack, only that malformed inputs were previously validated too loosely. It is not shown that a network peer could force durable consensus divergence rather than only trigger local rejection/acceptance differences. The public-key change does not by itself prove signature forgery; it may be defensive against parser inconsistency. The provided evidence does not establish the security impact of the p2p files touched elsewhere in the commit. No claim retained about the p2p files because no supporting diff was provided. No claim retained about signature forgery or replay because the snippets do not demonstrate that impact. The strongest grounded characterization is validation hardening in sensitive code, not a proven vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final confidence: `medium`
Final tags: `consensus, cryptography, input-validation, malformed-input, security-hardening`

The supplied patch evidence supports retaining this as a security-hardening case, not a proven security fix. The changes add stricter validation in consensus-critical and cryptographic parsing paths: full-precision block-number continuity checks, explicit rejection of malformed London parent headers, and explicit secp256k1 coordinate bounds checks. Those are security-relevant trust-boundary hardenings, but the patch alone does not prove a concrete exploitable vulnerability, attack path, or impact such as signature bypass, consensus split, or remote denial of service.

## Security Evidence

1. Clique and Bor replace `Uint64()`-based continuity checks with exact `big.Int` arithmetic in header validation.
2. The new consensus checks distinguish malformed block numbering from unknown ancestry, tightening validation of untrusted headers.
3. `UnmarshalPubkey` now rejects coordinates `>= P` before curve checks, explicitly guarding against parser misses.
4. EIP-1559 validation now rejects a malformed London parent missing `BaseFee` before fee computation.
5. All shown changes sit in security-sensitive code paths: consensus header validation and cryptographic key parsing.

## Missing Evidence

1. No proof that the prior `Uint64()` logic was exploitable in practice or caused consensus acceptance of invalid blocks.
2. No evidence of a demonstrated attacker-controlled exploit, consensus split, signature forgery, or remotely triggerable DoS.
3. No patch evidence was provided for the p2p-related files listed in the commit metadata.
4. No advisory, test, or commit text ties these changes to a specific disclosed vulnerability.

## Claim Boundaries

1. Supported claim: the commit hardens validation of malformed inputs in consensus and crypto paths.
2. Not supported: a confirmed exploitable vulnerability was fixed.
3. Not supported: any specific impact such as signature bypass, replay, consensus split, or remote DoS.
4. Not supported: security claims about the p2p files, because no corresponding diff evidence was supplied.
