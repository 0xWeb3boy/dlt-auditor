---
case_id: case_20191113_75e2e189e
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: high
date: 2019-11-13
source_refs:
  - git:75e2e189ea21bc57db6493b382f6c71b4a551ac1
  - "go/common/crypto/signature/signature.go:152"
  - "go/common/crypto/signature/signature.go:229"
  - "go/common/crypto/signature/signature.go:136"
  - "go/registry/api/api.go:273"
bug_class: panic-on-malformed-input
impact_type:
  - denial-of-service
confidence: medium
tags:
  - input-validation
  - malformed-input
  - panic
  - public-key
  - registry
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied changes are consistent with a denial-of-service fix caused by malformed or nil public keys. Before the patch, zero-length input could successfully unmarshal into a nil `PublicKey`, and later helper code could panic when converting an invalid-length key to a map key during registry entity validation. After the patch, malformed keys are rejected at unmarshal time, downstream conversion no longer panics on malformed keys, and registry validation rejects malformed node IDs before duplicate-check processing.

## Observed Patch Facts

1. In `go/common/crypto/signature/signature.go`, the patch replaces `// HACK: go-codec apparently was skipping calls to UnmarshalBinary` with `if len(data) != PublicKeySize {`.

2. In `go/common/crypto/signature/signature.go`, the patch replaces `if len(k) != PublicKeySize {` with `// For malformed public keys, use an all-zero MapKey to avoid`.

3. In `go/common/crypto/signature/signature.go`, the patch replaces `data = append([]byte{}, k[:]...)` with `// Since UnmarshalBinary will fail for incorrectly encoded keys,`.

4. In `go/registry/api/api.go`, the patch replaces `mk := v.ToMapKey()` with `if !v.IsValid() {`.

## Project Context

The changed code sits primarily in `go/common/crypto/signature`, `go/common/crypto`, `go/registry/api`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `go/registry/api/runtime.go`, `go/common/crypto/signature/signer.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/registry/api/runtime.go`, `go/common/crypto/signature/signers/file/file_signer.go`. The strongest project-level identifiers around this patch are `keys`, `malformed`, `data`, and `PublicKeySize`. Nearby tests or test-like files include `go/registry/tests/tester.go`.

## Before/After Behavior

Before the patch, `PublicKey.UnmarshalBinary` accepted `len(data) == 0` and produced a nil key, while `ToMapKey` panicked on invalid key length and `VerifyRegisterEntityArgs` called `ToMapKey()` on node IDs before checking structural validity. After the patch, `UnmarshalBinary` requires exact key length, `ToMapKey` avoids panic by returning an all-zero map key for malformed inputs, `MarshalBinary` normalizes malformed keys to an all-zero blacklisted key, and registry validation rejects malformed node IDs up front.

# Root Cause

Malformed public keys were handled inconsistently across the code path: deserialization allowed a nil/zero-length key as success, but later identity-conversion logic assumed exact key length and could panic when given that malformed value.

## Walkthrough

1. `PublicKey.UnmarshalBinary` previously special-cased zero-length input, setting the key to `nil` and returning success.

2. A nil or otherwise malformed `PublicKey` does not satisfy the exact-size assumption used elsewhere in the signature code.

3. `PublicKey.ToMapKey` previously enforced that assumption with a panic on invalid key length.

4. `VerifyRegisterEntityArgs` iterated `ent.Nodes` and converted each node ID with `ToMapKey()` for duplicate detection before rejecting malformed IDs.

5. The patch removes the zero-length success case from `UnmarshalBinary`, so malformed binary encodings fail immediately.

6. The patch also makes later handling safer by avoiding panic in `ToMapKey` and by explicitly rejecting malformed node IDs in registry validation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/common/crypto/signature/signature.go | 137 | Normalizes malformed public keys during binary marshaling to an all-zero blacklisted key instead of emitting arbitrary invalid-length data. |
| go/common/crypto/signature/signature.go | 152 | Tightens `PublicKey.UnmarshalBinary` so zero-length/nil encodings are rejected unless the input is exactly `PublicKeySize`. |
| go/common/crypto/signature/signature.go | 229 | Removes panic-on-invalid-length behavior from `ToMapKey`, returning an all-zero map key for malformed public keys. |
| go/registry/api/api.go | 273 | Rejects malformed node IDs during `VerifyRegisterEntityArgs` before duplicate detection converts them to map keys. |

## Code Snippets

## Snippet 1

Context: `go/common/crypto/signature/signature.go:152` (changes a sensitive control or state-update path)

Before
```go
// UnmarshalBinary decodes a binary marshaled public key.
func (k *PublicKey) UnmarshalBinary(data []byte) error {
	// HACK: go-codec apparently was skipping calls to UnmarshalBinary
	// or something, while the new library will always call it.
	//
	// We have approximately 3 million different places where we use
	// the default value for public keys, so special case it.
	if len(data) == 0 {
```
After
```go
// UnmarshalBinary decodes a binary marshaled public key.
func (k *PublicKey) UnmarshalBinary(data []byte) error {
	if len(data) != PublicKeySize {
		return ErrMalformedPublicKey
```

## Snippet 2

Context: `go/common/crypto/signature/signature.go:229` (changes signature or replay validation logic)

