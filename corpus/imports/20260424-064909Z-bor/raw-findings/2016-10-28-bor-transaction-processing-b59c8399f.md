---
case_id: case_20161028_b59c8399f
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2016-10-28
source_refs:
  - git:b59c8399fbe42390a3d41e945d03b1f21c1a9b8d
  - "crypto/crypto.go:199"
  - "accounts/account_manager.go:151"
  - "crypto/crypto_test.go:81"
  - "crypto/crypto.go:79"
bug_class: message-signing-domain-separation
impact_type:
  - unsafe-message-signing
tags:
  - cryptography
  - rpc-signing
  - eth-sign
  - message-signing
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a security hardening change in the RPC signing path: `eth_sign` was changed to sign a prefixed-and-hashed message instead of a raw caller-provided digest, and the codebase now separates raw signing from Ethereum-formatted signing. The evidence does not support stronger claims about transaction replay handling, nonce validation, or a demonstrated private-key extraction exploit.

## Observed Patch Facts

1. In `crypto/crypto.go`, the patch replaces `func Sign(hash []byte, prv *ecdsa.PrivateKey) (sig []byte, err error) {` with `// Sign calculates an ECDSA signature.`.

2. In `accounts/account_manager.go`, the patch replaces `// SignWithPassphrase signs hash if the private key matching the given address can be` with `// SignEthereum calculates a ECDSA signature for the given hash.`.

3. In `crypto/crypto_test.go`, the patch replaces `func TestSign(t *testing.T) {` with `func testSign(signfn func([]byte, *ecdsa.PrivateKey) ([]byte, error), t *testing.T) {`.

4. In `crypto/crypto.go`, the patch replaces `func Ecrecover(hash, sig []byte) ([]byte, error) {` with `// Ecrecover returns the public key for the private key that was used to`.

## Project Context

Historical context from `accounts/accounts_test.go`, `crypto/encrypt_decrypt_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `accounts/abi/type.go`, `accounts/abi/bind/auth.go`. The strongest project-level identifiers around this patch are `hash`, `byte`, `signature`, and `Ethereum`.

## Before/After Behavior

Before the change, the account-manager signing path shown in evidence returned `crypto.Sign(hash, unlockedKey.PrivateKey)`, i.e. a raw signature over a provided 32-byte hash. After the change, the code adds a distinct `SignEthereum` path, documents that raw `Sign` is unsafe for adversary-chosen inputs unless callers hash first, and the commit message says `eth_sign` now prefixes arbitrary messages with the standard Ethereum signed-message prefix, hashes them with `keccak256`, and signs that derived hash.

# Root Cause

The RPC/account signing boundary was too close to the low-level raw signing primitive, so user-supplied signing requests were not clearly forced into the Ethereum message-signing domain before signature generation.

## Walkthrough

1. `accounts/account_manager.go` shows a pre-existing path that signs a provided hash via `crypto.Sign(hash, unlockedKey.PrivateKey)`.

2. `crypto/crypto.go` adds an explicit warning that raw `Sign` is susceptible to chosen-plaintext attacks and that callers should hash inputs first.

3. The same area documents that raw `Sign` is not Ethereum compliant and points callers to `SignEthereum` for Ethereum-format signatures.

4. `accounts/account_manager.go` adds `SignEthereum(addr, hash)` as a separate account-manager entry point that calls `crypto.SignEthereum`.

5. `crypto/crypto.go` adds documentation that Ethereum signatures use a recovery-id offset of 27, clarifying the format distinction.

6. `crypto/crypto_test.go` is updated to normalize `sig[64]` when it is `27` or `28`, matching Ethereum-style signatures.

7. The commit message ties these code changes to RPC behavior by stating that `eth_sign` now prefixes and hashes messages before signing, and that `personal_sign` and `personal_recover` are added.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crypto/crypto.go | 199 | low-level ECDSA signing primitive; patch documents that signing chosen plaintext/raw hashes is unsafe unless callers hash first |
| accounts/account_manager.go | 143 | account manager signing boundary; separates generic raw signing from Ethereum-formatted signing for RPC-facing callers |
| crypto/crypto.go | 74 | signature recovery helper; clarifies Ethereum-specific recovery-id handling used by the message-signing flow |

## Code Snippets

## Snippet 1

Context: `crypto/crypto.go:199` (changes signature or replay validation logic)

Before
```go
}

func Sign(hash []byte, prv *ecdsa.PrivateKey) (sig []byte, err error) {
	if len(hash) != 32 {
		return nil, fmt.Errorf("hash is required to be exactly 32 bytes (%d)", len(hash))
	}

	seckey := common.LeftPadBytes(prv.D.Bytes(), prv.Params().BitSize/8)
```
After
```go
}

// Sign calculates an ECDSA signature.
// This function is susceptible to choosen plaintext attacks that can leak
// information about the private key that is used for signing. Callers must
// be aware that the given hash cannot be choosen by an adversery. Common
// solution is to hash any input before calculating the signature.
//
```

## Snippet 2

Context: `accounts/account_manager.go:151` (changes signature or replay validation logic)

Before
```go
}

// SignWithPassphrase signs hash if the private key matching the given address can be
// decrypted with the given passphrase.
func (am *Manager) SignWithPassphrase(addr common.Address, passphrase string, hash []byte) (signature []byte, err error) {
	_, key, err := am.getDecryptedKey(Account{Address: addr}, passphrase)
```
After
```go
}

