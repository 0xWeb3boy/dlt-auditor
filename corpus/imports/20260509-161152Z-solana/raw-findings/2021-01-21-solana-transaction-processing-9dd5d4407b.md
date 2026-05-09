---
case_id: case_20210121_9dd5d4407b
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2021-01-21
source_refs:
  - git:9dd5d4407bc1fbfa78feba57a467919ee03c4391
  - "sdk/src/signature.rs:144"
  - "sdk/program/src/pubkey.rs:61"
  - "sdk/src/signature.rs:530"
  - "sdk/program/src/pubkey.rs:342"
bug_class: input-bound-validation
impact_type:
  - resource-exhaustion-hardening
confidence: medium
tags:
  - input-validation
  - parser-hardening
  - base58
  - pubkey
  - signature
  - sdk
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds pre-decode maximum encoded-length checks to Solana SDK `Signature::from_str` and `Pubkey::from_str`. This is grounded input hardening for base58 parsing, but the provided evidence does not establish a concrete vulnerability, attacker entry point, denial-of-service impact, signature bypass, key substitution, replay issue, or consensus effect.

## Observed Patch Facts

1. In `sdk/src/signature.rs`, the patch adds `if s.len() > MAX_BASE58_SIGNATURE_LEN {`.

2. In `sdk/program/src/pubkey.rs`, the patch adds `if s.len() > MAX_BASE58_LEN {`.

3. In `sdk/src/signature.rs`, the patch adds `// too long input string`.

4. In `sdk/program/src/pubkey.rs`, the patch adds `// too long input string`.

## Project Context

