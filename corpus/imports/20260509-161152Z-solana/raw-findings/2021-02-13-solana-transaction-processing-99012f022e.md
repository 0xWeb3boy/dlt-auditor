---
case_id: case_20210213_99012f022e
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2021-02-13
source_refs:
  - git:99012f022e523ea7ea5e1a2620f35623f2549d9a
  - "sdk/program/src/hash.rs:68"
  - "sdk/program/src/hash.rs:179"
  - "sdk/program/src/hash.rs:7"
bug_class: input-size-validation
impact_type:
  - parser-hardening
  - resource-exhaustion-mitigation
confidence: medium
tags:
  - solana
  - sdk
  - hash-parsing
  - base58
  - input-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a maximum base58 string length check to Solana SDK Hash parsing. Hash::from_str now rejects strings longer than 44 characters with ParseHashError::WrongSize before calling bs58::decode. This is grounded as input-size validation and parser hardening, but the evidence does not prove a vulnerability or show that oversized input causes a security impact.

## Observed Patch Facts

1. In `sdk/program/src/hash.rs`, the patch adds `if s.len() > MAX_BASE58_LEN {`.

2. In `sdk/program/src/hash.rs`, the patch replaces `let mut hash_base58_str = bs58::encode(hash.0).into_string();` with `let input_too_big = bs58::encode(&[0xffu8; HASH_BYTES + 1]).into_string();`.

3. In `sdk/program/src/hash.rs`, the patch adds `/// Maximum string length of a base58 encoded hash`.

## Project Context

The changed code sits primarily in `sdk/program/src`, `sdk/program`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sdk/program/src/pubkey.rs`, `sdk/program/src/program_error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/program/src/pubkey.rs`, `sdk/program/src/program_error.rs`. The strongest project-level identifiers around this patch are `ParseHashError::WrongSize`, `bs58::encode`, `Self::Err`, and `bs58::decode`.

## Before/After Behavior

Before the change, Hash::from_str passed the supplied string directly into bs58::decode(s).into_vec(), then checked whether the decoded byte length matched Hash size. After the change, Hash::from_str first checks s.len() > MAX_BASE58_LEN and returns ParseHashError::WrongSize before decoding. A unit test was added for an oversized base58-encoded value.

# Root Cause

The Hash base58 parser lacked a pre-decode encoded-length bound. It still checked decoded byte length afterward, so the demonstrated issue is unbounded decoder input at the parser boundary, not an established acceptance of invalid hashes.

## Walkthrough

1. A caller supplies a string to Hash::from_str.

2. Before the patch, the string was passed directly to bs58::decode.

3. The parser then checked whether the decoded byte vector had the expected Hash size.

4. The patch defines MAX_BASE58_LEN as 44 for base58-encoded hashes.

5. Hash::from_str now rejects inputs longer than MAX_BASE58_LEN before decoding.

6. The updated test verifies that an oversized encoded input returns ParseHashError::WrongSize.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/program/src/hash.rs | 7 | Defines MAX_BASE58_LEN as the accepted maximum base58-encoded length for a 32-byte Hash. |
| sdk/program/src/hash.rs | 66 | Hash FromStr parser now rejects inputs longer than MAX_BASE58_LEN before bs58 decoding. |
| sdk/program/src/hash.rs | 159 | Unit test covers oversized encoded hash input returning ParseHashError::WrongSize. |

## Code Snippets

## Snippet 1

Context: `sdk/program/src/hash.rs:68` (changes a sensitive control or state-update path)

Before
```rust
fn from_str(s: &str) -> Result<Self, Self::Err> {
        let bytes = bs58::decode(s)
            .into_vec()
```
After
```rust
fn from_str(s: &str) -> Result<Self, Self::Err> {
        if s.len() > MAX_BASE58_LEN {
            return Err(ParseHashError::WrongSize);
        }
        let bytes = bs58::decode(s)
            .into_vec()
```

## Snippet 2

Context: `sdk/program/src/hash.rs:179` (changes signature or replay validation logic)

Before
```rust
);

        let mut hash_base58_str = bs58::encode(hash.0).into_string();
        assert_eq!(hash_base58_str.parse::<Hash>(), Ok(hash));
```
After
```rust
);

        let input_too_big = bs58::encode(&[0xffu8; HASH_BYTES + 1]).into_string();
        assert!(input_too_big.len() > MAX_BASE58_LEN);
        assert_eq!(
            input_too_big.parse::<Hash>(),
            Err(ParseHashError::WrongSize)
        );
