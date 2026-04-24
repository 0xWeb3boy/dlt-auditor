---
case_id: case_20211215_a10f79dc2
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2021-12-15
source_refs:
  - git:a10f79dc2795891f6cbc08e4cb7f3c86366c6528
  - "consensus/bor/bor.go:173"
  - "consensus/bor/bor.go:149"
  - "consensus/bor/bor_test.go:100"
  - "consensus/bor/bor.go:137"
bug_class: insufficient-signature-coverage
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - signature
  - header-hash
  - fork-awareness
  - basefee
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

This patch makes Bor seal-hash computation fork-aware and adds BaseFee to the signed header encoding at Jaipur. The provided evidence supports a consensus-integrity hardening claim: before the change, signer recovery used a seal hash that the added test describes as incorrectly omitting BaseFee after the EIP-1559-related fork.

## Observed Patch Facts

1. In `consensus/bor/bor.go`, the patch replaces `})` with `if c.IsJaipur(header.Number.Uint64()) {`.

2. In `consensus/bor/bor.go`, the patch replaces `func SealHash(header *types.Header) (hash common.Hash) {` with `func SealHash(header *types.Header, c *params.BorConfig) (hash common.Hash) {`.

3. In `consensus/bor/bor_test.go`, the patch adds `func TestEncodeSigHeaderJaipur(t *testing.T) {`.

4. In `consensus/bor/bor.go`, the patch replaces `pubkey, err := crypto.Ecrecover(SealHash(header).Bytes(), signature)` with `pubkey, err := crypto.Ecrecover(SealHash(header, c).Bytes(), signature)`.

## Project Context

The changed code sits primarily in `consensus/bor`, which anchors the finding in the `cryptography` area of the project. Historical context from `consensus/bor/snapshot.go`, `consensus/bor/genesis_contracts_client.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/bor/snapshot.go`, `consensus/bor/genesis_contracts_client.go`. The strongest project-level identifiers around this patch are `header`, `hash`, `SealHash`, and `types`.

## Before/After Behavior

Before the patch, signer recovery used SealHash(header) and encodeSigHeader(w, header) with a fixed encoded field list and no Bor config input. After the patch, SealHash takes Bor config, ecrecover uses SealHash(header, c), and encodeSigHeader conditionally appends header.BaseFee when c.IsJaipur(header.Number.Uint64()) is true.

# Root Cause

The seal-hash path was not fork-aware, so post-fork header hashing could omit BaseFee even when the protocol expected it to matter.

## Walkthrough

1. The signer-recovery path in consensus/bor/bor.go changes from crypto.Ecrecover(SealHash(header).Bytes(), signature) to crypto.Ecrecover(SealHash(header, c).Bytes(), signature).

2. SealHash is updated to accept *params.BorConfig, showing that hash construction now depends on fork configuration.

3. encodeSigHeader is refactored to build an enc slice instead of immediately encoding a fixed field list.

4. The new Jaipur check appends header.BaseFee when the configured fork condition is active.

5. The added test TestEncodeSigHeaderJaipur states that Bor had used an incorrect seal hash that did not include BaseFee and that Jaipur fixes it.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/bor/bor.go | 126 | validator signer recovery now uses fork-aware `SealHash(header, c)` |
| consensus/bor/bor.go | 149 | seal-hash construction changed to accept Bor fork config |
| consensus/bor/bor.go | 158 | header serialization for the signed payload conditionally includes `BaseFee` at Jaipur |
| consensus/bor/bor_test.go | 100 | regression test documenting that pre-fix Bor seal hash omitted `BaseFee` after the EIP-1559-related fork |

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

Make consensus signature hashing fork-aware and include newly relevant header fields in the signed serialization when the active protocol version requires them.

## How It Was Fixed

The patch threads Bor config into SealHash and ecrecover, then updates encodeSigHeader so Jaipur-era headers include BaseFee in the RLP-encoded payload used for signer recovery. A regression test documents the prior omission and the intended corrected behavior.

# Why It Matters

1. Validator signatures should bind to the full consensus-relevant header under the active fork rules.

2. Omitting BaseFee from the seal hash weakens the correspondence between the header being verified and the data covered by the signature.

3. The evidence supports a consensus/signature-scope issue, not memory-safety or code-execution impact.

# Evidence Notes

Direct evidence shows fork-aware hashing was added and BaseFee was conditionally included in the signed header encoding. The strongest support for the prior bug is the new test comment stating that the earlier Bor seal hash omitted BaseFee after the EIP-1559-related fork. The provided snippets do not establish a demonstrated exploit, arbitrary BaseFee manipulation, or broader impact outside consensus/signature verification semantics. Protocol security invariant: The seal hash used for Bor signer recovery should cover the consensus header fields required by the active fork rules. If a fork makes BaseFee part of header semantics, signer verification should hash it too. Verification notes: The patch does not prove a remotely exploitable attack beyond consensus/signature-scope inconsistency. The patch does not prove `BaseFee` could previously be chosen arbitrarily; other validation may still constrain it. The patch does not show confidentiality, memory-safety, or code-execution impact. The patch does not prove an observed chain compromise; it may be a preventive hard-fork correction for consensus integrity. Evidence is limited to the shown diffs and test comment. Security relevance is inferred from consensus signature coverage, not from a demonstrated attack trace. Confidence is reduced because the snippets do not show full validation rules or concrete exploitability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-signature-coverage`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, signature, header-hash, fork-awareness, basefee`

The patch is in a security-sensitive consensus path and changes the data covered by the seal hash used for signer recovery. The added test explicitly says the prior seal hash was incorrect because it omitted `BaseFee` after the EIP-1559-related fork, and the fix makes signature hashing fork-aware. That supports retaining this as security hardening for consensus/signature integrity, but the patch alone does not prove a concrete exploitable vulnerability or chain compromise, so it is better framed as hardening rather than a confirmed security bug fix.

## Security Evidence

1. `SealHash` now takes Bor config and becomes fork-aware.
2. `ecrecover` switches to `SealHash(header, c)` in the signer recovery path.
3. `encodeSigHeader` conditionally appends `header.BaseFee` for Jaipur blocks.
4. The new test states the previous seal hash was incorrect because it omitted `BaseFee`.
5. The changed logic affects block-header hashing and validator signature verification.

## Missing Evidence

1. No proof that an attacker could exploit the omission in practice.
2. No evidence of accepted invalid blocks, forged signatures, or a real incident.
3. No full validation flow showing whether other rules already constrained `BaseFee`.
4. No commit message or patch text explicitly describing a security vulnerability.

## Claim Boundaries

1. Supported claim: the patch hardens consensus signature coverage after a fork rule change.
2. Supported claim: previous signer-recovery hashing omitted a fork-relevant header field.
3. Not supported: a demonstrated exploit, signature forgery, or remote compromise.
4. Not supported: confidentiality, memory-safety, or code-execution impact.
5. Not supported: a pure liveness-only classification; the stronger signal is consensus integrity hardening.