Before
```go
// ToMapKey returns a fixed-sized representation of the public key.
func (k PublicKey) ToMapKey() MapKey {
	if len(k) != PublicKeySize {
		panic("signature: public key invalid size for ID")
	}

	var mk MapKey
	copy(mk[:], k)
```
After
```go
// ToMapKey returns a fixed-sized representation of the public key.
func (k PublicKey) ToMapKey() MapKey {
	var mk MapKey
	// For malformed public keys, use an all-zero MapKey to avoid
	// panics on conversions from malformed keys.
	if len(k) == PublicKeySize {
		copy(mk[:], k)
	}
```

## Snippet 3

Context: `go/common/crypto/signature/signature.go:136` (changes a sensitive control or state-update path)

Before
```go
// MarshalBinary encodes a public key into binary form.
func (k PublicKey) MarshalBinary() (data []byte, err error) {
	data = append([]byte{}, k[:]...)
	return
```
After
```go
// MarshalBinary encodes a public key into binary form.
func (k PublicKey) MarshalBinary() (data []byte, err error) {
	// Since UnmarshalBinary will fail for incorrectly encoded keys,
	// replace any malformed keys with an all-zero key. Note that
	// such a key is blacklisted and will always be invalid for
	// verification (but not malformed).
	if len(k) != PublicKeySize {
		var zeroKey [PublicKeySize]byte
```

## Snippet 4

Context: `go/registry/api/api.go:273` (changes a sensitive control or state-update path)

Before
```go
nodesMap := make(map[signature.MapKey]bool)
	for _, v := range ent.Nodes {
		mk := v.ToMapKey()
		if nodesMap[mk] {
```
After
```go
nodesMap := make(map[signature.MapKey]bool)
	for _, v := range ent.Nodes {
		if !v.IsValid() {
			logger.Error("RegisterEntity: malformed node id",
				"entity", ent,
			)
			return nil, ErrInvalidArgument
		}
```

# Fix Pattern

Tighten validation at the deserialization boundary and convert downstream panic-prone helper behavior into safe invalid-value handling, with explicit validity checks before malformed identifiers reach deduplication or indexing logic.

## How It Was Fixed

The patch makes `PublicKey.UnmarshalBinary` fail unless the input length is exactly `PublicKeySize`. It changes `ToMapKey` to stop panicking on malformed keys, changes `MarshalBinary` to serialize malformed keys as an all-zero key documented as blacklisted/invalid, and updates `VerifyRegisterEntityArgs` to reject malformed node IDs before duplicate detection uses them.

# Why It Matters

1. Malformed key encodings are no longer accepted as ordinary decoded public keys.

2. Registry validation now rejects malformed node IDs before they reach panic-prone conversion logic.

3. The visible impact supported by the diff is denial-of-service hardening, not signature bypass or privilege escalation.

# Evidence Notes

Direct evidence shows three linked changes: removal of successful nil-key unmarshaling, removal of panic-on-malformed-key conversion in `ToMapKey` with an explicit comment about avoiding panics, and addition of `IsValid()` checks before registry duplicate detection processes node IDs. The provided material supports a malformed-input panic thesis; it does not prove broader impact such as consensus failure or authentication bypass. Protocol security invariant: Public keys used as identities must decode to exactly `PublicKeySize` bytes, and malformed keys must be rejected or handled as invalid values without panicking during later map-key conversion or registry validation. Verification notes: The patch does not prove a remotely reachable exploit path in every deployment; it shows a panic-prone malformed-input path. The patch does not show signature forgery, authentication bypass, or privilege escalation. The patch does not prove consensus corruption; the visible effect is safer rejection of malformed keys. The all-zero fallback is documented as blacklisted/invalid, so the patch does not indicate acceptance of malformed identities as valid ones. No test hunks were provided, so regression coverage cannot be evaluated from the supplied evidence. The code comments explicitly reference avoiding panics on malformed keys, which supports the panic/DoS interpretation. Reachability through a specific external endpoint is implied by the registry validation path but not fully demonstrated in the supplied excerpts. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `panic-on-malformed-input`
Final impact type: `denial-of-service`
Final confidence: `medium`
Final tags: `input-validation, malformed-input, panic, public-key, registry`

The patch clearly hardens a security-sensitive path against malformed public-key inputs by rejecting invalid encodings earlier, preventing panic-prone key conversion, and adding explicit validity checks before registry processing. That supports a denial-of-service hardening interpretation. However, the supplied excerpts do not fully prove attacker reachability or an observed exploitable crash in production, so this is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `UnmarshalBinary` stops accepting zero-length public keys and returns `ErrMalformedPublicKey` unless the size is exact.
2. `ToMapKey` no longer panics on malformed key length and instead returns a zero-value map key, with a comment explicitly saying this avoids panics.
3. `VerifyRegisterEntityArgs` now rejects malformed node IDs with `IsValid()` before duplicate-detection logic uses them.
4. The code comments and control-flow changes consistently treat malformed key material as invalid and non-verifiable.

## Missing Evidence

1. No provided test diff demonstrates a previously crashing regression case.
2. No excerpt shows a concrete remote attack path from an untrusted endpoint to the panic condition.
3. No evidence shows actual exploitation, impact scope, or whether panic would terminate a critical service.

## Claim Boundaries

1. The patch supports malformed-input DoS hardening, not signature forgery or authentication bypass.
2. The evidence does not prove consensus compromise, privilege escalation, or confidentiality impact.
3. The evidence is sufficient to classify as security-relevant hardening, but not to prove a concrete exploitable vulnerability.
