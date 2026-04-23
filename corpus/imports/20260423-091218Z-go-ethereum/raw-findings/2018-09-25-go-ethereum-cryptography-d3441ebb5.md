---
case_id: case_20180925_d3441ebb5
project: go-ethereum
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2018-09-25
source_refs:
  - git:d3441ebb563439bac0837d70591f92e2c6080303
  - "signer/core/api.go:442"
  - "signer/core/api.go:273"
  - "signer/core/api.go:232"
  - "signer/core/api.go:353"
bug_class: signer-policy-hardening
impact_type:
  - unsafe-signing-default
  - api-surface-reduction
tags:
  - clef
  - signer
  - deny-by-default
  - transaction-validation
  - api-surface-reduction
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a Clef/signer security-hardening finding, not a low-level cryptographic replay or signature-validation flaw. The strongest grounded change is that signer transaction validation warnings are rejected by default before the signing prompt/path, while advanced mode preserves warning behavior. The commit also removes or narrows some external API surface, including EcRecover in the shown code, but several other security claims are supported only by commit text rather than visible hunks.

## Observed Patch Facts

1. In `signer/core/api.go`, the patch replaces `// EcRecover returns the address for the Account that was used to create the signature.` with `// SignHash is a helper function that calculates a hash for the given message that ca...`.

2. In `signer/core/api.go`, the patch replaces `resp, err := api.UI.ApproveNewAccount(&NewAccountRequest{MetadataFromContext(ctx)})` with `var (`.

3. In `signer/core/api.go`, the patch replaces `return &SignerAPI{big.NewInt(chainID), accounts.NewManager(backends...), ui, NewValid...` with `if advancedMode {`.

4. In `signer/core/api.go`, the patch replaces `req := SignTxRequest{` with `// If we are in 'rejectMode', then reject rather than show the user warnings`.

## Project Context

