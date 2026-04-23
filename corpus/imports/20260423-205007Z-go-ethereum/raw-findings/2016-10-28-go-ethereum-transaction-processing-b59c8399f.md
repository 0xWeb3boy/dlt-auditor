---
case_id: case_20161028_b59c8399f
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
bug_class: signature-domain-separation
impact_type:
  - signature-misuse-risk
  - private-key-exposure-risk
tags:
  - rpc-account-signing
  - eth-sign
  - ecdsa
  - signature-domain-separation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best classified as security hardening for go-ethereum RPC/account signing. The commit states that eth_sign was changed to sign keccak256 of an Ethereum Signed Message-prefixed payload, and the crypto.Sign comments warn that raw signing is unsafe when the input can be chosen by an adversary. The evidence supports a signature-domain-separation hardening claim, but not a proven exploit or transaction-validation vulnerability.

## Observed Patch Facts

1. In `crypto/crypto.go`, the patch replaces `func Sign(hash []byte, prv *ecdsa.PrivateKey) (sig []byte, err error) {` with `// Sign calculates an ECDSA signature.`.

2. In `accounts/account_manager.go`, the patch replaces `// SignWithPassphrase signs hash if the private key matching the given address can be` with `// SignEthereum calculates a ECDSA signature for the given hash.`.

3. In `crypto/crypto_test.go`, the patch replaces `func TestSign(t *testing.T) {` with `func testSign(signfn func([]byte, *ecdsa.PrivateKey) ([]byte, error), t *testing.T) {`.

4. In `crypto/crypto.go`, the patch replaces `func Ecrecover(hash, sig []byte) ([]byte, error) {` with `// Ecrecover returns the public key for the private key that was used to`.

## Project Context

