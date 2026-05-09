---
case_id: case_20210120_2783aee483
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2021-01-20
source_refs:
  - git:2783aee4839cad19f5c77a40bac498a071930f45
  - "sdk/src/signature.rs:144"
  - "sdk/src/signature.rs:530"
  - "sdk/src/signature.rs:59"
bug_class: input-validation
impact_type:
  - resource-exhaustion-hardening
confidence: medium
tags:
  - signature-parsing
  - base58
  - input-validation
  - resource-bound
  - sdk
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an early maximum-length check to Solana SDK signature parsing before calling `bs58::decode`. This is grounded as input validation and parser resource-bound hardening, but the provided evidence does not establish a concrete vulnerability such as authentication bypass, replay, consensus failure, or demonstrated denial of service.

## Observed Patch Facts

1. In `sdk/src/signature.rs`, the patch adds `if s.len() > MAX_BASE58_SIGNATURE_LEN {`.

2. In `sdk/src/signature.rs`, the patch adds `// too long input string`.

3. In `sdk/src/signature.rs`, the patch replaces `#[derive(` with `/// Number of bytes in a signature`.

## Project Context

The changed code sits primarily in `sdk/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sdk/src/genesis_config.rs`, `sdk/src/commitment_config.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/genesis_config.rs`, `sdk/src/commitment_config.rs`. The strongest project-level identifiers around this patch are `ParseSignatureError::WrongSize`, `Self::Err`, `bs58::decode`, and `ParseSignatureError::Invalid`.

## Before/After Behavior

Before the change, `Signature::from_str` passed the supplied string directly to `bs58::decode(s).into_vec()` and only afterward checked whether the decoded byte length matched the signature size. After the change, the code defines `SIGNATURE_BYTES = 64` and `MAX_BASE58_SIGNATURE_LEN = 88`, rejects strings longer than 88 characters with `ParseSignatureError::WrongSize` before decode, and retains the decoded-length check before constructing a `Signature`. A test now verifies that an overlong base58 string returns `WrongSize`.

# Root Cause

The parser did not enforce the maximum possible encoded length for a 64-byte signature before invoking the base58 decoder. The evidence supports inefficient or overly permissive parsing of impossible-length inputs, but not a proven security exploit.

## Walkthrough

1. A caller provides a string to `Signature::from_str`.

2. Before the patch, the string was sent directly to `bs58::decode(s).into_vec()`.

3. Decode failures were mapped to `ParseSignatureError::Invalid`.

4. After decode, the parser checked whether the decoded byte vector length matched the size of `Signature`.

5. The patch adds constants for the 64-byte signature size and 88-character maximum base58 signature length.

6. The patched parser rejects inputs longer than 88 characters before invoking the base58 decoder.

7. Regression coverage constructs an overlong base58 string and asserts that parsing returns `ParseSignatureError::WrongSize`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/src/signature.rs | 59 | Defines SIGNATURE_BYTES and MAX_BASE58_SIGNATURE_LEN used to bound signature parsing. |
| sdk/src/signature.rs | 144 | Rejects base58 signature strings longer than the maximum valid encoding before bs58::decode. |
| sdk/src/signature.rs | 530 | Adds regression coverage that an overlong base58 signature string returns ParseSignatureError::WrongSize. |

## Code Snippets

## Snippet 1

Context: `sdk/src/signature.rs:144` (changes a sensitive control or state-update path)

Before
```rust
fn from_str(s: &str) -> Result<Self, Self::Err> {
        let bytes = bs58::decode(s)
            .into_vec()
```
After
```rust
fn from_str(s: &str) -> Result<Self, Self::Err> {
        if s.len() > MAX_BASE58_SIGNATURE_LEN {
            return Err(ParseSignatureError::WrongSize);
        }
        let bytes = bs58::decode(s)
            .into_vec()
```

## Snippet 2

Context: `sdk/src/signature.rs:530` (changes signature or replay validation logic)

Before
```rust
Err(ParseSignatureError::Invalid)
        );
    }
```
After
```rust
Err(ParseSignatureError::Invalid)
        );

        // too long input string
        // longest valid encoding
        let mut too_long = bs58::encode(&[255u8; SIGNATURE_BYTES]).into_string();
        // and one to grow on
        too_long.push('1');
```

