---
case_id: case_20240806_72f88bae
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2024-08-06
source_refs:
  - git:72f88bae5e19566276490a783886b2420e037635
  - "coordinator/internal/types/auth.go:27"
  - "coordinator/internal/types/auth.go:98"
  - "common/version/version.go:6"
bug_class: signature-preimage-mismatch
impact_type:
  - authentication-integrity
confidence: medium
tags:
  - authentication
  - cryptography
  - legacy-compatibility
  - signature-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a targeted compatibility fix in coordinator authentication: the legacy Curie public-key recovery path was changed to hash a dedicated legacy identity payload instead of the current Message object. That shows a signer-recovery mismatch, but the provided diff does not establish that this caused acceptance of forged logins, replay, or an authorization bypass.

## Observed Patch Facts

1. In `coordinator/internal/types/auth.go`, the patch replaces `// Message the login message struct` with `// TODO just use for darwin upgrade, need delete next upgrade`.

2. In `coordinator/internal/types/auth.go`, the patch replaces `hash, err := a.Message.Hash()` with `curieIdentity := identity{`.

3. In `common/version/version.go`, the patch replaces `var tag = "v4.4.41"` with `var tag = "v4.4.42"`.

## Project Context

The changed code sits primarily in `coordinator/internal/types`, `coordinator/internal`, `common/version`, which anchors the finding in the `cryptography` area of the project. Historical context from `coordinator/internal/types/auth_test.go`, `coordinator/internal/types/metric.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `coordinator/internal/types/auth_test.go`, `coordinator/internal/orm/prover_task.go`. The strongest project-level identifiers around this patch are `Message`, `json`, `ProverName`, and `ProverVersion`.

## Before/After Behavior

Before the patch, RecoverPublicKeyFromSignature() recovered a key using a hash of a.Message. After the patch, it constructs a legacy identity with ProverName, ProverVersion, Challenge, and HardForkName set to "curie", then hashes that legacy identity for recovery. The nearby Verify() path still hashes a.Message in the shown excerpt. The version file change is only a release tag bump.

# Root Cause

The legacy pre-darwin/Curie compatibility path used the wrong signing preimage for public-key recovery: it hashed the current Message representation instead of the legacy identity payload expected by that compatibility flow.

## Walkthrough

1. The patch adds a new identity struct with ProverName, ProverVersion, Challenge, and HardForkName in coordinator/internal/types/auth.go.

2. The patch adds identity.Hash(), which RLP-encodes that identity and hashes it.

3. Before the change, RecoverPublicKeyFromSignature() started from a.Message.Hash().

4. After the change, RecoverPublicKeyFromSignature() builds a Curie-specific identity object from selected message fields and hard-codes HardForkName to "curie".

5. The recovery path now uses curieIdentity.Hash() instead of a.Message.Hash().

6. The shown Verify() function still hashes a.Message, so the change is limited to the legacy recovery path.

7. The only other modified file is common/version/version.go, which only bumps the release tag.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| coordinator/internal/types/auth.go | 27 | Defines the legacy Curie identity serialization used as the signature preimage for compatibility-sensitive login key recovery. |
| coordinator/internal/types/auth.go | 98 | Changes RecoverPublicKeyFromSignature to hash the legacy Curie identity instead of the current Message struct when recovering a prover public key from a signature. |
| common/version/version.go | 6 | Release/version bump only; no protocol or security semantics shown. |

## Code Snippets

## Snippet 1

Context: `coordinator/internal/types/auth.go:27` (changes signature or replay validation logic)

Before
```go
}

// Message the login message struct
type Message struct {
```
After
```go
}

