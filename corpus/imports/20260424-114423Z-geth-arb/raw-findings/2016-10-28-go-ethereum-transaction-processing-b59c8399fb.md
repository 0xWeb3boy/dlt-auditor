---
case_id: case_20161028_b59c8399fb
project: go-ethereum
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
bug_class: signing-api-domain-separation
impact_type:
  - signature-misuse-risk
  - private-key-exposure-risk
tags:
  - account-rpc-signing
  - eth-sign
  - message-signing
  - domain-separation
  - ecdsa
  - cryptographic-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is account signing API hardening, not transaction-processing replay protection. The commit changes eth_sign semantics so arbitrary messages are prefixed with the Ethereum Signed Message string, hashed with keccak256, and then signed. The strongest security evidence is the added crypto.Sign documentation warning that raw ECDSA signing is susceptible to chosen-plaintext attacks when adversaries can choose the hash, plus the API-level change away from raw signing behavior.

## Observed Patch Facts

1. In `crypto/crypto.go`, the patch replaces `func Sign(hash []byte, prv *ecdsa.PrivateKey) (sig []byte, err error) {` with `// Sign calculates an ECDSA signature.`.

2. In `accounts/account_manager.go`, the patch replaces `// SignWithPassphrase signs hash if the private key matching the given address can be` with `// SignEthereum calculates a ECDSA signature for the given hash.`.

3. In `crypto/crypto_test.go`, the patch replaces `func TestSign(t *testing.T) {` with `func testSign(signfn func([]byte, *ecdsa.PrivateKey) ([]byte, error), t *testing.T) {`.

4. In `crypto/crypto.go`, the patch replaces `func Ecrecover(hash, sig []byte) ([]byte, error) {` with `// Ecrecover returns the public key for the private key that was used to`.

## Project Context