## Snippet 3

Context: `sdk/src/signature.rs:59` (changes a sensitive control or state-update path)

Before
```rust
}

#[repr(transparent)]
#[derive(
```
After
```rust
}

/// Number of bytes in a signature
pub const SIGNATURE_BYTES: usize = 64;
/// Maximum string length of a base58 encoded signature
const MAX_BASE58_SIGNATURE_LEN: usize = 88;

#[repr(transparent)]
```

# Fix Pattern

Add a pre-decode length bound at the parser boundary, using explicit constants for the expected byte size and maximum encoded length while preserving the existing decoded-size validation.

## How It Was Fixed

The fix introduced `SIGNATURE_BYTES` and `MAX_BASE58_SIGNATURE_LEN` in `sdk/src/signature.rs`, then added an early guard in `Signature::from_str` that returns `ParseSignatureError::WrongSize` when the input string is longer than 88 characters. Existing base58 decoding and decoded-length validation remain for inputs within the encoded-length bound. A regression test covers overlong input.

# Why It Matters

1. Bounds untrusted signature text before decoder work begins.

2. Makes the valid signature size and encoded-length limit explicit.

3. Preserves the requirement that only exactly 64 decoded bytes can become a `Signature`.

4. Does not prove authentication bypass, replay, consensus divergence, or quantified denial-of-service impact.

# Evidence Notes

Primary evidence is limited to `sdk/src/signature.rs`: new constants near line 59, the pre-decode guard in `Signature::from_str` near line 144, and the overlong-input test near line 530. Related traced files provide SDK context only and are not part of the fix. The commit subject says sanitize base58 signature input, but the supplied evidence does not show exploitability or a security impact beyond parser hardening. Protocol security invariant: A base58-encoded SDK signature string should be no longer than the maximum possible encoding for a 64-byte signature, and a parsed Signature should only be constructed from exactly 64 decoded bytes. Verification notes: No evidence that signature verification correctness changed. No proof of transaction authentication bypass. No proof of replay vulnerability or consensus divergence. No quantified remote denial-of-service impact is shown by the patch alone. Related traced files show surrounding SDK context but are not part of the fix. Downgraded from likely security-hardening to unclear because no concrete vulnerability impact is established. Kept subsystem as SDK signature parsing, not broader transaction processing. Kept bug class as input-validation/resource-bound because the code adds a length guard before decoding. Set `keep_in_security_corpus` to false under the instruction for unclear security relevance. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `input-validation`
Final impact type: `resource-exhaustion-hardening`
Final confidence: `medium`
Final tags: `signature-parsing, base58, input-validation, resource-bound, sdk`

The patch adds a hard maximum encoded-length check before decoding a base58 signature string, preventing impossible overlong inputs from reaching `bs58::decode`. The evidence does not prove a concrete exploitable vulnerability, but it does clearly tighten parsing behavior in a security-sensitive signature type and bounds decoder work at an input boundary, which supports retaining it as security hardening rather than a confirmed security fix.

## Security Evidence

1. `Signature::from_str` now rejects inputs longer than `MAX_BASE58_SIGNATURE_LEN` before calling `bs58::decode`.
2. The affected type is a cryptographic signature representation with fixed decoded size of 64 bytes.
3. The added test explicitly covers an overlong base58 signature string returning `ParseSignatureError::WrongSize`.
4. The commit subject says `Sanitize base58 signature input`, matching the observed parser-boundary hardening.

## Missing Evidence

1. No exploit scenario or advisory is provided.
2. No evidence shows the parser is remotely reachable in a high-impact path.
3. No quantified CPU or memory denial-of-service impact is demonstrated.
4. No authentication bypass, replay, consensus failure, or signature verification correctness change is shown.

## Claim Boundaries

1. Classify as security hardening, not a proven vulnerability fix.
2. Do not claim transaction authentication bypass or replay prevention.
3. Do not claim consensus impact from the supplied patch alone.
4. The supported claim is bounded pre-decode validation for overlong base58 signature input.
