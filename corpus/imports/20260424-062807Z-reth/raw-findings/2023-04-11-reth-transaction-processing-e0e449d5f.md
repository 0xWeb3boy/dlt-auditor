---
case_id: case_20230411_e0e449d5f
project: reth
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-04-11
source_refs:
  - git:e0e449d5fffd816b3a5e11df33322e56c017d41d
  - "crates/primitives/src/transaction/signature.rs:61"
  - "crates/primitives/src/transaction/signature.rs:48"
bug_class: signature-input-validation
impact_type:
  - acceptance-of-malformed-input
confidence: medium
tags:
  - signature-validation
  - input-validation
  - transaction-processing
  - ethereum
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens legacy Ethereum signature decoding in `crates/primitives/src/transaction/signature.rs` by rejecting non-`27`/`28` legacy `v` values. That is a concrete validation improvement in a security-sensitive parser, but the provided evidence does not establish a specific exploit, consensus issue, replay issue, or signature forgery bug.

## Observed Patch Facts

1. In `crates/primitives/src/transaction/signature.rs`, the patch replaces `// non-EIP-155 legacy scheme` with `// non-EIP-155 legacy scheme, v = 27 for even y-parity, v = 28 for odd y-parity`.

2. In `crates/primitives/src/transaction/signature.rs`, the patch replaces `/// This will return a chain ID if the 'v' value is EIP-155 compatible.` with `/// This will return a chain ID if the 'v' value is [EIP-155](https://github.com/ethe...`.

## Project Context

The changed code sits primarily in `crates/primitives/src/transaction`, `crates/primitives/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/primitives/src/transaction/mod.rs`, `crates/primitives/src/transaction/tx_type.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/primitives/src/transaction/mod.rs`, `crates/primitives/src/transaction/util.rs`. The strongest project-level identifiers around this patch are `odd_y_parity`, `DecodeError::Custom`, `Signature`, and `legacy`.

## Before/After Behavior

Before the patch, `Signature::decode_with_eip155_chain_id` treated `v >= 35` as EIP-155 and otherwise entered a legacy branch that computed `odd_y_parity` as `(v - 27) != 0` without first checking that legacy `v` was actually `27` or `28`. After the patch, the legacy branch documents the expected Ethereum rule, rejects any legacy `v` other than `27` or `28` with `DecodeError::Custom("invalid Ethereum signature (V is not 27 or 28)")`, and then derives parity with `v == 28`. The nearby `v()` helper already encoded legacy signatures as `27 + parity`, so the decoder now matches that canonical encoding more closely.

# Root Cause

The legacy signature decode path derived `odd_y_parity` from the raw `v` value without first enforcing the Ethereum legacy constraint that `v` must be exactly `27` or `28`. That allowed non-canonical legacy-branch inputs to be normalized instead of rejected at parse time.

## Walkthrough

1. The changed code is in `crates/primitives/src/transaction/signature.rs`, inside `Signature::decode_with_eip155_chain_id`.

2. The function decodes `(v, r, s)` and already had special handling for EIP-155-style values when `v >= 35`.

3. In the pre-patch legacy branch, the code immediately computed `let odd_y_parity = (v - 27) != 0;` and returned a `Signature` with no explicit `v` validity check.

4. The patch adds an explicit legacy check: if `v` is not `27` and not `28`, decoding returns `DecodeError::Custom("invalid Ethereum signature (V is not 27 or 28)")`.

5. After validation, the patch derives legacy parity with `let odd_y_parity = v == 28;`, which matches the documented Ethereum rule.

6. The surrounding `v()` helper in the same file already emits legacy `v` as `27 + parity`, so the fix aligns decode behavior with encode behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/primitives/src/transaction/signature.rs | 40 | Defines the canonical Ethereum `v` encoding for legacy and EIP-155 signatures. |
| crates/primitives/src/transaction/signature.rs | 48 | Decodes `(v, r, s)` and determines whether a chain ID is present. |
| crates/primitives/src/transaction/signature.rs | 61 | Validates legacy signature `v` values and now rejects non-`27`/`28` inputs instead of coercing them into parity. |

## Code Snippets

## Snippet 1

Context: `crates/primitives/src/transaction/signature.rs:61` (changes signature or replay validation logic)

Before
```rust
Ok((Signature { r, s, odd_y_parity }, Some(chain_id)))
        } else {
            // non-EIP-155 legacy scheme
            let odd_y_parity = (v - 27) != 0;
            Ok((Signature { r, s, odd_y_parity }, None))
        }
```
After
```rust
Ok((Signature { r, s, odd_y_parity }, Some(chain_id)))
        } else {
            // non-EIP-155 legacy scheme, v = 27 for even y-parity, v = 28 for odd y-parity
            if v != 27 && v != 28 {
                return Err(DecodeError::Custom("invalid Ethereum signature (V is not 27 or 28)"))
            }
            let odd_y_parity = v == 28;
            Ok((Signature { r, s, odd_y_parity }, None))
```

