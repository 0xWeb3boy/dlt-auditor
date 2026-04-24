---
case_id: case_20201208_ed0670cb17
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2020-12-08
source_refs:
  - git:ed0670cb17a96aafeb9eaaeb9765a42fb6bb5663
  - "mobile/bind.go:83"
  - "accounts/abi/bind/auth.go:101"
  - "les/sync_test.go:81"
  - "les/sync_test.go:164"
bug_class: replay-protection-hardening
impact_type:
  - replay-risk-reduction
confidence: medium
tags:
  - blockchain-core
  - transaction-signing
  - contract-bindings
  - eip-155
  - chain-id
  - replay-protection
  - api-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is an API hardening change for go-ethereum contract binding transaction signing. The patch adds or exposes helpers that accept a chainID and use NewKeyedTransactorWithChainID instead of forcing some helper paths through the legacy Homestead signer. The evidence does not establish an access-control flaw or a concrete exploitable replay vulnerability, so this should not be treated as a confirmed security fix.

## Observed Patch Facts

1. In `mobile/bind.go`, the patch replaces `func NewKeyedTransactOpts(keyJson []byte, passphrase string) (*TransactOpts, error) {` with `func NewKeyedTransactOpts(keyJson []byte, passphrase string, chainID *big.Int) (*Tran...`.

2. In `accounts/abi/bind/auth.go`, the patch replaces `// NewClefTransactor is a utility method to easily create a transaction signer` with `// NewTransactorWithChainID is a utility method to easily create a transaction signer...`.

3. In `les/sync_test.go`, the patch replaces `if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(bind.NewKeyed...` with `auth, _ := bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))`.

4. In `les/sync_test.go`, the patch replaces `if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(bind.NewKeyed...` with `auth, _ := bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))`.

## Project Context

The changed code sits primarily in `accounts/abi/bind`, `accounts/abi`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `accounts/abi/bind/bind_test.go`, `les/handler_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `accounts/abi/bind/backends/simulated_test.go`, `accounts/abi/bind/backends/simulated.go`. The strongest project-level identifiers around this patch are `header`, `byte`, `bind`, and `signerKey`.

## Before/After Behavior

Before the patch, mobile NewKeyedTransactOpts accepted only keyJson and passphrase, decrypted the key, and wrapped bind.NewKeyedTransactor, which used a HomesteadSigner. The shown legacy NewKeyedTransactor still checked that the requested signing address matched the key address. After the patch, mobile NewKeyedTransactOpts accepts chainID, calls bind.NewKeyedTransactorWithChainID, and returns construction errors. accounts/abi/bind/auth.go also adds NewTransactorWithChainID for encrypted key streams, and LES checkpoint oracle tests create TransactOpts with NewKeyedTransactorWithChainID using chain ID 1337.

# Root Cause

The evidence supports an API limitation: some transaction option helper paths exposed or routed callers to the legacy Homestead signing helper and did not let them specify an EIP-155 chain ID. It does not support the draft baseline claim that an authorization check was missing or delayed.

## Walkthrough

1. Contract binding callers use TransactOpts to sign contract transactions.

2. The legacy NewKeyedTransactor shown in auth.go uses HomesteadSigner and checks address != keyAddr before signing.

3. The old mobile helper decrypted key JSON and returned TransactOpts based on NewKeyedTransactor, so that helper path used Homestead signing.

4. The patch changes the mobile helper to accept chainID and delegate to NewKeyedTransactorWithChainID, propagating errors.

5. The patch adds NewTransactorWithChainID so encrypted key stream callers can construct chain-aware TransactOpts directly.

6. LES checkpoint oracle tests are updated to use NewKeyedTransactorWithChainID with chain ID 1337 for contract calls.

7. The supported security inference is limited to replay-protection hardening through explicit chain-aware signing support.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| accounts/abi/bind/auth.go | 84 | legacy NewKeyedTransactor path still constructs Homestead-signed TransactOpts and retains the address authorization check |
| accounts/abi/bind/auth.go | 101 | adds NewTransactorWithChainID to decrypt a key and return chain-aware TransactOpts |
| mobile/bind.go | 83 | mobile keyed transaction option helper now accepts chainID and delegates to NewKeyedTransactorWithChainID |
| les/sync_test.go | 81 | checkpoint oracle registration test now signs contract transaction with chain ID 1337 |
| les/sync_test.go | 164 | missing-oracle backend test now signs contract transaction with chain ID 1337 |

## Code Snippets

## Snippet 1

Context: `mobile/bind.go:83` (changes an authorization or privilege gate)

Before
```go
// NewKeyedTransactOpts is a utility method to easily create a transaction signer
// from a single private key.
func NewKeyedTransactOpts(keyJson []byte, passphrase string) (*TransactOpts, error) {
	key, err := keystore.DecryptKey(keyJson, passphrase)
	if err != nil {
		return nil, err
	}
	return &TransactOpts{*bind.NewKeyedTransactor(key.PrivateKey)}, nil
```
After
```go
// NewKeyedTransactOpts is a utility method to easily create a transaction signer
// from a single private key.
func NewKeyedTransactOpts(keyJson []byte, passphrase string, chainID *big.Int) (*TransactOpts, error) {
	key, err := keystore.DecryptKey(keyJson, passphrase)
	if err != nil {
		return nil, err
	}
	auth, err := bind.NewKeyedTransactorWithChainID(key.PrivateKey, chainID)
```

## Snippet 2

Context: `accounts/abi/bind/auth.go:101` (changes signature or replay validation logic)

Before
```go
}

// NewClefTransactor is a utility method to easily create a transaction signer
// with a clef backend.
```
After
```go
}

