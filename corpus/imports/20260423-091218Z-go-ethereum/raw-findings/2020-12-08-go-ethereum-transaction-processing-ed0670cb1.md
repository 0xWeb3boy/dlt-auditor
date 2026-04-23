---
case_id: case_20201208_ed0670cb1
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2020-12-08
source_refs:
  - git:ed0670cb17a96aafeb9eaaeb9765a42fb6bb5663
  - "mobile/bind.go:83"
  - "accounts/abi/bind/auth.go:101"
  - "les/sync_test.go:81"
  - "les/sync_test.go:164"
bug_class: replay-protection
impact_type:
  - cross-chain-replay-risk
tags:
  - blockchain-core
  - transaction-processing
  - signature
  - eip155
  - chainid
  - replay-protection
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports replay-protection hardening in go-ethereum contract binding transaction option creation. The patch adds chainID-aware signer construction and routes mobile keyed transaction options and relevant tests through `NewKeyedTransactorWithChainID`. It does not establish an access-control flaw, privilege bypass, or proven exploit.

## Observed Patch Facts

1. In `mobile/bind.go`, the patch replaces `func NewKeyedTransactOpts(keyJson []byte, passphrase string) (*TransactOpts, error) {` with `func NewKeyedTransactOpts(keyJson []byte, passphrase string, chainID *big.Int) (*Tran...`.

2. In `accounts/abi/bind/auth.go`, the patch replaces `// NewClefTransactor is a utility method to easily create a transaction signer` with `// NewTransactorWithChainID is a utility method to easily create a transaction signer...`.

3. In `les/sync_test.go`, the patch replaces `if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(bind.NewKeyed...` with `auth, _ := bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))`.

4. In `les/sync_test.go`, the patch replaces `if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(bind.NewKeyed...` with `auth, _ := bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))`.

## Project Context

