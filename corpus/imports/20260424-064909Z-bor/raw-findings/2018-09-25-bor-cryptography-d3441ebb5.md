---
case_id: case_20180925_d3441ebb5
project: bor
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2018-09-25
source_refs:
  - git:d3441ebb563439bac0837d70591f92e2c6080303
  - "signer/core/api.go:442"
  - "signer/core/api.go:273"
  - "signer/core/api.go:232"
  - "signer/core/api.go:353"
bug_class: signer-trust-boundary-hardening
impact_type:
  - unsafe-default-behavior
  - reduced-attack-surface
confidence: medium
tags:
  - signer
  - fail-closed
  - api-surface
  - input-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a security-hardening change in the Clef signer API, not a demonstrated exploit fix. The grounded changes are fail-closed handling of transaction-validation warnings, removal of the externally exposed `EcRecover` helper, and stricter password handling in new-account creation.

## Observed Patch Facts

1. In `signer/core/api.go`, the patch replaces `// EcRecover returns the address for the Account that was used to create the signature.` with `// SignHash is a helper function that calculates a hash for the given message that ca...`.

2. In `signer/core/api.go`, the patch replaces `resp, err := api.UI.ApproveNewAccount(&NewAccountRequest{MetadataFromContext(ctx)})` with `var (`.

3. In `signer/core/api.go`, the patch replaces `return &SignerAPI{big.NewInt(chainID), accounts.NewManager(backends...), ui, NewValid...` with `if advancedMode {`.

4. In `signer/core/api.go`, the patch replaces `req := SignTxRequest{` with `// If we are in 'rejectMode', then reject rather than show the user warnings`.

## Project Context

The changed code sits primarily in `signer/core`, which anchors the finding in the `cryptography` area of the project. Historical context from `signer/core/api_test.go`, `signer/core/types.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `signer/core/api_test.go`, `signer/core/abihelper_test.go`. The strongest project-level identifiers around this patch are `accounts`, `SignerAPI`, `Account`, and `signature`.

## Before/After Behavior

Before the patch, `NewSignerAPI(...)` did not show a reject-mode flag in the returned `SignerAPI`, and `SignTransaction(...)` moved on after `ValidateTransaction(...)` without the new warning-to-error gate. After the patch, the constructor passes an added boolean derived from `!advancedMode`, and `SignTransaction(...)` returns an error if `msgs.getWarnings()` reports warnings while reject mode is enabled. Before the patch, `New(...)` made a single approval call for account creation; after the patch, it introduces a retry loop labeled `Three retries to get a valid password`. Before the patch, `signer/core/api.go` exposed an `EcRecover` method; after the patch, that method is removed from the shown API surface.

# Root Cause

The signer API was too permissive at the trust boundary: validator warnings were not enforced as blocking conditions by default, the remote API exposed an extra helper operation, and account-creation password input handling was weaker than the patched version.

## Walkthrough

1. `NewSignerAPI(...)` now carries a mode flag derived from `advancedMode`, indicating a default reject posture outside advanced mode.

2. `SignTransaction(...)` adds a new gate immediately after transaction validation: warnings become an error when reject mode is active.

3. `New(...)` changes from a single approval response to a bounded retry flow for obtaining a valid password during account creation.

4. The exported `EcRecover` API section is removed from `signer/core/api.go`, narrowing the remotely reachable signer surface.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| signer/core/api.go | 206 | initializes `SignerAPI` with reject-by-default behavior outside advanced mode |
| signer/core/api.go | 270 | new-account flow now retries for valid passwords and keeps approval as a gate |
| signer/core/api.go | 346 | transaction-signing path rejects validator warnings instead of merely surfacing them |
| signer/core/api.go | 415 | external signing surface is narrowed by removing the exposed `EcRecover` helper around this area |
| rpc/http.go | 1 | forwards UA and Origin into request context so the approval/UI layer can display origin metadata |
| signer/storage/aes_gcm_storage.go | 1 | hardens encrypted storage against key/value entry substitution |

## Code Snippets

## Snippet 1

Context: `signer/core/api.go:442` (changes signature or replay validation logic)

Before
```go
}

// EcRecover returns the address for the Account that was used to create the signature.
// Note, this function is compatible with eth_sign and personal_sign. As such it recovers
// the address of:
// hash = keccak256("\x19Ethereum Signed Message:\n"${message length}${message})
// addr = ecrecover(hash, signature)
//
```
After
```go
}

// SignHash is a helper function that calculates a hash for the given message that can be
// safely used to calculate a signature from.
```

## Snippet 2

Context: `signer/core/api.go:273` (changes a sensitive control or state-update path)

Before
```go
return accounts.Account{}, errors.New("password based accounts not supported")
	}
	resp, err := api.UI.ApproveNewAccount(&NewAccountRequest{MetadataFromContext(ctx)})

	if err != nil {
		return accounts.Account{}, err
	}
	if !resp.Approved {
```
After
```go
return accounts.Account{}, errors.New("password based accounts not supported")
	}
	var (
		resp NewAccountResponse
		err  error
	)
	// Three retries to get a valid password
	for i := 0; i < 3; i++ {
```

## Snippet 3

Context: `signer/core/api.go:232` (changes a sensitive control or state-update path)

Before
```go
}
	}
	return &SignerAPI{big.NewInt(chainID), accounts.NewManager(backends...), ui, NewValidator(abidb)}
}