```

## Snippet 3

Context: `sdk/program/src/hash.rs:7` (changes a sensitive control or state-update path)

Before
```rust
pub const HASH_BYTES: usize = 32;
#[derive(
    Serialize, Deserialize, Clone, Copy, Default, Eq, PartialEq, Ord, PartialOrd, Hash, AbiExample,
```
After
```rust
pub const HASH_BYTES: usize = 32;
/// Maximum string length of a base58 encoded hash
const MAX_BASE58_LEN: usize = 44;
#[derive(
    Serialize, Deserialize, Clone, Copy, Default, Eq, PartialEq, Ord, PartialOrd, Hash, AbiExample,
```

# Fix Pattern

Add an early encoded-input length guard before decoding fixed-size base58 data, while retaining the decoded-byte-length check.

## How It Was Fixed

The patch introduced MAX_BASE58_LEN in sdk/program/src/hash.rs and added an early s.len() > MAX_BASE58_LEN check in Hash::from_str. Oversized input now returns ParseHashError::WrongSize before bs58 decoding.

# Why It Matters

1. Bounds parser input before decoder work.

2. Aligns Hash parsing with the shown Pubkey parsing pattern.

3. No provided evidence demonstrates consensus impact, replay impact, signature impact, memory corruption, or network-critical exploitability.

# Evidence Notes

Evidence is limited to sdk/program/src/hash.rs and related context showing a similar Pubkey parser guard. The code supports an input-size validation finding. Claims about transaction processing, cryptographic failure, replay sensitivity, storage handling, or a confirmed security vulnerability are not supported by the provided snippets. Protocol security invariant: A fixed-size 32-byte Hash parsed from base58 should reject encodings that exceed the expected maximum encoded length before decoding. The patch enforces this parser boundary, but the provided evidence does not establish a protocol-level security invariant violation or exploit path. Verification notes: No exploitability is proven by the patch alone. No consensus, signature verification, or replay invariant is shown to be bypassed before the fix. No evidence shows that oversized input reaches a network-critical path in this context. No memory corruption is indicated; Rust parsing returns errors. The patch proves input bound enforcement, not a full protocol-level vulnerability. Confirmed by diff: MAX_BASE58_LEN was added. Confirmed by diff: Hash::from_str now checks input length before bs58::decode. Confirmed by test snippet: oversized encoded input is expected to return WrongSize. Not established: exploitability or security impact beyond parser hardening. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `input-size-validation`
Final impact type: `parser-hardening, resource-exhaustion-mitigation`
Final confidence: `medium`
Final tags: `solana, sdk, hash-parsing, base58, input-validation, security-hardening`

The patch adds an explicit encoded-length bound before base58 decoding fixed-size Hash input, which is a clear parser hardening change in a security-sensitive hash type. The evidence does not prove a concrete exploitable vulnerability, consensus issue, replay bypass, or signature failure, so it should not be treated as a confirmed security fix. It is suitable for the corpus only as conservative security hardening.

## Security Evidence

1. Hash::from_str previously decoded the supplied string before enforcing the fixed 32-byte decoded size.
2. The patch rejects inputs longer than MAX_BASE58_LEN before calling bs58::decode.
3. A regression test verifies an oversized base58-encoded hash returns ParseHashError::WrongSize.
4. The same maximum-length pattern is shown for Pubkey parsing, supporting this as boundary validation for fixed-size base58 values.

## Missing Evidence

1. No exploit path or attacker-controlled entry point is shown.
2. No proof of denial of service, excessive allocation, consensus impact, replay impact, or signature validation bypass is provided.
3. No evidence shows the prior behavior accepted invalid hashes after decoded-size validation.
4. No advisory, CVE, or security note is included in the supplied metadata.

## Claim Boundaries

1. Classify as parser/input-size hardening, not a confirmed vulnerability fix.
2. Do not claim memory corruption; the code is Rust and returns parse errors.
3. Do not claim transaction-processing, replay, storage, or signature impact from the supplied snippets alone.
4. Resource-exhaustion relevance is plausible from pre-decode bounding but not demonstrated.
