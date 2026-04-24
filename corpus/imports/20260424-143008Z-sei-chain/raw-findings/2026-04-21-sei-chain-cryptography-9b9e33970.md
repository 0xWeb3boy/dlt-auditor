---
case_id: case_20260421_9b9e33970
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2026-04-21
source_refs:
  - git:9b9e33970f0412352885ae82dee529b699a1a29e
  - "sei-tendermint/crypto/ed25519/ed25519.go:66"
  - "sei-tendermint/crypto/tmhash/hash.go:20"
  - "sei-tendermint/crypto/ed25519/ed25519.go:153"
  - "sei-tendermint/crypto/ed25519/ed25519.go:39"
bug_class: secret-key-lifecycle-hardening
impact_type:
  - secret-key-exposure-risk-reduction
  - memory-lifecycle-hardening
tags:
  - cryptography
  - ed25519
  - secret-key-lifecycle
  - memory-zeroization
  - runtime-keepalive
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is Ed25519 secret-key lifecycle hardening, not a proven exploitable vulnerability. The evidence shows changes to SecretKey representation, runtime cleanup registration, and SignWithTag keepalive behavior. The tmhash removal is not tied to a concrete security invariant in the supplied evidence and should be treated as cleanup/API removal unless more context is provided.

## Observed Patch Facts

1. In `sei-tendermint/crypto/ed25519/ed25519.go`, the patch replaces `raw := utils.Alloc([ed25519.PrivateKeySize]byte(b))` with `type Secret = [ed25519.PrivateKeySize]byte`.

2. In `sei-tendermint/crypto/tmhash/hash.go`, the patch removes `//-------------------------------------------------------------`.

3. In `sei-tendermint/crypto/ed25519/ed25519.go`, the patch replaces `sig := utils.OrPanic1(ed25519.PrivateKey((*k.key)[:]).Sign(nil, msg, opts))` with `defer runtime.KeepAlive(k)`.

4. In `sei-tendermint/crypto/ed25519/ed25519.go`, the patch replaces `// This is a pointer to avoid copying the secret all over the memory.` with `// When using the key make sure to use runtime.KeepAlive, so that key is not zeroized...`.

## Project Context

The changed code sits primarily in `sei-tendermint/crypto/ed25519`, `sei-tendermint/crypto`, `sei-tendermint/crypto/tmhash`, which anchors the finding in the `cryptography` area of the project. Historical context from `sei-tendermint/crypto/ed25519/ed25519_test.go`, `sei-tendermint/crypto/ed25519/json.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/crypto/ed25519/json.go`, `sei-tendermint/crypto/ed25519/ed25519_test.go`. The strongest project-level identifiers around this patch are `ed25519`, `pointer`, `secret`, and `byte`.

## Before/After Behavior

Before the patch, SecretKey stored a direct pointer-to-pointer field, SecretKeyFromSecretBytes registered a cleanup callback that closed over raw while zeroizing it, and SignWithTag used the key without an explicit runtime.KeepAlive. After the patch, SecretKey stores a private closure returning the pointer, AddCleanup receives the raw secret pointer as its cleanup argument, and SignWithTag defers runtime.KeepAlive(k) before signing through k.key().

# Root Cause

The evidence supports a weak secret-key lifecycle boundary rather than an attacker-triggered parsing, verification, or consensus bug. The old representation and cleanup/signing paths did not clearly encode the intended Go runtime reachability invariants for secret key memory.

## Walkthrough

1. SecretKey is the internal Ed25519 private-key representation.

2. The old SecretKey field directly stored key **[ed25519.PrivateKeySize]byte.

3. SecretKeyFromSecretBytes allocated key material and registered cleanup intended to zero secret memory.

4. The old cleanup callback closed over raw, while the new comments state AddCleanup requires the referenced pointer to be unreachable even from the cleanup function.

5. The patch changes AddCleanup so the cleanup callback receives raw *Secret as the cleanup argument.

6. The patch changes SecretKey.key to a private closure returning **Secret, with comments tying that to avoiding reflection extraction from other modules.

7. SignWithTag now defers runtime.KeepAlive(k), keeping the key object live through signing.

