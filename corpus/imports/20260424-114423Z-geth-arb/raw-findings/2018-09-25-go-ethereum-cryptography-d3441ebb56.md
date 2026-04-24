---
case_id: case_20180925_d3441ebb56
project: go-ethereum
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
bug_class: signer-boundary-policy-hardening
impact_type:
  - unsafe-signing-risk-reduction
  - api-surface-reduction
confidence: medium
tags:
  - signer
  - clef
  - rpc
  - fail-closed
  - api-surface-reduction
  - transaction-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is signer-boundary hardening. The clearest grounded change makes Clef reject transaction validation warnings by default before continuing toward UI-mediated signing, while preserving warning-only behavior only under explicit advanced mode. The same supplied evidence supports password-validation retries for new account creation and removal of the shown EcRecover external API method, but it does not prove signature forgery, replay, consensus impact, or direct remote signing without user approval.

## Observed Patch Facts

1. In `signer/core/api.go`, the patch replaces `// EcRecover returns the address for the Account that was used to create the signature.` with `// SignHash is a helper function that calculates a hash for the given message that ca...`.

2. In `signer/core/api.go`, the patch replaces `resp, err := api.UI.ApproveNewAccount(&NewAccountRequest{MetadataFromContext(ctx)})` with `var (`.

3. In `signer/core/api.go`, the patch replaces `return &SignerAPI{big.NewInt(chainID), accounts.NewManager(backends...), ui, NewValid...` with `if advancedMode {`.

4. In `signer/core/api.go`, the patch replaces `req := SignTxRequest{` with `// If we are in 'rejectMode', then reject rather than show the user warnings`.

## Project Context

The changed code sits primarily in `signer/core`, which anchors the finding in the `cryptography` area of the project. Historical context from `signer/core/api_test.go`, `signer/core/types.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `signer/core/api_test.go`, `signer/core/abihelper_test.go`. The strongest project-level identifiers around this patch are `accounts`, `SignerAPI`, `Account`, and `signature`.

## Before/After Behavior

Before the patch, SignerAPI construction did not include the shown rejectMode policy, and SignTransaction could continue after validation produced warnings. After the patch, NewSignerAPI accepts advancedMode and stores rejectMode as !advancedMode; SignTransaction calls msgs.getWarnings() in reject mode and returns the warning error before request construction. Before the patch, New called ApproveNewAccount once; after the patch, it retries up to three times to obtain a valid password response. The shown EcRecover method was removed from the external API area near the signing code.

# Root Cause

The grounded root cause was a permissive default at the signer boundary: validator warnings were not treated as blocking errors in normal mode before the signing request could continue. Other changes reduce exposed API surface and improve account-creation input validation, but the provided evidence does not establish those as independently exploitable root causes.

## Walkthrough

1. NewSignerAPI now takes an advancedMode setting.

2. Normal mode maps to rejectMode by storing !advancedMode on SignerAPI.

3. SignTransaction still validates the transaction first through ValidateTransaction.

4. In rejectMode, SignTransaction calls msgs.getWarnings() and returns an error if warnings are present.

5. This stops the flow before constructing the signing request for UI approval.

6. New account creation now loops through the UI approval/password path up to three times for valid password input.

7. The shown EcRecover external API method was removed, reducing nonessential external API surface.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| signer/core/api.go | 206 | constructs SignerAPI with rejectMode enabled by default unless advancedMode is requested |
| signer/core/api.go | 346 | validates transaction and rejects validator warnings before building the signing request in default mode |
| signer/core/api.go | 270 | new account flow now retries through UI until a valid password response is obtained |
| signer/core/api.go | 415 | sign data path remains UI-mediated and removes EcRecover from the external API surface near this signing API area |
| rpc/http.go | 1 | commit context says HTTP server forwards User-Agent and Origin into request context for signer UI display |

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

Fail closed at the signer API boundary: convert validator warnings into errors by default, require explicit advanced mode for warning-only behavior, validate account-creation input before continuing, and remove unnecessary external API methods.

## How It Was Fixed

The patch added rejectMode behavior to SignerAPI construction, set it to true unless advancedMode is enabled, and added a SignTransaction check that returns validator warning errors in default mode. It also changed the new-account path to retry for a valid password response and removed the shown EcRecover method from signer/core/api.go.

# Why It Matters

1. Default signer behavior rejects unsafe or suspicious transaction conditions instead of only warning.

2. Users in normal mode are less likely to approve a transaction that validator logic already flagged.

3. Advanced warning-only behavior remains explicit rather than the default.

4. Validated password input is required before new account creation proceeds.

5. Reducing external API surface lowers signer exposure, though exploitability is not shown.

# Evidence Notes

Evidence is strongest for signer/core/api.go: NewSignerAPI constructs SignerAPI with !advancedMode, SignTransaction rejects msgs.getWarnings() in rejectMode, New adds a three-retry password validation flow, and the EcRecover method shown in the before snippet is removed. Commit text also mentions local path disclosure removal, account import removal, AES-GCM key/value swap prevention, calldata length checking, and User-Agent/Origin display, but the supplied code excerpts do not establish those details enough to classify them as the root cause here. The evidence does not support claims of signature forgery, replay, consensus failure, or remote signing without UI approval. Protocol security invariant: The Clef signer boundary should fail closed on validator warnings by default, expose only necessary external API methods, and require validated user input before account creation or signing-sensitive operations proceed. Verification notes: The patch evidence does not prove direct remote transaction signing without user approval. The patch evidence does not prove signature forgery, replay, or consensus impact. The AES-GCM key/value swap issue is named in the commit body, but the provided diff evidence does not show the storage invariant details. Removing EcRecover and account import from the external API is API surface reduction; exploitability is not shown here. User-Agent and Origin display depends on remote-supplied headers and should not be treated as strong authentication. Classified as security hardening, not a confirmed concrete exploit. Downgraded away from cryptography/replay classification because the shown code does not prove replay or signature-validation failure. Kept in security corpus because the commit and grounded code changes show security-relevant signer fail-closed behavior. AES-GCM storage and local path disclosure claims are not used as primary evidence because their diffs are not provided. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signer-boundary-policy-hardening`
Final impact type: `unsafe-signing-risk-reduction, api-surface-reduction`
Final confidence: `medium`
Final tags: `signer, clef, rpc, fail-closed, api-surface-reduction, transaction-validation`