// List returns the set of wallet this signer manages. Each wallet can contain
// multiple accounts.
func (api *SignerAPI) List(ctx context.Context) (Accounts, error) {
```
After
```go
}
	}
	if advancedMode {
		log.Info("Clef is in advanced mode: will warn instead of reject")
	}
	return &SignerAPI{big.NewInt(chainID), accounts.NewManager(backends...), ui, NewValidator(abidb), !advancedMode}
}
```

## Snippet 4

Context: `signer/core/api.go:353` (changes a sensitive control or state-update path)

Before
```go
return nil, err
	}

	req := SignTxRequest{
```
After
```go
return nil, err
	}
	// If we are in 'rejectMode', then reject rather than show the user warnings
	if api.rejectMode {
		if err := msgs.getWarnings(); err != nil {
			return nil, err
		}
	}
```

# Fix Pattern

Harden a signer trust boundary by failing closed on validator warnings, reducing exposed remote API surface, and tightening validation around sensitive account-creation inputs.

## How It Was Fixed

The patch adds reject-by-default behavior for validation warnings in transaction signing, removes the externally exposed `EcRecover` helper from the signer API, and adds repeated password-validation attempts in the new-account flow.

# Why It Matters

1. Warning-only validation can let risky signing requests proceed farther than intended.

2. Reducing exposed signer API methods lowers remote attack surface.

3. Password validation in account creation protects a sensitive state-changing path.

# Evidence Notes

Direct evidence is limited to `signer/core/api.go`. It clearly shows reject-by-default logic in `NewSignerAPI(...)` and `SignTransaction(...)`, a retry-based password-validation path in `New(...)`, and removal of `EcRecover` from the visible API surface. The draft's claims about `UA`/`Origin` forwarding and AES-GCM key/value swap protection are only supported by commit text and mapper notes, not by the supplied code excerpts, so they should not be treated as established here. Protocol security invariant: The external signer boundary must fail closed on risky requests: validation warnings should block signing by default, sensitive helper operations should not be unnecessarily exposed through the remote API, and account-creation inputs should be validated before creating state. Verification notes: The provided excerpts do not prove a concrete exploit chain or key theft before the patch. The patch shows stricter validation and reduced API exposure, but not that transaction signing previously bypassed user approval entirely. The AES-GCM storage issue is identified by commit text, but the exact cryptographic binding change is not shown in the excerpts. UA and Origin handling here improves operator context; it does not by itself authenticate the remote caller. No excerpted diff was provided for `rpc/http.go` or `signer/storage/aes_gcm_storage.go`, so those aspects are not validated from code here. The evidence supports security hardening, but not a fully demonstrated pre-patch exploit chain. The exact impact of removing `EcRecover` is not shown beyond API-surface reduction. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signer-trust-boundary-hardening`
Final impact type: `unsafe-default-behavior, reduced-attack-surface`
Final confidence: `medium`
Final tags: `signer, fail-closed, api-surface, input-validation`

The supplied patch evidence supports retaining this as a security-hardening case, not a proven exploit fix. The code shows the signer moving to reject warnings by default in a sensitive signing path, adding stricter handling around new-account password input, and removing an externally exposed cryptographic helper from the API surface. Those are security-relevant hardening changes at a trust boundary, but the excerpts do not prove a concrete replay, signature-validation, or forgery vulnerability before the patch.

## Security Evidence

1. `SignTransaction` now returns an error on validator warnings when `rejectMode` is enabled, changing a warning-only path into fail-closed behavior.
2. `NewSignerAPI` wires a `rejectMode` flag derived from `!advancedMode`, indicating stricter default behavior outside advanced mode.
3. The `EcRecover` external API method is removed from the shown API surface, reducing remotely reachable functionality.
4. `New` adds bounded retries for obtaining a valid password during account creation, showing stronger input validation on a sensitive operation.

## Missing Evidence

1. No diff is provided for the claimed AES-GCM key/value swap fix, so that cryptographic claim is not validated here.
2. No excerpt shows a concrete pre-patch exploit path, attacker-controlled bypass, or signature/replay abuse.
3. No evidence demonstrates that removing `EcRecover` fixed an actively vulnerable behavior rather than simply shrinking surface area.
4. UA/Origin forwarding and UI-display changes are mentioned in commit text but not proven security controls by the supplied code snippets.

## Claim Boundaries

1. This evidence supports security hardening of the signer boundary, not a confirmed security bug with demonstrated exploitation.
2. The original `replay-or-signature-validation` classification is too specific for the supplied patch excerpts.
3. The validated impact is conservative: stricter defaults and reduced attack surface, not proven request forgery or replay.
4. Only the shown changes in `signer/core/api.go` are grounded; broader commit-message security claims remain unverified from this patch evidence.