Historical context from `accounts/accounts_test.go`, `crypto/encrypt_decrypt_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `accounts/abi/type.go`, `accounts/abi/bind/auth.go`. The strongest project-level identifiers around this patch are `hash`, `byte`, `signature`, and `Ethereum`.

## Before/After Behavior

Before the patch, the provided evidence shows accounts.Manager.Sign signing a supplied 32-byte hash through crypto.Sign, and crypto.Sign only enforcing hash length. The commit message indicates eth_sign previously did not apply the Ethereum Signed Message prefix and keccak256 hashing to arbitrary messages. After the patch, eth_sign signs a keccak256 hash of a prefixed message, crypto.Sign is documented as a raw primitive unsafe for adversary-chosen hashes unless callers hash first, SignEthereum is added as a distinct Ethereum-format signing path, and recovery-ID handling is clarified for raw versus Ethereum-style signatures.

# Root Cause

The supported root cause is that the account/RPC signing boundary exposed or relied on raw ECDSA signing semantics for caller-supplied signing input without enforcing a message-hashing and domain-separation step at that API boundary. The evidence does not prove private-key leakage, transaction replay, or that all raw crypto.Sign callers were exploitable.

## Walkthrough

1. A caller reaches the account signing surface through eth_sign, with personal_sign added as a related API in the same commit.

2. The pre-patch lower-level path shown in the evidence signs a supplied 32-byte hash through accounts.Manager.Sign and crypto.Sign.

3. The patch adds documentation to crypto.Sign warning that raw signing is susceptible to chosen-plaintext attacks if the hash can be chosen by an adversary.

4. The eth_sign behavior is changed so arbitrary messages are prefixed with the Ethereum Signed Message string and message length, then hashed with keccak256 before signing.

5. The account manager gains a separate SignEthereum path for Ethereum-formatted signatures while raw crypto.Sign remains a lower-level primitive with explicit caller obligations.

6. Tests and comments are updated to account for recovery-ID differences between raw secp256k1 signatures and Ethereum-style signatures.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| internal/ethapi/api.go | 1 | JSON-RPC eth_sign/personal_sign API behavior changed to hash prefixed messages before signing |
| accounts/account_manager.go | 143 | account manager signing boundary, separating raw Sign from Ethereum-formatted SignEthereum |
| crypto/crypto.go | 199 | low-level ECDSA signing primitive documented as unsafe for adversary-chosen hashes unless prehashed |
| crypto/crypto.go | 79 | signature recovery primitive documents Ethereum recovery-id offset handling |
| crypto/crypto_test.go | 81 | tests updated to cover both raw and Ethereum-style signature recovery-id forms |

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

Enforce hashing and domain separation at the signing API boundary for arbitrary messages, while keeping raw ECDSA signing as a lower-level primitive with explicit warnings and separate Ethereum-format helpers.

## How It Was Fixed

The patch changes eth_sign to prefix messages with the standard Ethereum Signed Message string and length, hash the prefixed data with keccak256, and sign that hash. It adds personal_sign with similar signing semantics plus password-based scoped unlocking, adds or exposes SignEthereum for Ethereum-format signatures, documents raw crypto.Sign risks for adversary-chosen hashes, clarifies recovery-ID offset handling, and updates signing tests accordingly.

# Why It Matters

1. Prehashing and prefixing provide domain separation for account-message signatures.

2. Raw ECDSA signing over adversary-controlled input is explicitly identified as dangerous by the patched code comments.

3. The evidence supports signing API hardening, not a proven transaction replay or validation bug.

4. Separating raw and Ethereum-formatted signatures reduces ambiguity for callers.

# Evidence Notes

Grounded evidence comes from the commit message and snippets in crypto/crypto.go, accounts/account_manager.go, crypto/crypto_test.go, and Ecrecover comments. The commit message supplies the eth_sign before/after semantics. The crypto.Sign comment supplies the security rationale around chosen-plaintext risk. The evidence does not establish a concrete exploit, private-key disclosure in practice, transaction-processing impact, or unsafe behavior in every raw signing caller. Protocol security invariant: Account signing APIs that accept caller-controlled messages should not expose raw ECDSA signing without hashing and domain separation. Arbitrary messages should be prefixed and hashed before signing so the signature is bound to an Ethereum signed-message context rather than treated as an unstructured raw signing input. Verification notes: No concrete private-key leakage exploit is demonstrated by the patch evidence. No transaction validation or state-transition replay bug is shown. No remote attacker capability is proven beyond influence over messages submitted to signing APIs. The evidence does not show that all callers of raw crypto.Sign were unsafe. The added personal_sign/personal_recover APIs are partly API expansion, not solely a vulnerability fix. Downgraded subsystem from transaction-processing to account-rpc-signing. Rejected transaction replay and state-transition claims as unsupported. Kept classification as likely security hardening because the patch itself documents chosen-input signing risk and changes eth_sign to hash a domain-separated message. Confidence remains medium because the provided evidence lacks an end-to-end exploit or caller threat model beyond adversary-controlled signing input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signing-api-domain-separation`
Final impact type: `signature-misuse-risk, private-key-exposure-risk`
Final tags: `account-rpc-signing, eth-sign, message-signing, domain-separation, ecdsa, cryptographic-hardening`

The supplied evidence supports keeping this as security hardening: the commit changes eth_sign from raw hash-signing semantics to prefixed-and-hashed arbitrary message signing, and the patch explicitly documents raw ECDSA signing as susceptible to chosen-plaintext attacks when adversaries can choose the input. The evidence does not prove a concrete exploit, transaction replay flaw, or transaction-processing vulnerability, so the corpus entry should be narrowed away from replay/transaction claims.

## Security Evidence

1. Commit message states eth_sign now prefixes arbitrary messages with the Ethereum Signed Message string, hashes with keccak256, then signs.
2. crypto.Sign gains an explicit warning that raw ECDSA signing can leak private-key information under chosen-plaintext input.
3. accounts.Manager keeps raw Sign separate and adds SignEthereum for Ethereum-format signatures.
4. Tests and comments distinguish raw secp256k1 signatures from Ethereum-style recovery-id handling.

## Missing Evidence

1. No end-to-end exploit or demonstrated private-key recovery is shown.
2. No concrete remote attacker capability is established beyond influence over signing input.
3. No transaction validation, state transition, or replay bug is evidenced by the provided snippets.
4. The exact internal/ethapi implementation diff is described by the commit message but not shown in the evidence snippets.

## Claim Boundaries

1. Validate as signing API hardening, not a confirmed vulnerability fix.
2. Do not claim proven transaction replay or request forgery impact.
3. Do not claim all crypto.Sign callers were exploitable.
4. Do not claim demonstrated private-key disclosure in practice.