The supplied evidence supports keeping this as security hardening, not as a concrete replay or signature-validation vulnerability. The strongest code evidence shows Clef changing default signer behavior to reject validator warnings unless advanced mode is explicitly enabled, plus removal of an external EcRecover API method and added password validation retries. That is security-relevant fail-closed behavior at a signing boundary, but the excerpts do not prove an exploitable signature forgery, replay, consensus issue, or direct unauthorized signing bug.

## Security Evidence

1. Commit subject and body explicitly describe security fixes in Clef/signer.
2. NewSignerAPI now accepts advancedMode and stores rejectMode as the inverse of advancedMode.
3. SignTransaction now returns an error on validator warnings in rejectMode before constructing the signing request.
4. Default behavior is changed from warning-only to reject-by-default unless advanced mode is selected.
5. The shown EcRecover external API method is removed from signer/core/api.go.
6. New account creation now retries through a password validation path instead of accepting a single UI response.

## Missing Evidence

1. No supplied excerpt proves request forgery, replay, or signature forgery.
2. No supplied excerpt proves consensus or validator impact.
3. No supplied excerpt shows an attacker bypassing UI approval or causing unauthorized signing.
4. Commit body mentions AES-GCM storage, local path disclosure, account import removal, and calldata length checks, but the provided code evidence does not show those fixes.

## Claim Boundaries

1. Classify as signer-boundary hardening rather than a confirmed exploitable vulnerability.
2. Do not retain the original replay-or-signature-validation classification.
3. Do not claim request replay, signature forgery, consensus failure, or remote signing without user approval.
4. Treat EcRecover removal as API surface reduction unless additional exploit evidence is supplied.
5. Treat User-Agent and Origin forwarding/display as contextual UI information, not authentication.
