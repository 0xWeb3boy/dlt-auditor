---
case_id: case_20250724_9836e33a2
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-07-24
source_refs:
  - git:9836e33a207bd64ee4e304118fdd733d8f2ec32c
  - "x/evm/ante/preprocess.go:302"
  - "precompiles/addr/legacy/v610/addr.go:221"
  - "precompiles/addr/legacy/v606/addr.go:221"
  - "precompiles/addr/legacy/v605/addr.go:221"
bug_class: vulnerable-cryptographic-dependency
impact_type:
  - unspecified-security-impact
confidence: medium
tags:
  - dependency-update
  - cve
  - cryptography
  - public-key-parsing
  - btcec
  - x-crypto
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded finding is a cryptographic dependency security update with required btcec API migration. The commit message explicitly says the btcec and x/crypto bumps fix CVE-2022-44797 and CVE-2024-45337. The supplied code evidence shows public-key parsing call sites changed from `btcec.ParsePubKey(bytes, btcec.S256())` to `btcec.ParsePubKey(bytes)` in EVM ante preprocessing and legacy address association precompiles. The evidence does not establish an independent sei-chain authorization, replay, nonce, or signature-validation bug.

## Observed Patch Facts

1. In `x/evm/ante/preprocess.go`, the patch replaces `pk, err := btcec.ParsePubKey(acc.GetPubKey().Bytes(), btcec.S256())` with `pk, err := btcec.ParsePubKey(acc.GetPubKey().Bytes())`.

2. In `precompiles/addr/legacy/v610/addr.go`, the patch replaces `pubKey, err := btcec.ParsePubKey(pubKeyBytes, btcec.S256())` with `pubKey, err := btcec.ParsePubKey(pubKeyBytes)`.

3. In `precompiles/addr/legacy/v606/addr.go`, the patch replaces `pubKey, err := btcec.ParsePubKey(pubKeyBytes, btcec.S256())` with `pubKey, err := btcec.ParsePubKey(pubKeyBytes)`.

4. In `precompiles/addr/legacy/v605/addr.go`, the patch replaces `pubKey, err := btcec.ParsePubKey(pubKeyBytes, btcec.S256())` with `pubKey, err := btcec.ParsePubKey(pubKeyBytes)`.

## Project Context

