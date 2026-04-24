---
case_id: case_20211215_e2b938562
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2021-12-15
source_refs:
  - git:e2b938562a3856db77c091e8dd8e693994d17d3f
  - "consensus/bor/bor.go:173"
  - "consensus/bor/bor.go:149"
  - "consensus/bor/bor_test.go:100"
  - "consensus/bor/bor.go:137"
bug_class: signature-domain-mismatch
impact_type:
  - consensus-integrity
tags:
  - consensus
  - signature
  - fork-rules
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects Bor's seal-hash computation around the Jaipur fork by making the signed header encoding fork-aware. The provided evidence shows that the pre-fix Bor seal hash omitted `BaseFee` in the relevant post-EIP-1559 path, and the fix propagates fork config into `SealHash` and `ecrecover` so signer recovery uses the updated encoding.

## Observed Patch Facts

1. In `consensus/bor/bor.go`, the patch replaces `})` with `if c.IsJaipur(header.Number.Uint64()) {`.

2. In `consensus/bor/bor.go`, the patch replaces `func SealHash(header *types.Header) (hash common.Hash) {` with `func SealHash(header *types.Header, c *params.BorConfig) (hash common.Hash) {`.

3. In `consensus/bor/bor_test.go`, the patch adds `func TestEncodeSigHeaderJaipur(t *testing.T) {`.

4. In `consensus/bor/bor.go`, the patch replaces `pubkey, err := crypto.Ecrecover(SealHash(header).Bytes(), signature)` with `pubkey, err := crypto.Ecrecover(SealHash(header, c).Bytes(), signature)`.

## Project Context

The changed code sits primarily in `consensus/bor`, which anchors the finding in the `cryptography` area of the project. Historical context from `consensus/bor/snapshot.go`, `consensus/bor/genesis_contracts_client.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/bor/snapshot.go`, `consensus/bor/genesis_contracts_client.go`. The strongest project-level identifiers around this patch are `header`, `hash`, `SealHash`, and `types`.

## Before/After Behavior

Before the patch, `SealHash` and `ecrecover` used a fixed header encoding that ended at `header.Nonce`, with no fork-config input. After the patch, `SealHash` takes `*params.BorConfig`, `ecrecover` uses that fork-aware hash, and `encodeSigHeader` conditionally appends `header.BaseFee` when `c.IsJaipur(header.Number.Uint64())` is true.

# Root Cause

A fork-unaware canonicalization bug in the Bor seal-hash path caused post-fork signer hashing to omit the `BaseFee` field that Jaipur-era rules expected.

## Walkthrough

1. `encodeSigHeader` was changed from directly RLP-encoding a fixed field list to building the list and conditionally appending `header.BaseFee` under `c.IsJaipur(...)`.

2. `SealHash` was widened from `SealHash(header)` to `SealHash(header, c)`, making seal-hash derivation depend on active Bor fork config.

3. `ecrecover` now calls `crypto.Ecrecover(SealHash(header, c).Bytes(), signature)` instead of hashing the header without fork context.

4. The added `TestEncodeSigHeaderJaipur` explicitly states that Bor previously used an incorrect seal hash that did not include `BaseFee` and that Jaipur fixes it.

5. Together, the observed changes support a consensus/signature-domain correction, not the draft's earlier crash or malformed-input theory.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/bor/bor.go | 158 | Canonical RLP encoding of header fields used to derive the Bor seal hash; now conditionally includes `BaseFee` after Jaipur |
| consensus/bor/bor.go | 126 | Signer recovery path that verifies/reconstructs the validator identity from the fork-aware seal hash |
| consensus/bor/bor.go | 149 | `SealHash` helper whose API was widened to accept Bor fork config so signature hashing follows chain rules |
| consensus/bor/bor_test.go | 94 | Regression coverage documenting that the pre-fix Bor seal hash omitted `BaseFee` around the EIP-1559 transition |

## Code Snippets

## Snippet 1

Context: `consensus/bor/bor.go:173` (changes persisted or aggregate state handling)

Before
```go
header.MixDigest,
		header.Nonce,
	})
	if err != nil {
		panic("can't encode: " + err.Error())
	}
```
After
```go
header.MixDigest,
		header.Nonce,
	}
	if c.IsJaipur(header.Number.Uint64()) {
		if header.BaseFee != nil {
			enc = append(enc, header.BaseFee)
		}
	}
```

## Snippet 2

Context: `consensus/bor/bor.go:149` (changes signature or replay validation logic)

Before
```go
// SealHash returns the hash of a block prior to it being sealed.
func SealHash(header *types.Header) (hash common.Hash) {
	hasher := sha3.NewLegacyKeccak256()
	encodeSigHeader(hasher, header)
	hasher.Sum(hash[:0])
	return hash
}
```
After
```go
// SealHash returns the hash of a block prior to it being sealed.
func SealHash(header *types.Header, c *params.BorConfig) (hash common.Hash) {
	hasher := sha3.NewLegacyKeccak256()
	encodeSigHeader(hasher, header, c)
	hasher.Sum(hash[:0])
	return hash
}
```

