---
case_id: case_20201208_ed0670cb1
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
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
  - transaction-replay
confidence: medium
tags:
  - blockchain-core
  - transaction-signing
  - eip155
  - replay-protection
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a security-hardening change in the ABI binding transaction-signing helpers. Before this patch, the convenience path shown here used `types.HomesteadSigner{}`; the patch adds chain-ID-aware helper entry points and updates some callers to use them. The code supports a replay-protection rationale, but not a claim of a demonstrated exploit or full removal of legacy signing paths.

## Observed Patch Facts

1. In `mobile/bind.go`, the patch replaces `func NewKeyedTransactOpts(keyJson []byte, passphrase string) (*TransactOpts, error) {` with `func NewKeyedTransactOpts(keyJson []byte, passphrase string, chainID *big.Int) (*Tran...`.

2. In `accounts/abi/bind/auth.go`, the patch replaces `// NewClefTransactor is a utility method to easily create a transaction signer` with `// NewTransactorWithChainID is a utility method to easily create a transaction signer...`.

3. In `les/sync_test.go`, the patch replaces `if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(bind.NewKeyed...` with `auth, _ := bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))`.

4. In `les/sync_test.go`, the patch replaces `if _, err := server.handler.server.oracle.Contract().RegisterCheckpoint(bind.NewKeyed...` with `auth, _ := bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))`.

## Project Context

The changed code sits primarily in `accounts/abi/bind`, `accounts/abi`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `accounts/abi/bind/bind_test.go`, `les/handler_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `accounts/abi/bind/backends/simulated_test.go`, `accounts/abi/bind/backends/simulated.go`. The strongest project-level identifiers around this patch are `header`, `byte`, `bind`, and `signerKey`.

## Before/After Behavior

Before the change, the shown convenience helpers produced `TransactOpts` via `NewKeyedTransactor`, and the provided `auth.go` context shows that helper using `types.HomesteadSigner{}`. After the change, new constructors accept `chainID *big.Int`, the mobile wrapper now requires a chain ID and calls `NewKeyedTransactorWithChainID`, and the shown test call sites were updated to construct transactors with `big.NewInt(1337)` before submitting contract transactions.

# Root Cause

The helper layer for contract transaction creation was centered on a legacy Homestead-based signer, so convenience-generated signing options did not carry an explicit chain-specific replay-protection domain through those APIs.

## Walkthrough

1. `accounts/abi/bind/auth.go` shows `NewKeyedTransactor` building a signer with `types.HomesteadSigner{}`.

2. The patch adds `NewTransactorWithChainID(..., chainID *big.Int)` and routes decrypted-key construction into `NewKeyedTransactorWithChainID`.

3. `mobile/bind.go` changes `NewKeyedTransactOpts` to require `chainID` and replaces the old helper call with `NewKeyedTransactorWithChainID`.

4. The two shown `les/sync_test.go` call sites stop using `bind.NewKeyedTransactor(signerKey)` and instead create `auth` with `bind.NewKeyedTransactorWithChainID(signerKey, big.NewInt(1337))`.

5. These changes show added chain-aware signing support and caller migration, not proof that every legacy path was removed.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| accounts/abi/bind/auth.go | 84 | core transactor helper previously defaulting to `HomesteadSigner`, now complemented by chain-ID-aware signer construction |
| mobile/bind.go | 79 | mobile wrapper for `TransactOpts` creation, now accepts `chainID` and routes to the chain-aware signer helper |
| les/sync_test.go | 43 | integration-style test path updated to sign checkpoint-registration transactions with chain ID 1337 |
| les/sync_test.go | 134 | second oracle/checkpoint test path updated to the same chain-aware signing flow |

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

Add chain-ID-aware signer constructors, thread `chainID` through higher-level transaction-option helpers, and update representative callers to use the chain-aware path.

## How It Was Fixed

The patch introduced chain-ID-aware transactor creation in the ABI binding layer and propagated that API into the mobile wrapper and shown downstream call sites. Instead of always constructing `TransactOpts` through the Homestead-based helper, the updated paths can now build signing options with an explicit chain ID.

# Why It Matters

1. Chain-bound signatures are relevant to replay protection.

2. Convenience helpers often become the default signing path for callers.

3. The patch reduces reliance on legacy Homestead-only signing in updated paths.

4. The evidence supports hardening, not an authorization-bypass finding.

# Evidence Notes

Grounded evidence is limited to the provided snippets: the old helper in `accounts/abi/bind/auth.go` uses `types.HomesteadSigner{}`, new `WithChainID` helpers are added, `mobile/bind.go` now requires `chainID`, and two test call sites switch to `NewKeyedTransactorWithChainID(..., 1337)`. The commit message explicitly frames the change as allowing EIP155 plus chain ID for added security. The provided context also shows the legacy helper still exists, so the evidence does not support claiming universal enforcement or a proven real-world replay exploit. Protocol security invariant: Helper-created Ethereum transaction signers should be able to bind signatures to an intended chain ID when replay protection is required, instead of always using legacy Homestead signing. Verification notes: The patch does not prove that an attacker successfully replayed transactions across chains in practice. The evidence does not show an on-chain authorization bypass; the main change is transaction signature domain selection. The patch appears to add safer APIs and migrate some callers, but it does not prove all signing paths are now enforced to use EIP-155. The provided snippets do not show impact scope across deployments, forks, or external consumers of the old API. Assessment is based only on the supplied commit metadata and code excerpts. No exploit reproduction or impact demonstration is provided in the evidence. The snippets support replay-protection hardening more strongly than a concrete vulnerability-fix claim. Legacy signing helper presence in the provided context limits confidence about complete mitigation scope. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `replay-protection`
Final impact type: `transaction-replay`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-signing, eip155, replay-protection`

The patch evidence supports a security-hardening change, not an access-control fix. The code adds chain-ID-aware transactor constructors, threads `chainID` into higher-level transaction-option helpers, and updates representative callers to use the chain-aware path. That directly aligns with replay-protection hardening for Ethereum-style transaction signing. However, the patch does not prove a concrete exploitable vulnerability, and the legacy Homestead-based helper still exists in the provided context, so the strongest justified label is security hardening rather than a confirmed security bug fix.

## Security Evidence

1. Commit message explicitly cites EIP155 and chain ID as adding security.
2. `NewTransactorWithChainID` is added for chain-aware signing.
3. `mobile/bind.go` now requires `chainID` for keyed transact options.
4. Updated call sites switch from `NewKeyedTransactor` to `NewKeyedTransactorWithChainID(..., 1337)`.
5. Provided context shows the old helper used `types.HomesteadSigner{}`, making the change replay-sensitive.

## Missing Evidence

1. No proof of an actual replay exploit or vulnerable deployment is shown.
2. No evidence that all old signing paths were removed or blocked.
3. No test or patch snippet demonstrates a previously accepted replayed transaction.
4. No concrete impact on funds, authorization, or consensus is demonstrated.

## Claim Boundaries

1. Do not describe this as an access-control or privilege-escalation fix.
2. Do not claim a proven exploitable vulnerability from the patch alone.
3. Do not claim universal enforcement of chain-ID signing across the project.
4. The supported claim is limited to replay-protection hardening in transaction-signing helpers and some migrated callers.
