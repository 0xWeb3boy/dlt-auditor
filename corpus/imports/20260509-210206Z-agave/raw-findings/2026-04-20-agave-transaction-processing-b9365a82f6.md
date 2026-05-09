---
case_id: case_20260420_b9365a82f6
project: agave
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2026-04-20
source_refs:
  - git:b9365a82f6d6930f0c5c80d4eb77718c3b39b99b
  - "transaction-view/src/sanitize.rs:106"
  - "transaction-view/src/sanitize.rs:23"
  - "transaction-view/src/sanitize.rs:63"
  - "transaction-view/src/sanitize.rs:1"
bug_class: transaction-sanitization-hardening
impact_type:
  - malformed-transaction-rejection
  - validation-hardening
confidence: medium
tags:
  - transaction-processing
  - sanitize
  - validation
  - signature-validation
  - bounds-check
  - protocol-invariants
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch strengthens and centralizes transaction-view sanitization in `transaction-view/src/sanitize.rs`, adding or reorganizing checks for transaction size, signatures, account/address limits, duplicate addresses, header fields, and config fields. These checks are security-relevant in a broad transaction-processing sense, but the evidence does not show that the previous behavior enabled an exploit, consensus failure, signature bypass, fund loss, or denial of service. Classify as unclear validation hardening/correctness, not a confirmed security fix.

## Observed Patch Facts

1. In `transaction-view/src/sanitize.rs`, the patch replaces `fn sanitize_instructions(` with `/// Accounts (aka Addresses) Constraints:`.

2. In `transaction-view/src/sanitize.rs`, the patch replaces `fn sanitize_signatures(view: &UnsanitizedTransactionView<impl TransactionData>) -> Re...` with `/// Transaction constraints:`.

3. In `transaction-view/src/sanitize.rs`, the patch replaces `// Check there is at least 1 writable fee-payer account.` with `Ok(())`.

4. In `transaction-view/src/sanitize.rs`, the patch replaces `};` with `crate::{`.

## Project Context

The changed code sits primarily in `transaction-view/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `transaction-view/src/transaction_view.rs`, `transaction-view/src/resolved_transaction_view.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `transaction-view/src/transaction_view.rs`, `transaction-view/src/resolved_transaction_view.rs`. The strongest project-level identifiers around this patch are `view`, `UnsanitizedTransactionView`, `TransactionData`, and `Result`.

## Before/After Behavior

Before the patch, the provided excerpts do not show the complete pre-patch sanitizer or prove which malformed transactions were accepted. After the patch, the sanitize flow explicitly calls message header validation, config validation, signature validation, account access validation, instruction validation, and address table lookup validation. The added checks reject invalid conditions with `TransactionViewError::SanitizeError`, including version-specific transaction size/account limits, signature count mismatches, too many signatures, insufficient static account keys for signatures, duplicate addresses, invalid header counts, and invalid requested heap size constraints.

# Root Cause

The grounded root cause is incomplete or insufficiently centralized transaction-view structural validation. It is reasonable to infer that some invariants were not previously enforced at this sanitize boundary, but the provided evidence does not prove downstream exploitability or a concrete vulnerable state transition.

## Walkthrough

1. A transaction is represented as an `UnsanitizedTransactionView<impl TransactionData>`.

2. The updated sanitize path invokes separate validation routines for message header, config, signatures, account access, instructions, and address table lookups.

3. Transaction size validation now selects a maximum based on `view.version()`.

4. Signature validation checks that provided signatures match required signatures, do not exceed `MAX_SIGNATURES_PER_PACKET`, and have corresponding static account keys.

5. Account access validation applies version-specific address/account limits and is documented to reject duplicate addresses.

6. Message header validation rejects internally inconsistent required-signature and readonly-account counts.

7. Config validation checks requested heap size constraints when transaction config is present.

8. Invalid structures now return `TransactionViewError::SanitizeError` during sanitization.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| transaction-view/src/sanitize.rs | 17 | top-level sanitize flow calls message header, config, signatures, account access, instructions, and address table lookup validation |
| transaction-view/src/sanitize.rs | 23 | transaction size validation selects maximum size by transaction version |
| transaction-view/src/sanitize.rs | 45 | message header validation enforces required signatures and writable fee payer/header consistency |
| transaction-view/src/sanitize.rs | 89 | signature validation enforces signature count, maximum signatures per packet, and static key coverage |
| transaction-view/src/sanitize.rs | 106 | account access validation enforces version-specific account/address limits and duplicate-address rejection |
| transaction-view/src/transaction_view.rs | 1 | transaction view path imports and uses sanitize before exposing parsed transaction data |
| transaction-view/src/resolved_transaction_view.rs | 1 | resolved transaction view depends on sanitized transaction view semantics |

## Code Snippets

## Snippet 1

Context: `transaction-view/src/sanitize.rs:106` (changes a sensitive control or state-update path)

Before
```rust
}

fn sanitize_instructions(
    view: &UnsanitizedTransactionView<impl TransactionData>,
```
After
```rust
}

/// Accounts (aka Addresses) Constraints:
/// * for v1: 1 <= NumAddresses <= 64
///   * legacy/v0 uses current limits of: num_accounts <= 256 (u8 bound)
/// * No duplicate addresses
fn sanitize_account_access(view: &UnsanitizedTransactionView<impl TransactionData>) -> Result<()> {
    let addresses_limit = match view.version() {
```

## Snippet 2

Context: `transaction-view/src/sanitize.rs:23` (changes a sensitive control or state-update path)