The changed code sits primarily in `accounts/abi/bind`, `accounts/abi`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `accounts/abi/bind/bind_test.go`, `les/handler_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `accounts/abi/bind/backends/simulated_test.go`, `accounts/abi/bind/backends/simulated.go`. The strongest project-level identifiers around this patch are `header`, `byte`, `bind`, and `signerKey`.

## Before/After Behavior

Before the patch, the shown binding paths used `NewKeyedTransactor`, which constructs `TransactOpts` with `types.HomesteadSigner{}` and has no chainID input. The mobile wrapper also returned options from that legacy helper. After the patch, new chainID-aware constructors are available, the mobile keyed transaction option API accepts `chainID *big.Int`, errors from chainID-aware construction are propagated, and LES checkpoint oracle tests use chainID `1337`.

# Root Cause

The prior helper API defaulted to Homestead signing and did not let these entry points express EIP-155 chain-domain separation. The supported root cause is legacy/default signing behavior without chainID selection, not missing authorization.

## Walkthrough

1. `NewKeyedTransactor` built `TransactOpts` using `types.HomesteadSigner{}`.

2. The mobile `NewKeyedTransactOpts` wrapper decrypted a key and returned options from that legacy helper.

3. The patch adds `NewTransactorWithChainID`, which decrypts the key and delegates to `NewKeyedTransactorWithChainID`.

4. The mobile wrapper now accepts a `chainID` and delegates to `bind.NewKeyedTransactorWithChainID`.

5. LES checkpoint oracle tests now construct auth options with `NewKeyedTransactorWithChainID(..., big.NewInt(1337))`.

6. The old Homestead helper remains present and deprecated, so the patch adds safer chainID-aware paths rather than eliminating legacy signing entirely.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| accounts/abi/bind/auth.go | 84 | Existing NewKeyedTransactor path still builds Homestead-signed TransactOpts and is deprecated in favor of chainID-aware signing. |
| accounts/abi/bind/auth.go | 101 | Adds NewTransactorWithChainID to decrypt a key and create TransactOpts using a chainID-aware signer. |
| mobile/bind.go | 83 | Mobile TransactOpts construction now accepts chainID and delegates to NewKeyedTransactorWithChainID. |
| les/sync_test.go | 81 | Checkpoint oracle contract transaction tests updated to sign with chainID 1337. |
| les/sync_test.go | 164 | Oracle backend registration test updated to use chainID-aware transaction signing. |

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

Add explicit chainID-aware transaction signer construction and update affected entry points that need chain-specific signing to use it, while retaining the legacy Homestead helper as deprecated compatibility API.

## How It Was Fixed

`accounts/abi/bind/auth.go` gained `NewTransactorWithChainID`; `mobile/bind.go` changed keyed transaction option construction to accept a chainID and call `NewKeyedTransactorWithChainID`; tests in `les/sync_test.go` were updated to use chainID-aware auth options for simulated oracle contract registration.

# Why It Matters

1. ChainID-aware signing provides domain separation for EIP-155 chains.

2. Always defaulting contract binding helpers to Homestead signing can be unsafe for callers expecting replay protection.

3. The evidence supports hardening against cross-chain replay risk.

4. The evidence does not prove remote exploitation or unauthorized contract execution.

# Evidence Notes

Grounded evidence is limited to signer construction changes in `accounts/abi/bind/auth.go`, the mobile wrapper change in `mobile/bind.go`, and test updates in `les/sync_test.go`. The commit message explicitly says previous contract interactions used the Homestead signer and that users can now specify Homestead or EIP-155 plus chainID. Claims about access control, privilege checks, or demonstrated exploitability are unsupported and removed. Protocol security invariant: Contract transaction signing should use a signer appropriate to the target chain. On EIP-155 chains, callers should be able to bind signatures to the intended chainID rather than always producing legacy Homestead-style signatures. Verification notes: The patch does not prove a remote attacker could exploit the prior behavior. The patch does not remove the Homestead signing API; it remains available and deprecated. The evidence does not show unauthorized contract calls or privilege bypass. The concrete impact depends on callers using contract bindings on chains where replay across chain domains matters. Test changes demonstrate required chainID use in simulated/oracle paths but do not by themselves prove production compromise. No evidence shows a privilege bypass or authorization-check ordering issue. No evidence shows the legacy Homestead API was removed; it remains deprecated. Test updates demonstrate expected use of chainID-aware signing in simulated chain context. Impact depends on callers and deployment contexts where Homestead-style signatures could be replay-sensitive. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `replay-protection`
Final impact type: `cross-chain-replay-risk`
Final tags: `blockchain-core, transaction-processing, signature, eip155, chainid, replay-protection`

The supplied evidence supports retaining this as security hardening, not as an access-control or privilege-misuse fix. The patch adds chainID-aware transaction signer construction, routes mobile keyed transact options through that path, and updates tests to use an EIP-155-style chain-specific signer. This clearly tightens replay-sensitive signing behavior, but it does not prove an exploitable vulnerability or unauthorized contract execution.

## Security Evidence

1. Commit message states previous contract interactions used the Homestead signer and now users can specify Homestead or EIP-155 plus chainID.
2. `mobile/bind.go` changes keyed transact option creation to accept `chainID` and call `NewKeyedTransactorWithChainID`.
3. `accounts/abi/bind/auth.go` adds `NewTransactorWithChainID` for encrypted-key transaction signer creation.
4. Tests replace `NewKeyedTransactor` with `NewKeyedTransactorWithChainID(..., big.NewInt(1337))` in checkpoint oracle contract interactions.

## Missing Evidence

1. No evidence shows a concrete exploit, theft, privilege escalation, or unauthorized contract execution.
2. No evidence shows an access-control check was missing or bypassed.
3. The legacy Homestead signer path remains available and is deprecated rather than removed.
4. Impact depends on callers and deployment contexts where cross-chain replay protection matters.

## Claim Boundaries

1. Classify as replay-protection hardening, not access control.
2. Do not claim a proven security fix for an exploited vulnerability.
3. Do not claim privilege misuse or authorization bypass from this patch alone.
4. Supported claim is that the patch adds safer chainID-aware signing paths for contract binding transactions.