The changed code sits primarily in `signer/core`, which anchors the finding in the `cryptography` area of the project. Historical context from `signer/core/api_test.go`, `signer/core/types.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `signer/core/api_test.go`, `signer/core/abihelper_test.go`. The strongest project-level identifiers around this patch are `accounts`, `SignerAPI`, `Account`, and `signature`.

## Before/After Behavior

Before the change, the shown SignTransaction path validated the transaction but did not show a default-mode gate that converted validator warnings into errors before proceeding. After the change, NewSignerAPI sets rejectMode to !advancedMode, and SignTransaction returns msgs.getWarnings() as an error when rejectMode is true. Before the change, New(ctx) performed a single new-account UI approval request in the shown excerpt; after the change, it uses a retry loop around approval/password handling. Before the change, EcRecover was exposed as a SignerAPI method in signer/core/api.go; after the change, that method is removed from the shown API surface.

# Root Cause

The supported root cause is a permissive signer policy/API boundary: validation warnings and nonessential external API methods were allowed in the default signer interface. The evidence does not establish private key extraction, signature forgery, consensus failure, or a proven remote exploit path.

## Walkthrough

1. An external Clef/signer request reaches the SignerAPI transaction signing path.

2. SignTransaction calls api.validator.ValidateTransaction and receives validation messages.

3. The patch adds rejectMode to SignerAPI construction and enables it by default unless advancedMode is selected.

4. When rejectMode is true, SignTransaction treats validation warnings as errors and returns before proceeding toward approval/signing.

5. The patch removes the EcRecover method from the shown external signer API surface.

6. The new-account flow is changed from a single approval call to a retry loop around approval/password handling.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| signer/core/api.go | 206 | constructs SignerAPI with rejectMode enabled by default unless advancedMode is selected |
| signer/core/api.go | 346 | transaction signing path rejects validator warnings before prompting/signing in default mode |
| signer/core/api.go | 270 | new account flow retries UI approval until a valid password is supplied before account creation |
| signer/core/api.go | 442 | removes EcRecover from the external signer API surface |
| rpc/http.go | 0 | commit indicates HTTP server forwards User-Agent and Origin into request context for signer UI display |
| signer/storage/aes_gcm_storage.go | 0 | commit indicates encrypted storage was changed to prevent swapping key-value entries |

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

Deny by default at the signer API boundary: turn validation warnings into blocking errors in normal mode, require explicit advanced mode for warning-only behavior, and reduce exposed external API capabilities.

## How It Was Fixed

NewSignerAPI now receives advancedMode and stores rejectMode as !advancedMode. SignTransaction checks msgs.getWarnings() under rejectMode and returns any warning as an error before continuing. The shown EcRecover API method is removed, and the new-account path is reworked to retry approval/password handling. Other changes mentioned in the commit, such as path disclosure removal, calldata length checks, and AES-GCM key-value swap prevention, are not sufficiently shown in the provided hunks to describe precisely.

# Why It Matters

1. Default signing behavior blocks suspicious transactions instead of relying only on user interpretation of warnings.

2. Advanced mode becomes an explicit opt-in for weaker warning-only behavior.

3. Reducing signer API surface lowers exposure from unnecessary external methods.

4. The provided evidence supports hardening, but not a demonstrated cryptographic break or remote compromise.

# Evidence Notes

Grounded code evidence comes from signer/core/api.go: NewSignerAPI setting rejectMode, SignTransaction rejecting warnings in default mode, New(ctx) changing account-creation approval flow, and removal of EcRecover. Commit metadata additionally mentions local path disclosure removal, User-Agent/Origin display, account import removal, calldata length checking, and AES-GCM storage hardening, but those exact mechanisms are not visible in the supplied excerpts. The heuristic label replay-or-signature-validation is too strong for the shown code. Protocol security invariant: Clef/signer external requests should expose only intended API capabilities and should not proceed to transaction signing or account creation unless validation and UI policy allow them. Validation warnings are treated as blocking by default, with warning-only behavior reserved for explicit advanced mode. Verification notes: The evidence does not prove private key extraction or signature forgery. The evidence does not prove remote exploitability without user approval or deployment configuration details. The EcRecover removal alone is API surface reduction, not proof of a cryptographic vulnerability. The AES-GCM storage issue is identified from commit metadata, but the provided patch excerpt does not show the exact binding mechanism. The heuristic replay/signature-validation label is too broad for the traced signer policy path. No private-key extraction or signature-forgery path is proven by the provided evidence. No remote exploitability claim is supported without deployment and user-approval context. AES-GCM storage hardening is security-relevant in commit text, but the provided excerpt does not show the binding fix. Classified as security hardening rather than a confirmed specific vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signer-policy-hardening`
Final impact type: `unsafe-signing-default, api-surface-reduction`
Final tags: `clef, signer, deny-by-default, transaction-validation, api-surface-reduction, security-hardening`

The supplied evidence supports retaining this as security hardening, not as a concrete replay or signature-validation vulnerability. The strongest code-backed change is that Clef/signer now rejects validator warnings by default before continuing in the transaction-signing path, with warning-only behavior requiring advanced mode. The removal of EcRecover from the external signer API also supports API surface reduction. The evidence does not prove signature forgery, replay, request forgery, or a specific exploit path.

## Security Evidence

1. NewSignerAPI stores rejectMode as the inverse of advancedMode, making rejection the default behavior.
2. SignTransaction now returns validator warnings as errors when rejectMode is enabled, blocking the signing flow before approval/signing continues.
3. EcRecover is removed from the shown SignerAPI surface, reducing externally exposed signer functionality.
4. Commit metadata explicitly frames the change set as Clef/signer security fixes and mentions several security-sensitive signer/API changes.

## Missing Evidence

1. No supplied hunk demonstrates a concrete replay or signature-validation bypass.
2. No exploit path shows an attacker causing unauthorized signing without user approval.
3. No supplied AES-GCM storage hunk shows the key-value swap prevention mechanism.
4. No supplied path-disclosure or calldata-length hunk is available to validate those claims independently.

## Claim Boundaries

1. Validate as signer/Clef hardening, not a proven cryptographic vulnerability fix.
2. Do not claim private-key extraction, signature forgery, consensus impact, or remote compromise from this evidence.
3. Do not retain the original replay-or-signature-validation or request-forgery framing as the primary corpus label.
4. Commit-level security language can support context, but concrete corpus claims should stay limited to the shown signer policy and API-surface changes.