Historical context from `accounts/accounts_test.go`, `crypto/encrypt_decrypt_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `accounts/abi/type.go`, `accounts/abi/bind/auth.go`. The strongest project-level identifiers around this patch are `hash`, `byte`, `signature`, and `Ethereum`.

## Before/After Behavior

Before the change, the provided evidence shows a low-level crypto.Sign(hash []byte, prv *ecdsa.PrivateKey) primitive for signing a 32-byte hash, and the commit body indicates eth_sign previously did not apply the new Ethereum Signed Message prefixing semantics. After the change, the commit body says eth_sign accepts an arbitrary message, prefixes it with the Ethereum Signed Message string and message length, hashes that data with keccak256, and signs the digest. The patch also adds personal_sign and personal_recover, documents raw signing risks, and clarifies Ethereum recovery-id handling.

# Root Cause

The supported root cause is that account-signing RPC behavior was tied too closely to raw ECDSA hash-signing semantics. Without explicit message-prefix domain separation before signing, caller-supplied signing input could be used in a less clearly scoped signature context. The evidence does not establish transaction replay, nonce handling failure, or a concrete private-key leakage exploit.

## Walkthrough

1. crypto.Sign remains a low-level primitive that signs a 32-byte hash with an ECDSA private key.

2. The patch adds comments warning that raw signing is susceptible to chosen-input risks and that callers should hash input before signing.

3. The commit body states that eth_sign now prefixes arbitrary messages with the Ethereum Signed Message string and message length before hashing and signing.

4. personal_sign is added with the same signed-message semantics plus passphrase-based temporary unlock.

5. personal_recover is added to recover the address associated with a signed message.

6. The account manager separates raw signing from Ethereum-format signature handling via SignEthereum.

7. Recovery-id comments and tests are adjusted to distinguish raw secp256k1 recovery IDs from Ethereum signature recovery IDs.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crypto/crypto.go | 199 | low-level ECDSA signing primitive now explicitly documents chosen-plaintext risk and distinguishes raw signatures from Ethereum-format signatures |
| accounts/account_manager.go | 143 | account manager path for signing with unlocked account, separating raw Sign from Ethereum-compliant SignEthereum |
| crypto/crypto.go | 79 | signature recovery helper documents Ethereum recovery-id offset handling for recovered signatures |
| crypto/crypto_test.go | 81 | tests adjusted to cover both raw and Ethereum-style signature recovery-id formats |

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

Apply signature domain separation at the RPC/account-signing boundary by prefixing arbitrary messages, hashing the prefixed payload, and then invoking the ECDSA signing primitive; keep raw hash signing as an internal or trusted low-level operation with explicit warnings.

## How It Was Fixed

The commit changes eth_sign semantics according to the commit body, adds personal_sign and personal_recover around the signed-message workflow, introduces SignEthereum for Ethereum-format signatures, and documents the risks of raw crypto.Sign on adversary-chosen input. Tests were adjusted to handle both raw and Ethereum-style recovery-id formats.

# Why It Matters

1. RPC signing methods accept caller-controlled input.

2. Domain separation reduces ambiguity between arbitrary signed messages and other Ethereum signature uses.

3. Raw ECDSA signing is security-sensitive when exposed across trust boundaries.

4. The evidence supports hardening, not a confirmed exploited vulnerability.

# Evidence Notes

The strongest evidence is the commit body describing the eth_sign behavior change and the crypto.Sign comment warning about chosen-input signing risk. The snippets also support a split between raw signing and Ethereum-format signatures. Unsupported parts of the baseline were removed: the evidence does not show transaction processing validation, nonce or replay logic, state-transition behavior, or a demonstrated remote exploit. Protocol security invariant: Account-signing RPC methods should not expose raw ECDSA signing over caller-controlled input in a form that can be confused with other Ethereum signature contexts; arbitrary messages should be domain-prefixed and hashed before signing. Verification notes: The patch does not prove remote exploitability of eth_sign by itself. The evidence does not show transaction validation or nonce/replay handling being changed. The patch includes API additions and compatibility changes, so not every changed file is security-fix logic. No concrete private-key leakage scenario is demonstrated beyond the documented chosen-plaintext risk. The affected path is RPC/account message signing, not the core block or transaction execution path. Classified as RPC/account-signing, not transaction-processing. Bug class narrowed to signature-domain-separation rather than generic replay validation. Confidence remains medium because the commit message is explicit but the provided diff snippets do not include the full eth_sign implementation. Kept as security hardening because the patch addresses a documented signing-boundary risk without proving an exploit. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-domain-separation`
Final impact type: `signature-misuse-risk, private-key-exposure-risk`
Final tags: `rpc-account-signing, eth-sign, ecdsa, signature-domain-separation, security-hardening`

The supplied evidence supports retaining this as security hardening for RPC/account signing, not as a proven exploitable security fix. The commit explicitly changes eth_sign to prefix and hash arbitrary messages before signing, and the added crypto.Sign comments warn that raw adversary-chosen signing input can leak private-key information. However, the snippets do not show a concrete exploit, transaction replay flaw, or full eth_sign implementation, so the finding should be narrowed away from transaction-processing and generic replay claims.

## Security Evidence

1. Commit body states eth_sign now prefixes arbitrary messages with the Ethereum Signed Message string, hashes with keccak256, then signs.
2. crypto.Sign documentation explicitly warns that chosen-plaintext signing can leak private-key information and advises hashing input before signing.
3. Account-signing code distinguishes raw signing from Ethereum-format signatures via SignEthereum.
4. Tests and comments distinguish raw secp256k1 recovery IDs from Ethereum signature recovery IDs.

## Missing Evidence

1. No full eth_sign implementation diff is provided in the evidence snippets.
2. No demonstrated exploit path or remote attack scenario is shown.
3. No transaction validation, nonce handling, or replay-prevention logic is shown as changed.
4. No proof is provided that private-key leakage was practically exploitable in this code path.

## Claim Boundaries

1. Classify as RPC/account-signing hardening, not transaction-processing.
2. Do not claim a confirmed transaction replay vulnerability.
3. Do not claim proven private-key compromise; only a documented chosen-input signing risk.
4. The supported fix pattern is message-signing domain separation and hashing before ECDSA signing.