## Snippet 3

Context: `consensus/bor/bor_test.go:100` (changes signature or replay validation logic)

Before
```go
assert.Equal(t, statedb.GetBalance(addr0), big.NewInt(0))
}
```
After
```go
assert.Equal(t, statedb.GetBalance(addr0), big.NewInt(0))
}

func TestEncodeSigHeaderJaipur(t *testing.T) {
	// As part of the EIP-1559 fork in mumbai, an incorrect seal hash
	// was used for Bor that did not included the BaseFee. The Jaipur
	// block is a hard fork to fix that.
	h := &types.Header{
```

## Snippet 4

Context: `consensus/bor/bor.go:137` (changes signature or replay validation logic)

Before
```go
// Recover the public key and the Ethereum address
	pubkey, err := crypto.Ecrecover(SealHash(header).Bytes(), signature)
	if err != nil {
		return common.Address{}, err
```
After
```go
// Recover the public key and the Ethereum address
	pubkey, err := crypto.Ecrecover(SealHash(header, c).Bytes(), signature)
	if err != nil {
		return common.Address{}, err
```

# Fix Pattern

Make the canonical signature-domain encoding fork-aware and thread the active chain configuration through all seal-hash and signer-recovery call sites.

## How It Was Fixed

The fix passes `*params.BorConfig` into the seal-hash path, updates signer recovery to use the fork-aware digest, and includes `BaseFee` in the RLP-encoded signed header payload for Jaipur-era blocks. A regression test documents the intended behavior.

# Why It Matters

1. Signer recovery only works correctly if all nodes hash the same fork-specific header fields.

2. Omitting `BaseFee` means the signature is bound to an incomplete post-fork header representation.

3. In a consensus path, that kind of mismatch can create protocol-integrity risk even if the evidence here does not show a full exploit chain.

# Evidence Notes

The strong evidence is limited to the Bor consensus code and the added test comment. It supports a fork-specific seal-hash mismatch involving `BaseFee`; it does not support claims about panics, memory corruption, remote crashability, fund theft, or signature forgery. Protocol security invariant: Bor signer recovery must use the same fork-specific header encoding that validators sign. After the Jaipur fork condition, the seal hash needs to include `BaseFee` when present so all participants derive the same signed digest from the same header. Verification notes: The patch does not prove signature forgery; it shows a mismatch in which header fields are hashed. The patch does not demonstrate a remote crash, memory-corruption issue, or generic denial-of-service primitive. The evidence does not prove fund theft or unauthorized state transitions. The patch most directly supports a fork-specific consensus/authentication correction for Bor networks using Jaipur-era rules. `consensus/bor/bor.go` directly shows the fork-aware `SealHash` and `ecrecover` changes. `consensus/bor/bor.go` directly shows `encodeSigHeader` appending `BaseFee` only for Jaipur. `consensus/bor/bor_test.go` explicitly documents the pre-fix omission of `BaseFee` and the Jaipur fix. Security impact is inferred from the consensus/signature role of the changed path, so confidence is reduced from high to medium. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-domain-mismatch`
Final impact type: `consensus-integrity`
Final tags: `consensus, signature, fork-rules, validator`

The patch changes Bor's signer-recovery and seal-hash derivation so the authenticated header encoding becomes fork-aware and includes `BaseFee` for Jaipur-era blocks. That is a security-sensitive consensus/authentication path, and the added test explicitly says the prior seal hash was incorrect. The evidence supports retaining this as security hardening for consensus-integrity/signature-domain correctness, but it does not prove a concrete exploitable vulnerability or specific real-world attack from the patch alone.

## Security Evidence

1. `SealHash` and `ecrecover` were updated to take `*params.BorConfig`, so validator recovery now follows active fork rules.
2. `encodeSigHeader` now conditionally appends `header.BaseFee` for Jaipur blocks, changing the fields covered by the signed hash.
3. The added regression test states the previous Bor seal hash was incorrect because it omitted `BaseFee`, and Jaipur fixes that.
4. The modified code is in consensus signature hashing and validator recovery, not peripheral product or maintenance code.

## Missing Evidence

1. No proof that an attacker could forge signatures, impersonate validators, or get invalid blocks accepted.
2. No concrete evidence of a chain split, finalized safety failure, or remotely triggerable denial of service in the patch itself.
3. No evidence showing whether the bug was only upgrade-compatibility/correctness versus an actively exploitable flaw.

## Claim Boundaries

1. Supported: the commit fixes a fork-specific mismatch in the header fields covered by Bor seal hashing.
2. Supported: the change hardens a security-sensitive consensus/signature-validation path.
3. Not supported: fund theft, memory corruption, generic remote DoS, or direct signature forgery claims.
4. Not supported: any impact claim more specific than consensus-integrity/authentication correctness risk.