// TODO just use for darwin upgrade, need delete next upgrade
type identity struct {
	ProverName    string `json:"prover_name"`
	ProverVersion string `json:"prover_version"`
	Challenge     string `json:"challenge"`
	HardForkName  string `json:"hard_fork_name"`
```

## Snippet 2

Context: `coordinator/internal/types/auth.go:98` (changes signature or replay validation logic)

Before
```go
// This method is for pre-darwin's compatible.
func (a *LoginParameter) RecoverPublicKeyFromSignature() (string, error) {
	hash, err := a.Message.Hash()
	if err != nil {
		return "", err
```
After
```go
// This method is for pre-darwin's compatible.
func (a *LoginParameter) RecoverPublicKeyFromSignature() (string, error) {
	curieIdentity := identity{
		ProverName:    a.Message.ProverName,
		ProverVersion: a.Message.ProverVersion,
		Challenge:     a.Message.Challenge,
		HardForkName:  "curie",
	}
```

## Snippet 3

Context: `common/version/version.go:6` (changes a sensitive control or state-update path)

Before
```go
)

var tag = "v4.4.41"

var commit = func() string {
```
After
```go
)

var tag = "v4.4.42"

var commit = func() string {
```

# Fix Pattern

Use a protocol-version-specific canonical signing payload in compatibility code instead of reusing the current message schema.

## How It Was Fixed

The fix introduces a dedicated legacy identity type and switches RecoverPublicKeyFromSignature() to hash that legacy Curie payload, including an explicit hard-fork name, so recovered keys are derived from the expected legacy signing context.

# Why It Matters

1. It corrects key recovery for older Curie-compatible signers.

2. It prevents mixing a legacy recovery path with a newer message schema.

3. It shows a compatibility/authentication bug, but not a proven exploit from the supplied evidence.

# Evidence Notes

Supported directly by the diff: a new identity struct and Hash() method were added, and RecoverPublicKeyFromSignature() changed from hashing a.Message to hashing a Curie-specific identity. The evidence does not show any changed authorization decision, any call site proving exploitability, or any replay/nonce lifecycle change. The version.go modification has no demonstrated security meaning. Protocol security invariant: Public-key recovery or signature verification must use the same canonical signed payload and signing context that the prover actually used. In the legacy Curie compatibility path, recovery should be derived from the legacy identity payload, not the newer Message representation. Verification notes: The patch does not prove that invalid or forged signatures were previously accepted. The patch does not show a replay-defense change such as nonce or challenge lifecycle enforcement. The patch does not establish where recovered public keys are consumed for authorization decisions. The evidence only clearly supports a legacy Curie/pre-darwin compatibility mismatch, not a broader cryptographic break. No concrete exploit path or privilege escalation is demonstrated by the diff alone. The diff clearly demonstrates a change in the recovery preimage for the legacy Curie path. The diff does not demonstrate that invalid signatures were previously accepted. The diff does not show where recovered public keys are consumed for authorization. The diff does not support a stronger claim such as replay protection, privilege escalation, or confirmed vulnerability exploitation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-preimage-mismatch`
Final impact type: `authentication-integrity`
Final confidence: `medium`
Final tags: `authentication, cryptography, legacy-compatibility, signature-validation`

The patch changes an authentication-sensitive cryptographic path so legacy public-key recovery uses a Curie-specific canonical identity payload, including an explicit hard-fork name, instead of the current Message schema. That clearly tightens security-relevant behavior by removing a risky signature-context mismatch in login handling. However, the diff does not prove that forged logins, replay, or authorization bypass were actually possible before the change, so the strongest support is for security hardening rather than a confirmed security fix.

## Security Evidence

1. RecoverPublicKeyFromSignature() is part of login/authentication handling.
2. The fix replaces hashing the current Message object with hashing a dedicated legacy identity payload.
3. The new legacy payload includes explicit fields plus HardForkName set to "curie".
4. The change makes recovery depend on a protocol-version-specific canonical signing context.
5. The substantive code change is confined to cryptographic key-recovery logic; the version bump is incidental.

## Missing Evidence

1. No call-site evidence shows recovered keys are used in an authorization decision.
2. The patch does not show that invalid signatures were previously accepted.
3. No test or exploit evidence demonstrates impersonation, forgery, or replay.
4. The diff does not change or document challenge freshness, nonce handling, or replay defenses.

## Claim Boundaries

1. Supported: the legacy Curie compatibility path used the wrong signing preimage/schema for public-key recovery.
2. Supported: the commit hardens authentication-related signature handling.
3. Not supported: attackers could definitely bypass authentication before this change.
4. Not supported: this commit fixes replay protection.
5. Not supported: the issue is proven to have caused privilege escalation or account compromise.