Before
```rust
}

fn sanitize_signatures(view: &UnsanitizedTransactionView<impl TransactionData>) -> Result<()> {
    // Check the required number of signatures matches the number of signatures.
    if view.num_signatures() != view.num_required_signatures() {
        return Err(TransactionViewError::SanitizeError);
    }
```
After
```rust
}

/// Transaction constraints:
/// * size <= 4096 bytes
fn sanitize_transaction_size(
    view: &UnsanitizedTransactionView<impl TransactionData>,
) -> Result<()> {
    let max_transaction_size = match view.version() {
```

## Snippet 3

Context: `transaction-view/src/sanitize.rs:63` (changes a sensitive control or state-update path)

Before
```rust
}

    // Check there is at least 1 writable fee-payer account.
    if view.num_readonly_signed_static_accounts() >= view.num_required_signatures() {
        return Err(TransactionViewError::SanitizeError);
    }

    // Check there are not more than 256 accounts.
```
After
```rust
}

    Ok(())
}

/// Config Constraints:
/// * heap_size must be multiples of 1024, if specified
fn sanitize_config(view: &UnsanitizedTransactionView<impl TransactionData>) -> Result<()> {
```

## Snippet 4

Context: `transaction-view/src/sanitize.rs:1` (changes a sensitive control or state-update path)

Before
```rust
use crate::{
    result::{Result, TransactionViewError},
    transaction_data::TransactionData,
    transaction_view::UnsanitizedTransactionView,
};
```
After
```rust
use {
    crate::{
        result::{Result, TransactionViewError},
        signature_frame::MAX_SIGNATURES_PER_PACKET,
        transaction_data::TransactionData,
        transaction_version::TransactionVersion,
        transaction_view::UnsanitizedTransactionView,
    },
```

# Fix Pattern

Centralize structural validation at the transaction-view sanitize boundary and make protocol limits explicit and version-aware.

## How It Was Fixed

`transaction-view/src/sanitize.rs` was updated to import needed version/signature constants, add version-selected transaction size validation, include centralized signature validation, enforce version-specific account/address limits, reject duplicate addresses, and keep header/config checks in the top-level sanitize flow. Invalid inputs fail with `TransactionViewError::SanitizeError`.

# Why It Matters

1. Prevents downstream code from relying on malformed transaction-view structures.

2. Makes version-specific transaction bounds explicit.

3. Improves consistency of signature and account metadata validation.

4. Security relevance is plausible, but concrete vulnerability impact is not shown.

# Evidence Notes

Evidence is limited to commit metadata and excerpts from `transaction-view/src/sanitize.rs` plus related import/use context. The excerpts support that validation was added or reorganized in a critical transaction-view path. They do not include a full pre-patch sanitizer, failing test case, exploit transaction, advisory, or demonstrated impact. Claims of signature-verification bypass, consensus split, fund loss, or denial of service are unsupported. Protocol security invariant: Transaction views should be rejected during sanitization when their encoded structure violates protocol or implementation bounds, including version-specific size and account/address limits, signature count consistency, static-key coverage for signatures, duplicate addresses, and internally valid header/config fields. The provided evidence supports this as a validation invariant, but does not establish a security vulnerability or exploit impact. Verification notes: No concrete exploit transaction is shown in the provided evidence. No bypass of cryptographic signature verification is proven. No consensus split, fund loss, or denial-of-service impact is demonstrated by the patch alone. Some changes may be correctness or protocol-compliance cleanup rather than a vulnerability fix. The exact pre-patch downstream behavior after accepting malformed views is not shown. No exploit path is demonstrated by the provided evidence. No concrete malformed transaction accepted before the patch is proven. No security advisory or CVE-style impact is provided. Treat helper or related files as supporting context only. Keep out of the security corpus unless additional evidence establishes vulnerability impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-sanitization-hardening`
Final impact type: `malformed-transaction-rejection, validation-hardening`
Final confidence: `medium`
Final tags: `transaction-processing, sanitize, validation, signature-validation, bounds-check, protocol-invariants`

The evidence supports a security-hardening classification rather than a confirmed security fix. The patch centralizes and expands transaction-view sanitization in a security-sensitive transaction-processing path, adding or moving checks for transaction size, signature consistency, maximum signatures, static key coverage, account/address limits, duplicate addresses, header consistency, and heap-size constraints. However, the supplied evidence does not prove an exploitable pre-patch vulnerability, accepted exploit transaction, consensus failure, fund loss, or denial-of-service impact.

## Security Evidence

1. Top-level sanitize flow now invokes message header, config, signature, account access, instruction, and address table lookup validation.
2. Signature sanitization rejects mismatched required/provided signatures, excessive signatures, and insufficient static account keys for signatures.
3. Account access sanitization applies version-specific address/account limits and documents duplicate-address rejection.
4. Transaction size sanitization applies version-specific maximum transaction size limits.
5. Invalid transaction structures return TransactionViewError::SanitizeError in a transaction-processing boundary.

## Missing Evidence

1. No full pre-patch sanitizer is provided to prove exactly which malformed transactions were previously accepted.
2. No exploit transaction, failing test demonstrating vulnerable behavior, advisory, or CVE-style impact is supplied.
3. No demonstrated signature bypass, consensus split, fund loss, or denial-of-service path is shown.
4. Some changes may be reorganization or protocol-compliance cleanup rather than remediation of a concrete vulnerability.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Do not claim cryptographic signature verification bypass from the supplied evidence.
3. Do not claim consensus, fund-loss, or denial-of-service impact without additional proof.
4. Supported claim is limited to stricter transaction-view structural validation in a security-sensitive path.