8. The tmhash hunk removes truncated-hash code, but the supplied evidence does not establish a vulnerability or security invariant for that part.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/crypto/ed25519/ed25519.go | 39 | SecretKey internal representation; hides key pointer behind closure and documents keepalive/cleanup invariant |
| sei-tendermint/crypto/ed25519/ed25519.go | 64 | Secret key import/allocation path; registers cleanup to zero secret memory without keeping it reachable via closure capture |
| sei-tendermint/crypto/ed25519/ed25519.go | 153 | domain-separated Ed25519 signing path; keeps secret key alive until signing completes |
| sei-tendermint/crypto/tmhash/hash.go | 18 | hash utility cleanup/removal of truncated hash implementation; no concrete security invariant shown in supplied hunk |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/crypto/ed25519/ed25519.go:66` (changes signature or replay validation logic)

Before
```go
return SecretKey{}, fmt.Errorf("ed25519: bad private key length: got %d, want %d", got, want)
	}
	raw := utils.Alloc([ed25519.PrivateKeySize]byte(b))
	runtime.AddCleanup(&raw, func(int) {
		// Zero the memory to avoid leaking the secret.
		for i := range raw {
			raw[i] = 0
		}
```
After
```go
return SecretKey{}, fmt.Errorf("ed25519: bad private key length: got %d, want %d", got, want)
	}
	type Secret = [ed25519.PrivateKeySize]byte
	raw := utils.Alloc(Secret(b))
	runtime.AddCleanup(&raw, func(raw *Secret) {
		// Zero the memory to avoid leaking the secret.
		for i := range raw {
			raw[i] = 0
```

## Snippet 2

Context: `sei-tendermint/crypto/tmhash/hash.go:20` (changes signature or replay validation logic)

Before
```go
return h[:]
}

//-------------------------------------------------------------

const (
	TruncatedSize = 20
)
```
After
```go
return h[:]
}
```

## Snippet 3

Context: `sei-tendermint/crypto/ed25519/ed25519.go:153` (changes signature or replay validation logic)

Before
```go
// It is secure to use the same secret key for signing with both Sign() and SignWithTag() [https://datatracker.ietf.org/doc/html/rfc8032#section-8.6].
func (k SecretKey) SignWithTag(tag Tag, msg []byte) Signature {
	opts := &ed25519.Options{Context: tag.tag}
	// Returns no error if opts.Context is of correct size.
	sig := utils.OrPanic1(ed25519.PrivateKey((*k.key)[:]).Sign(nil, msg, opts))
	return Signature{sig: [ed25519.SignatureSize]byte(sig)}
}
```
After
```go
// It is secure to use the same secret key for signing with both Sign() and SignWithTag() [https://datatracker.ietf.org/doc/html/rfc8032#section-8.6].
func (k SecretKey) SignWithTag(tag Tag, msg []byte) Signature {
	defer runtime.KeepAlive(k)
	opts := &ed25519.Options{Context: tag.tag}
	// Returns no error if opts.Context is of correct size.
	sig := utils.OrPanic1(ed25519.PrivateKey((*k.key())[:]).Sign(nil, msg, opts))
	return Signature{sig: [ed25519.SignatureSize]byte(sig)}
}
```

## Snippet 4

Context: `sei-tendermint/crypto/ed25519/ed25519.go:39` (changes signature or replay validation logic)

Before
```go
// SecretKey represents a secret key in the Ed25519 signature scheme.
type SecretKey struct {
	// This is a pointer to avoid copying the secret all over the memory.
	// This is a pointer to pointer, so that runtime.AddCleanup can actually work:
	// Cleanup requires the referenced pointer to be unreachable, even from
	// the cleanup function.
	key **[ed25519.PrivateKeySize]byte
	// Comparing the secrets is not allowed.
```
After
```go
// SecretKey represents a secret key in the Ed25519 signature scheme.
type SecretKey struct {
	// When using the key make sure to use runtime.KeepAlive, so that key is not zeroized midway.
	// This is a pointer to avoid copying the secret to stack when used.
	// This is a pointer to pointer, so that runtime.AddCleanup can actually work:
	// AddCleanup requires the referenced pointer to be unreachable, even from the cleanup function.
	// This is a closure returning pointer to pointer , so that secret is not extractable via golang reflection,
	// because reflection is not able to call closures stored in private fields of types in other modules.
```

# Fix Pattern

Harden cryptographic secret lifecycle handling by making runtime reachability explicit, avoiding cleanup callbacks that retain the object being cleaned, hiding raw secret pointers behind a private accessor, and keeping key objects alive until signing completes.

## How It Was Fixed

The Ed25519 code now uses a Secret alias for the private-key byte array, passes the raw secret pointer into runtime.AddCleanup instead of capturing it, stores the key accessor as a private closure, and adds runtime.KeepAlive in SignWithTag. The signing code was updated to dereference through k.key().

# Why It Matters

1. Affects Ed25519 private-key storage and signing code.

2. Improves alignment with Go runtime cleanup reachability rules.

3. Reduces exposure of raw secret pointers through the object representation.

4. Prevents premature cleanup/zeroization during SignWithTag.

5. Does not prove remote exploitation, key theft, signature forgery, or consensus failure.

# Evidence Notes

Primary evidence is from sei-tendermint/crypto/ed25519/ed25519.go: SecretKey representation changed, SecretKeyFromSecretBytes changed AddCleanup usage, and SignWithTag added runtime.KeepAlive. The reflection-exposure claim is supported only by the new code comment, not by a demonstrated exploit. The tmhash change lacks enough evidence to classify as security-relevant. Protocol security invariant: Ed25519 secret keys should remain confidential in process memory, should not be unnecessarily copied or exposed through ordinary representation/reflection paths, should stay live for the duration of signing, and should be zeroized only after they become unreachable. Verification notes: No remote exploit path is proven by the patch evidence. No signature forgery, verification bypass, or consensus safety violation is shown. No evidence shows private keys were exposed outside process memory by an attacker-controlled input. No evidence shows the tmhash changes fix a security bug rather than removing unused or obsolete API surface. This should be described as secret-management hardening unless additional advisory context confirms an exploitable vulnerability. No exploit path is shown in the supplied evidence. No test evidence demonstrates prior key leakage or premature zeroization. No evidence supports signature forgery, verification bypass, or consensus impact. Classify as security hardening, not a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `secret-key-lifecycle-hardening`
Final impact type: `secret-key-exposure-risk-reduction, memory-lifecycle-hardening`
Final tags: `cryptography, ed25519, secret-key-lifecycle, memory-zeroization, runtime-keepalive, security-hardening`

The supplied patch evidence supports retaining this as security hardening for Ed25519 secret-key lifecycle handling. The changes make cleanup reachability explicit, avoid closing over the secret in the cleanup callback, keep the key alive during signing, and hide the raw secret pointer behind a private closure. The evidence does not prove an exploitable vulnerability, key theft, signature forgery, verification bypass, or consensus impact, so it should not be classified as a security-fix.

## Security Evidence

1. SecretKeyFromSecretBytes changes runtime.AddCleanup usage so the cleanup callback receives the secret pointer rather than capturing raw.
2. The cleanup comment explicitly says the secret is zeroed to avoid leaking it.
3. SecretKey representation changes from a direct pointer-to-pointer field to a private closure returning the pointer, with comments tying this to reflection-based secret extraction resistance.
4. SignWithTag adds defer runtime.KeepAlive(k), matching the new comment that keys must not be zeroized midway through use.
5. The affected code is Ed25519 private-key storage and signing logic, a security-sensitive cryptographic path.

## Missing Evidence

1. No advisory, CVE, exploit scenario, or attacker-controlled path is supplied.
2. No evidence shows actual private-key disclosure outside process memory.
3. No evidence shows signature forgery, verification bypass, replay, or consensus safety impact.
4. No test evidence demonstrates the prior premature zeroization or leakage behavior.
5. The tmhash removal is not tied to a concrete security invariant in the supplied evidence.

## Claim Boundaries

1. Classify as security-hardening, not a proven vulnerability fix.
2. Limit the finding to Ed25519 secret-key lifecycle and in-memory exposure hardening.
3. Do not claim remote exploitability or direct key exfiltration from the patch alone.
4. Do not treat the tmhash hunk as security-relevant without additional evidence.
5. Do not claim consensus, replay, or signature-validation impact from the supplied evidence.