// NewTransactorWithChainID is a utility method to easily create a transaction signer from
// an encrypted json key stream and the associated passphrase.
func NewTransactorWithChainID(keyin io.Reader, passphrase string, chainID *big.Int) (*TransactOpts, error) {
	json, err := ioutil.ReadAll(keyin)
	if err != nil {
		return nil, err
```

## Snippet 3

Context: `les/sync_test.go:81` (changes an authorization or privilege gate)

Before
```go
sig, _ := crypto.Sign(crypto.Keccak256(data), signerKey)
			sig[64] += 27 // Transform V from 0/1 to 27/28 according to the yellow paper
			if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(bind.NewKeyedTransactor(signerKey), cp.SectionIndex, cp.Hash().Bytes(), new(big.Int).Sub(header.Number, big.NewInt(1)), header.ParentHash, [][]byte{sig}); err != nil {
				t.Error("register checkpoint failed", err)
			}
```
After
```go
sig, _ := crypto.Sign(crypto.Keccak256(data), signerKey)
			sig[64] += 27 // Transform V from 0/1 to 27/28 according to the yellow paper
			auth, _ := bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))
			if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(auth, cp.SectionIndex, cp.Hash().Bytes(), new(big.Int).Sub(header.Number, big.NewInt(1)), header.ParentHash, [][]byte{sig}); err != nil {
				t.Error("register checkpoint failed", err)
			}
```

## Snippet 4

Context: `les/sync_test.go:164` (changes an authorization or privilege gate)

Before
```go
sig, _ := crypto.Sign(crypto.Keccak256(data), signerKey)
	sig[64] += 27 // Transform V from 0/1 to 27/28 according to the yellow paper
	if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(bind.NewKeyedTransactor(signerKey), cp.SectionIndex, cp.Hash().Bytes(), new(big.Int).Sub(header.Number, big.NewInt(1)), header.ParentHash, [][]byte{sig}); err != nil {
		t.Error("register checkpoint failed", err)
	}
```
After
```go
sig, _ := crypto.Sign(crypto.Keccak256(data), signerKey)
	sig[64] += 27 // Transform V from 0/1 to 27/28 according to the yellow paper
	auth, _ := bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))
	if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(auth, cp.SectionIndex, cp.Hash().Bytes(), new(big.Int).Sub(header.Number, big.NewInt(1)), header.ParentHash, [][]byte{sig}); err != nil {
		t.Error("register checkpoint failed", err)
	}