## Snippet 2

Context: `crates/primitives/src/transaction/signature.rs:48` (changes a sensitive control or state-update path)

Before
```rust
/// Decodes the `v`, `r`, `s` values without a RLP header.
    /// This will return a chain ID if the `v` value is EIP-155 compatible.
    pub(crate) fn decode_with_eip155_chain_id(
        buf: &mut &[u8],
```
After
```rust
/// Decodes the `v`, `r`, `s` values without a RLP header.
    /// This will return a chain ID if the `v` value is [EIP-155](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md) compatible.
    pub(crate) fn decode_with_eip155_chain_id(
        buf: &mut &[u8],
```

# Fix Pattern

Add explicit canonical-value validation at the decode boundary for signature metadata and fail closed on malformed encodings instead of normalizing them.

## How It Was Fixed

The non-EIP-155 branch now checks that legacy `v` is exactly `27` or `28`, returns a decode error otherwise, and replaces the loose parity derivation with the canonical comparison `v == 28`. The doc comment was also updated to reference EIP-155 explicitly.

# Why It Matters

1. Malformed legacy signature encodings are no longer silently mapped into an internal parity bit.

2. Decoder behavior is now consistent with the encoder's Ethereum-specific `v` scheme.

3. This reduces ambiguity in a shared transaction-signature parsing path.

4. The supplied evidence supports parser hardening, but not a proven exploitable vulnerability.

# Evidence Notes

The evidence is limited to one focused code change in `crates/primitives/src/transaction/signature.rs` plus nearby context in the same file showing the canonical encoder formula. The patch clearly adds a new rejection path for legacy `v` values outside `27`/`28`. However, the supplied material does not show downstream sender recovery behavior, transaction acceptance behavior, consensus impact, a reported exploit, or tests demonstrating a security failure before the fix. Claims stronger than signature-format validation hardening are not supported by the provided evidence. Protocol security invariant: Ethereum signature decoding should preserve the canonical `v` encoding used by the scheme: EIP-155 values use `35 + 2*chain_id + parity`, and legacy values use only `27` or `28`. The decoder should reject other legacy `v` values rather than coercing them into a parity bit. Verification notes: The patch does not prove malformed legacy `v` values could reach execution or state transition logic. The patch does not show whether sender recovery or consensus acceptance actually succeeded for every previously accepted noncanonical `v` value. The patch does not establish a concrete replay, forgery, or chain-split exploit. The patch does not prove whether pre-fix behavior for `v < 27` was wrapping, panicking, or otherwise environment-dependent. Direct evidence shows the decoder now rejects legacy `v` values other than `27` or `28`. Direct evidence shows the pre-patch code derived parity without an explicit legacy `v` validity check. No supplied evidence proves malformed signatures previously reached execution, sender recovery, or consensus-critical logic. No supplied evidence proves replay, forgery, or chain-split impact. Because the patch is in a signature parser, security relevance is plausible, but the vulnerability thesis is not established from the provided evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-input-validation`
Final impact type: `acceptance-of-malformed-input`
Final confidence: `medium`
Final tags: `signature-validation, input-validation, transaction-processing, ethereum`

The patch clearly tightens validation in a security-sensitive signature decoding path by rejecting legacy Ethereum signatures whose `v` value is not exactly `27` or `28`. That is meaningful hardening because the previous code normalized any non-EIP-155 `v` into a parity bit instead of failing closed. However, the supplied evidence does not show that malformed values were exploitable in practice, reached consensus-critical execution, enabled replay, or permitted signature forgery. The strongest supported classification from the patch alone is security hardening, not a proven security vulnerability fix.

## Security Evidence

1. Legacy signature decoding now rejects `v` values other than `27` or `28`.
2. Pre-patch code derived parity from `(v - 27) != 0` without explicit legacy-value validation.
3. The change is in `Signature::decode_with_eip155_chain_id`, a signature parsing and validation path.
4. The decoder is aligned with the encoder logic that emits legacy `v` as `27 + parity`.
5. The new behavior fails closed with `DecodeError::Custom` on malformed legacy encodings.

## Missing Evidence

1. No proof that malformed legacy `v` values were accepted into execution or consensus-critical flows.
2. No test or report showing signature forgery, replay, chain split, or sender-recovery abuse.
3. No downstream evidence that noncanonical values changed authorization or transaction acceptance semantics.
4. No exploit narrative or advisory tying this parser issue to a concrete security incident.

## Claim Boundaries

1. Supported claim: the commit hardens signature-format validation for legacy Ethereum `v` values.
2. Supported claim: pre-fix code accepted and normalized some noncanonical legacy encodings instead of rejecting them.
3. Not supported: a proven replay, forgery, or consensus-bypass vulnerability.
4. Not supported: attacker-controlled malformed signatures definitely reached security-relevant state transitions before the fix.