The changed code sits primarily in `sdk/src`, `sdk/program/src`, `sdk/program`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sdk/program/src/hash.rs`, `sdk/src/genesis_config.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/program/src/hash.rs`, `sdk/src/genesis_config.rs`. The strongest project-level identifiers around this patch are `Self::Err`, `bs58::decode`, `too_long`, and `ParsePubkeyError::WrongSize`.

## Before/After Behavior

Before the patch, `Signature::from_str` and `Pubkey::from_str` called `bs58::decode(s).into_vec()` before checking whether the decoded byte length matched the fixed signature or public key size. After the patch, each parser first rejects strings longer than the relevant maximum base58 length with `WrongSize`, then proceeds to decode and perform the existing decoded-size check. Tests were added for overlong base58 inputs in both parsers.

# Root Cause

The parser boundary lacked an encoded-string length bound before base58 decoding, so overlong inputs that could not be valid fixed-size signatures or public keys still reached decode logic.

## Walkthrough

1. A caller passes a string to `Signature::from_str` or `Pubkey::from_str`.

2. Before the change, the parser immediately invoked `bs58::decode(s).into_vec()`.

3. The parser then checked whether the decoded bytes had the exact fixed size and returned `WrongSize` on mismatch.

4. The patch adds an early encoded-length check using `MAX_BASE58_SIGNATURE_LEN` for signatures and `MAX_BASE58_LEN` for public keys.

5. Overlong inputs now return `WrongSize` before base58 decoding is attempted.

6. Regression tests construct a longest valid encoding, append one extra character, and assert `WrongSize` for both signatures and public keys.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/src/signature.rs | 144 | Adds maximum base58 encoded-length guard before decoding a signature string. |
| sdk/program/src/pubkey.rs | 61 | Adds maximum base58 encoded-length guard before decoding a public key string. |
| sdk/src/signature.rs | 530 | Adds regression coverage for overlong base58 signature input returning `WrongSize`. |
| sdk/program/src/pubkey.rs | 342 | Adds regression coverage for overlong base58 pubkey input returning `WrongSize`. |

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

Context: `sdk/program/src/pubkey.rs:61` (changes a sensitive control or state-update path)

Before
```rust
fn from_str(s: &str) -> Result<Self, Self::Err> {
        let pubkey_vec = bs58::decode(s)
            .into_vec()
```
After
```rust
fn from_str(s: &str) -> Result<Self, Self::Err> {
        if s.len() > MAX_BASE58_LEN {
            return Err(ParsePubkeyError::WrongSize);
        }
        let pubkey_vec = bs58::decode(s)
            .into_vec()
```

## Snippet 3

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
        let mut too_long: GenericArray<u8, U64> = GenericArray::default();
        // *sigh*
        for i in &mut too_long {
```

## Snippet 4

Context: `sdk/program/src/pubkey.rs:342` (changes persisted or aggregate state handling)

Before
```rust
Err(ParsePubkeyError::Invalid)
        );
    }
```
After
```rust
Err(ParsePubkeyError::Invalid)
        );

        // too long input string
        // longest valid encoding
        let mut too_long = bs58::encode(&[255u8; PUBKEY_BYTES]).into_string();
        // and one to grow on
        too_long.push('1');
```

# Fix Pattern

Add explicit maximum encoded-length validation at the parser boundary before invoking base58 decoding for fixed-size values, while retaining post-decode exact-size validation.

## How It Was Fixed

`sdk/src/signature.rs` now checks `s.len() > MAX_BASE58_SIGNATURE_LEN` before `bs58::decode` and returns `ParseSignatureError::WrongSize`. `sdk/program/src/pubkey.rs` now checks `s.len() > MAX_BASE58_LEN` before `bs58::decode` and returns `ParsePubkeyError::WrongSize`. Tests in both files cover overlong base58 input.

# Why It Matters

1. Bounds parser work for invalid overlong encoded inputs.

2. Makes the maximum valid representation explicit for fixed-size cryptographic values.

3. Evidence supports parser hardening, not a proven exploitable vulnerability.

4. No concrete remote or protocol-level attack path is shown.

# Evidence Notes

Primary evidence is limited to implementation and tests in `sdk/src/signature.rs` and `sdk/program/src/pubkey.rs`. The changed code clearly adds early length guards before `bs58::decode`. The tests clearly assert `WrongSize` for overlong base58 strings. Claims about transaction processing, replay-sensitive logic, state corruption, cryptographic bypass, or concrete denial of service are unsupported by the provided snippets. Protocol security invariant: Fixed-size SDK cryptographic values such as public keys and signatures should reject base58 strings longer than the maximum valid encoded representation before attempting decode, while still enforcing exact decoded byte length afterward. Verification notes: The patch does not show that overlong inputs were accepted as valid pubkeys or signatures. The patch does not prove signature forgery, key substitution, replay, or consensus-state corruption. The patch does not identify a concrete remote entry point or attacker-controlled protocol message path. The patch supports input-bound hardening, but exact denial-of-service impact is not proven from the provided evidence alone. Verified from provided diff snippets only; no file inspection or external context used. Security impact is not established beyond input hardening. Helper or test additions are treated as support evidence, not root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `input-bound-validation`
Final impact type: `resource-exhaustion-hardening`
Final confidence: `medium`
Final tags: `input-validation, parser-hardening, base58, pubkey, signature, sdk`

The evidence supports retaining this as security hardening, not as a proven security fix. The patch adds explicit maximum encoded-length checks before base58 decoding for fixed-size cryptographic identifiers, reducing exposure to overlong attacker-controlled input reaching decode logic. However, the supplied evidence does not prove an exploitable denial of service, remote entry point, consensus impact, signature bypass, or key substitution issue.

## Security Evidence

1. Adds pre-decode length guard in Signature::from_str for strings longer than MAX_BASE58_SIGNATURE_LEN.
2. Adds pre-decode length guard in Pubkey::from_str for strings longer than MAX_BASE58_LEN.
3. Changed code parses signatures and public keys, which are security-sensitive fixed-size cryptographic values.
4. Regression tests assert overlong base58 encodings are rejected with WrongSize.

## Missing Evidence

1. No concrete attacker-controlled entry point is shown.
2. No measured or demonstrated denial-of-service condition is shown.
3. No evidence that overlong inputs were accepted as valid signatures or public keys.
4. No proof of signature forgery, key substitution, replay, or consensus impact.

## Claim Boundaries

1. Classify as parser/input hardening only.
2. Do not claim a concrete exploitable vulnerability from this evidence.
3. Do not claim authentication, signature verification, replay, or consensus bypass.
4. Do not claim impact beyond bounding invalid overlong base58 input before decode.