```

# Fix Pattern

Add chain-aware signer construction APIs alongside legacy helpers, pass chainID through higher-level wrappers, and update call sites that need EIP-155 signing to use the new helper.

## How It Was Fixed

The patch introduced NewTransactorWithChainID, changed mobile NewKeyedTransactOpts to accept a chainID and call NewKeyedTransactorWithChainID, and updated representative tests to construct auth with NewKeyedTransactorWithChainID. The legacy Homestead helper remains present and deprecated, so the patch provides an explicit safer option rather than enforcing it everywhere.

# Why It Matters

1. EIP-155 signatures can bind transactions to a specific chain ID.

2. The old helper path shown used Homestead signing without that chain ID binding.

3. Contract binding helpers are reused by generated contract call code.

4. The patch reduces replay-sensitive API ambiguity.

5. The evidence does not prove a concrete exploit path.

# Evidence Notes

Primary evidence is from accounts/abi/bind/auth.go, mobile/bind.go, and les/sync_test.go. The commit message uses security language and says users can choose Homestead or EIP-155 and specify chainID. The code evidence supports chain-aware signing support, not access-control remediation, unauthorized checkpoint registration, remote exploitation, fund theft, or mandatory migration away from Homestead signing. Protocol security invariant: Contract transaction helpers should allow callers to use signing rules appropriate to the target chain. EIP-155 chain-aware signing binds signatures to a chain ID, but the provided evidence does not show that all prior Homestead-signed contract interactions were exploitable or that chain-aware signing became mandatory. Verification notes: The patch does not prove a missing privilege or access-control check. The patch does not show that Homestead-signed transactions were exploitable in all contract binding uses. The patch does not remove the legacy Homestead signer API; callers may still choose it. The evidence does not prove remote code execution, fund theft, or unauthorized checkpoint registration. The LES test changes demonstrate compatibility with chain-aware signing, not a production exploit path by themselves. Downgraded from likely security fix to unclear security relevance because no exploit path is established. Removed unsupported access-control framing; the shown legacy signer already checks the signing address. Kept the replay-protection/API-hardening explanation because it is grounded in the chainID and EIP-155 changes. Set keep_in_security_corpus to false under the rule for security-relevant but unproven vulnerability theses. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `replay-protection-hardening`
Final impact type: `replay-risk-reduction`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-signing, contract-bindings, eip-155, chain-id, replay-protection, api-hardening`

The supplied evidence supports retaining this as security hardening, not as a concrete security fix. The patch adds chainID-aware transaction signer construction and moves affected helper/test paths from the legacy Homestead signer toward NewKeyedTransactorWithChainID, which is replay-sensitive EIP-155 signing behavior. However, the evidence does not prove an exploitable prior vulnerability, missing authorization check, or mandatory enforcement of chain-aware signing.

## Security Evidence

1. Mobile keyed transaction options now accept a chainID and call NewKeyedTransactorWithChainID instead of NewKeyedTransactor.
2. accounts/abi/bind adds NewTransactorWithChainID for encrypted key streams and chain-aware signing.
3. Legacy NewKeyedTransactor shown in context uses HomesteadSigner and is deprecated in favor of NewKeyedTransactorWithChainID.
4. LES checkpoint oracle tests were updated to sign contract transactions with NewKeyedTransactorWithChainID and chain ID 1337.
5. Commit message explicitly frames chainID/EIP-155 signer selection as adding security.

## Missing Evidence

1. No demonstrated exploit path for replaying prior Homestead-signed contract interactions.
2. No evidence that the legacy signer lacked an authorization check; the shown code still checks address != keyAddr.
3. No proof that chain-aware signing became mandatory across all exposed contract-binding paths.
4. No evidence of unauthorized checkpoint registration, fund theft, consensus compromise, or remote attackability.

## Claim Boundaries

1. Classify as API/security hardening for replay-sensitive transaction signing only.
2. Do not classify as an access-control fix.
3. Do not claim a confirmed replay vulnerability from the patch alone.
4. Do not claim the legacy Homestead signer was removed or fully blocked.