// SignEthereum calculates a ECDSA signature for the given hash.
// The signature has the format as described in the Ethereum yellow paper.
func (am *Manager) SignEthereum(addr common.Address, hash []byte) ([]byte, error) {
	am.mu.RLock()
	defer am.mu.RUnlock()
	unlockedKey, found := am.unlocked[addr]
```

## Snippet 3

Context: `crypto/crypto_test.go:81` (changes signature or replay validation logic)

Before
```go
}

func TestSign(t *testing.T) {
	key, _ := HexToECDSA(testPrivHex)
	addr := common.HexToAddress(testAddrHex)

	msg := Keccak256([]byte("foo"))
	sig, err := Sign(msg, key)
```
After
```go
}

func testSign(signfn func([]byte, *ecdsa.PrivateKey) ([]byte, error), t *testing.T) {
	key, _ := HexToECDSA(testPrivHex)
	addr := common.HexToAddress(testAddrHex)

	msg := Keccak256([]byte("foo"))
	sig, err := signfn(msg, key)
```

## Snippet 4

Context: `crypto/crypto.go:79` (changes a sensitive control or state-update path)

Before
```go
}

func Ecrecover(hash, sig []byte) ([]byte, error) {
	return secp256k1.RecoverPubkey(hash, sig)
```
After
```go
}

// Ecrecover returns the public key for the private key that was used to
// calculate the signature.
//
// Note: secp256k1 expects the recover id to be either 0, 1. Ethereum
// signatures have a recover id with an offset of 27. Callers must take
// this into account and if "recovering" from an Ethereum signature adjust.
```

# Fix Pattern

Separate low-level cryptographic primitives from RPC-facing signing APIs, and enforce message-domain separation by prefixing and hashing user-supplied messages before signing.

## How It Was Fixed

The patch keeps raw `crypto.Sign` as a low-level primitive but adds warnings about its safety assumptions, introduces an Ethereum-specific signing path (`SignEthereum`), clarifies Ethereum recovery-id handling, and updates tests for Ethereum-formatted signatures. Per the commit message, the externally visible hardening is that `eth_sign` now signs a prefixed-and-hashed message instead of a raw provided digest.

# Why It Matters

1. It narrows the chance that RPC callers obtain signatures over raw digests outside the intended Ethereum message-signing domain.

2. It makes the boundary between generic signing and Ethereum-formatted signing explicit.

3. It reduces ambiguity around Ethereum signature formatting and recovery semantics.

# Evidence Notes

The strongest evidence is the commit message plus the added `crypto.Sign` warning about chosen-input signing, the new `SignEthereum` account-manager path, and the test updates for Ethereum-style recovery IDs. The evidence supports classifying this as security hardening of message-signing semantics. It does not show transaction-validation changes, nonce/replay enforcement, or proof of a concrete exploit against prior releases. Protocol security invariant: An RPC message-signing endpoint should not expose raw secp256k1 signing over attacker-chosen inputs without Ethereum-specific message prefixing and hashing. User-facing message signatures should be bound to the Ethereum signed-message domain, while low-level raw signing remains a separate primitive with stricter safety assumptions. Verification notes: The patch does not prove a remotely exploitable private-key extraction attack occurred before the change. The patch does not show on-chain transaction validation or nonce/replay rules being modified. The patch does not prove prior `eth_sign` outputs were directly usable as valid transactions or contract authorizations. Part of the commit is API expansion and compatibility change (`personal_sign`, `personal_recover`), not just a narrowly scoped vulnerability fix. The commit message explicitly states that `eth_sign` changed to prefix and hash messages before signing. The added `crypto.Sign` comment explicitly warns about chosen-plaintext risk for adversary-chosen inputs. `accounts/account_manager.go` shows a new Ethereum-specific signing entry point separate from raw signing. The test changes confirm handling differences between raw signatures and Ethereum-style signatures. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `message-signing-domain-separation`
Final impact type: `unsafe-message-signing`
Final tags: `cryptography, rpc-signing, eth-sign, message-signing`

The supplied evidence supports keeping this as a security-hardening case. The commit message explicitly says `eth_sign` stopped signing raw caller-provided digests and now prefixes and hashes messages before signing, and the patch evidence aligns with that by separating raw signing from Ethereum-specific signing and adding warnings that raw signing of adversary-chosen input is unsafe. That is a clear tightening of a security-sensitive signing boundary, but the patch alone does not prove a concrete exploitable vulnerability or replay bug, so this should remain hardening rather than a confirmed security-fix.

## Security Evidence

1. Commit metadata states `eth_sign` was changed to prefix and hash messages before signing.
2. `crypto.Sign` is newly documented as unsafe for adversary-chosen inputs, indicating a security-sensitive risk in raw signing.
3. `accounts/account_manager.go` adds a distinct `SignEthereum` path, separating raw signing from Ethereum-formatted signing.
4. Test updates account for Ethereum-specific signature formatting, consistent with a hardened signing API boundary.

## Missing Evidence

1. No direct diff excerpt is provided for the RPC handler that performs the prefix-and-hash step.
2. No proof that the prior behavior enabled a concrete exploit in practice.
3. No evidence of transaction nonce or replay-validation changes.

## Claim Boundaries

1. The evidence supports hardening of RPC/message-signing semantics, not a demonstrated exploit fix.
2. The evidence does not support the stronger original `replay-or-signature-validation` classification.
3. The patch should not be cited as proof of transaction replay protection or private-key extraction prevention in deployed systems.