The changed code sits primarily in `x/evm/ante`, `x/evm`, `precompiles/addr/legacy/v610`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/ante/router_test.go`, `x/evm/ante/preprocess_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/addr/legacy/v603/addr.go`, `precompiles/addr/legacy/v601/addr.go`. The strongest project-level identifiers around this patch are `btcec`, `ParsePubKey`, `pubKey`, and `pubKeyBytes`. Nearby tests or test-like files include `x/evm/integration_test.go`, `x/evm/blocktest/config.go`.

## Before/After Behavior

Before the patch, EVM ante preprocessing and legacy address association precompile paths parsed secp256k1 public keys using the older two-argument btcec `ParsePubKey` API. After the patch, those same paths use the upgraded one-argument API. Existing behavior on parse failure appears unchanged: the ante path logs and continues without EVM address metadata, while the precompile paths return the parse error.

# Root Cause

The supported root cause is use of older cryptographic dependency versions affected by CVEs, plus call sites tied to the older btcec public-key parsing API. The provided evidence does not prove a separate application-level logic flaw in sei-chain.

## Walkthrough

1. The commit message says btcec and x/crypto were bumped and explicitly names CVE-2022-44797 and CVE-2024-45337.

2. In `x/evm/ante/preprocess.go`, account public keys used during EVM address preprocessing are parsed with btcec.

3. That call changed from `ParsePubKey(acc.GetPubKey().Bytes(), btcec.S256())` to `ParsePubKey(acc.GetPubKey().Bytes())`.

4. In legacy address precompile versions v610, v606, and v605, compressed public-key bytes decoded from hex are parsed with btcec before address association work continues.

5. Those precompile calls changed from `ParsePubKey(pubKeyBytes, btcec.S256())` to `ParsePubKey(pubKeyBytes)`.

6. The shown surrounding code keeps the same parse-error handling.

7. No supplied code excerpt shows a new project-level validation branch, replay check, nonce rule, authorization rule, or signature-verification change.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/ante/preprocess.go | 302 | Parses account public keys during EVM address preprocessing before associating or emitting signer address metadata. |
| precompiles/addr/legacy/v610/addr.go | 221 | Parses compressed public keys supplied to the address association precompile. |
| precompiles/addr/legacy/v606/addr.go | 221 | Legacy address association precompile public-key parsing path. |
| precompiles/addr/legacy/v605/addr.go | 221 | Legacy address association precompile public-key parsing path. |
| go.mod | 0 | Dependency version source for the btcec and x/crypto security updates referenced by the commit. |

## Code Snippets

## Snippet 1

Context: `x/evm/ante/preprocess.go:302` (changes a sensitive control or state-update path)

Before
```go
continue
		}
		pk, err := btcec.ParsePubKey(acc.GetPubKey().Bytes(), btcec.S256())
		if err != nil {
			ctx.Logger().Debug(fmt.Sprintf("failed to parse pubkey for %s, likely due to the fact that it isn't on secp256k1 curve", acc.GetPubKey()), "err", err)
```
After
```go
continue
		}
		pk, err := btcec.ParsePubKey(acc.GetPubKey().Bytes())
		if err != nil {
			ctx.Logger().Debug(fmt.Sprintf("failed to parse pubkey for %s, likely due to the fact that it isn't on secp256k1 curve", acc.GetPubKey()), "err", err)
```

## Snippet 2

Context: `precompiles/addr/legacy/v610/addr.go:221` (changes a sensitive control or state-update path)

Before
```go
// Parse the compressed public key
	pubKey, err := btcec.ParsePubKey(pubKeyBytes, btcec.S256())
	if err != nil {
		return nil, 0, err
```
After
```go
// Parse the compressed public key
	pubKey, err := btcec.ParsePubKey(pubKeyBytes)
	if err != nil {
		return nil, 0, err
```

## Snippet 3

Context: `precompiles/addr/legacy/v606/addr.go:221` (changes a sensitive control or state-update path)

Before
```go
// Parse the compressed public key
	pubKey, err := btcec.ParsePubKey(pubKeyBytes, btcec.S256())
	if err != nil {
		return nil, 0, err
```
After
```go
// Parse the compressed public key
	pubKey, err := btcec.ParsePubKey(pubKeyBytes)
	if err != nil {
		return nil, 0, err
```

## Snippet 4

Context: `precompiles/addr/legacy/v605/addr.go:221` (changes a sensitive control or state-update path)

Before
```go
// Parse the compressed public key
	pubKey, err := btcec.ParsePubKey(pubKeyBytes, btcec.S256())
	if err != nil {
		return nil, 0, err
```
After
```go
// Parse the compressed public key
	pubKey, err := btcec.ParsePubKey(pubKeyBytes)
	if err != nil {
		return nil, 0, err
```

# Fix Pattern

Upgrade vulnerable cryptographic dependencies and migrate affected public-key parsing call sites to the replacement API while preserving existing malformed-key handling.

## How It Was Fixed

The commit updates btcec and x/crypto versions according to the commit metadata, then adjusts btcec call sites to the v2 one-argument `ParsePubKey` signature in EVM ante preprocessing and legacy address precompile code.

# Why It Matters

1. Public-key parsing is part of signer/address identity handling.

2. The commit explicitly references dependency CVE fixes.

3. Malformed public keys must continue to fail before address derivation or association proceeds.

4. The evidence supports dependency security hardening, not a demonstrated sei-chain logic vulnerability.

# Evidence Notes

Evidence is limited to commit metadata and code excerpts. The commit message is direct evidence that the dependency bump was intended to fix CVEs. The shown diff is mostly API migration at public-key parsing call sites. The actual vulnerable behavior inside btcec or x/crypto is not included, and exploitability in sei-chain is not demonstrated. Protocol security invariant: EVM address derivation and address association should only proceed from well-formed secp256k1 public keys. The shown project code preserves the existing parse-error gates while moving those call sites onto the upgraded btcec API; the security relevance is tied to the dependency CVE fixes named in the commit message. Verification notes: The patch evidence does not show a new project-level authorization, nonce, replay, or signature verification check. Exploitability in sei-chain is not proven by the provided diff. The exact vulnerable behavior fixed inside btcec or x/crypto is not shown in the provided evidence. The ParsePubKey call-site behavior appears intended to remain equivalent aside from using the upgraded API. No consensus-level state transition bug is demonstrated by the shown code changes. Confirmed by supplied evidence: btcec `ParsePubKey` call sites changed to the new signature. Confirmed by supplied evidence: commit message names CVE-2022-44797 and CVE-2024-45337. Not shown: dependency diff details from `go.mod` or `go.sum`. Not shown: CVE mechanics or a sei-chain-specific exploit path. Not shown: new application-level replay, nonce, authorization, or signature validation logic. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `vulnerable-cryptographic-dependency`
Final impact type: `unspecified-security-impact`
Final confidence: `medium`
Final tags: `dependency-update, cve, cryptography, public-key-parsing, btcec, x-crypto`

The supplied metadata explicitly states that the dependency bumps fix CVE-2022-44797 and CVE-2024-45337, and the shown patch migrates btcec public-key parsing call sites in security-sensitive address and transaction-processing paths to the upgraded API. However, the code excerpts do not demonstrate a sei-chain-specific replay, request-forgery, authorization, nonce, or signature-validation flaw. This should be retained only as dependency security hardening, with the original replay/signature-validation impact narrowed.

## Security Evidence

1. Commit body explicitly says the btcec and x/crypto bumps fix named CVEs.
2. Changed files include go.mod/go.sum plus implementation call sites using btcec public-key parsing.
3. Public-key parsing occurs in EVM ante preprocessing and address association precompile paths, which are security-sensitive identity/address handling areas.
4. Error handling around invalid public keys appears preserved while moving to the upgraded btcec API.

## Missing Evidence

1. No go.mod/go.sum diff excerpt showing the exact vulnerable-to-fixed dependency version transition.
2. No CVE mechanics or vulnerable behavior inside btcec or x/crypto are supplied.
3. No project-level exploit path is shown for sei-chain.
4. No new replay, nonce, authorization, or signature-verification check is shown.

## Claim Boundaries

1. Classify as dependency security hardening, not a demonstrated sei-chain application logic vulnerability.
2. Do not claim request forgery or replay impact from the supplied patch.
3. Do not claim a consensus or validator bug based only on the shown ParsePubKey API migration.
4. Security relevance rests mainly on the explicit CVE-fix commit metadata and cryptographic dependency update.
