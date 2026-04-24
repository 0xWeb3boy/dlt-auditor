---
case_id: case_20220723_87d5950c06
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2022-07-23
source_refs:
  - git:87d5950c06dfc8cd8931ffe89ebcce4cd8c9060d
  - "crates/sui-types/src/crypto.rs:601"
  - "crates/sui-types/src/crypto.rs:643"
  - "crates/sui-types/src/messages_checkpoint.rs:385"
  - "crates/sui-types/src/messages_checkpoint.rs:436"
bug_class: signing-type-registration-hardening
impact_type:
  - signature-integrity
confidence: medium
tags:
  - cryptography
  - signature
  - bcs
  - trait-sealing
  - type-safety
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch centralizes and seals BcsSignable registration for types that use BCS-based signing helpers. This is security-adjacent hardening of a sensitive signing serialization boundary, but the provided evidence does not establish a concrete vulnerability, exploit path, or prior unsafe behavior beyond distributed trait implementations.

## Observed Patch Facts

1. In `crates/sui-types/src/crypto.rs`, the patch replaces `pub trait BcsSignable: Serialize + serde::de::DeserializeOwned {}` with `///`.

2. In `crates/sui-types/src/crypto.rs`, the patch replaces `T: BcsSignable,` with `T: bcs_signable::BcsSignable,`.

3. In `crates/sui-types/src/messages_checkpoint.rs`, the patch removes `impl BcsSignable for CheckpointContents {}`.

4. In `crates/sui-types/src/messages_checkpoint.rs`, the patch removes `impl BcsSignable for CheckpointProposalSummary {}`.

## Project Context

The changed code sits primarily in `crates/sui-types/src`, `crates/sui-types`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-types/src/signature_seed.rs`, `crates/sui-types/src/messages.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/signature_seed.rs`, `crates/sui-types/src/messages.rs`. The strongest project-level identifiers around this patch are `serde_name::trace_name`, `BcsSignable`, `name`, and `serde_name`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/waypoint_tests.rs`, `crates/sui-types/src/unit_tests/messages_tests.rs`.

## Before/After Behavior

Before the patch, BcsSignable was a public marker trait that could be implemented outside the crypto module, and SignableBytes applied to any T: BcsSignable. Checkpoint types implemented the marker locally in messages_checkpoint.rs. After the patch, the generic signing-byte implementation depends on bcs_signable::BcsSignable, with comments describing a sealed trait pattern and a requirement that implementations be registered centrally and comply with serde_name assumptions. The trace_name failure path changed from returning an error to expect(), relying on the new registration invariant.

# Root Cause

The supported root cause is weak compile-time control over which serializable types could opt into BCS signing helpers. The evidence does not show that this caused signature forgery, consensus failure, malformed-input denial of service, or another concrete vulnerability.

## Walkthrough

1. The crypto module uses serde_name and BCS to build signable bytes for hashing and signing.

2. Before the change, BcsSignable was an open public marker trait.

3. Any module defining a suitable type could add a local BcsSignable implementation.

4. CheckpointContents and CheckpointProposalSummary had local BcsSignable implementations in messages_checkpoint.rs.

5. The patch introduces or moves to a sealed bcs_signable module as the registration point.

6. The SignableBytes blanket implementation now requires bcs_signable::BcsSignable.

7. The code now uses expect() for serde_name::trace_name, relying on the stated invariant that registered types must be compatible with serde_name.

8. The provided evidence supports centralization and reviewability, not a proven vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/crypto.rs | 601 | Defines the BCS signable marker and changes it into a sealed registration surface for audited signable types. |
| crates/sui-types/src/crypto.rs | 643 | Applies SignableBytes only to sealed BcsSignable types and relies on the registration invariant when calling serde_name::trace_name. |
| crates/sui-types/src/messages_checkpoint.rs | 385 | Removes direct local BcsSignable implementation for CheckpointContents, indicating signable registration is no longer distributed in the checkpoint module. |
| crates/sui-types/src/messages_checkpoint.rs | 436 | Removes direct local BcsSignable implementation for CheckpointProposalSummary, moving checkpoint signing eligibility into the centralized registry. |

## Code Snippets

## Snippet 1

Context: `crates/sui-types/src/crypto.rs:601` (changes a consensus- or validator-sensitive branch)

Before
```rust
/// * We use `serde_name` to extract a seed from the name of structs and enums.
/// * We use `BCS` to generate canonical bytes suitable for hashing and signing.
pub trait BcsSignable: Serialize + serde::de::DeserializeOwned {}

impl<T, W> Signable<W> for T
where
    T: BcsSignable,
    W: std::io::Write,
```
After
```rust
/// * We use `serde_name` to extract a seed from the name of structs and enums.
/// * We use `BCS` to generate canonical bytes suitable for hashing and signing.
///
/// # Safety
/// We protect the access to this marker trait through a "sealed trait" pattern:
/// impls must be add added here (nowehre else) which lets us note those impls
/// MUST be on types that comply with the `serde_name` machinery
/// for the below implementations not to panic. One way to check they work is to write
```

## Snippet 2

Context: `crates/sui-types/src/crypto.rs:643` (changes the branch that decides whether execution stops or continues)

Before
```rust
impl<T> SignableBytes for T
where
    T: BcsSignable,
{
    fn from_signable_bytes(bytes: &[u8]) -> Result<Self, Error> {
        // Remove name tag before deserialization using BCS
        let name = serde_name::trace_name::<Self>()
            .ok_or_else(|| anyhow::anyhow!("Self should be a struct or an enum"))?;
```
After
```rust
impl<T> SignableBytes for T
where
    T: bcs_signable::BcsSignable,
{
    fn from_signable_bytes(bytes: &[u8]) -> Result<Self, Error> {
        // Remove name tag before deserialization using BCS
        let name = serde_name::trace_name::<Self>().expect("Self should be a struct or an enum");
        let name_byte_len = format!("{}::", name).bytes().len();
```

## Snippet 3

Context: `crates/sui-types/src/messages_checkpoint.rs:385` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

impl BcsSignable for CheckpointContents {}

// TODO: We should create a type for ordered contents,
// instead of mixing them in the same type.
```
After
```rust
}

// TODO: We should create a type for ordered contents,
// instead of mixing them in the same type.
```

## Snippet 4

Context: `crates/sui-types/src/messages_checkpoint.rs:436` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

impl BcsSignable for CheckpointProposalSummary {}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SignedCheckpointProposalSummary {
```
After
```rust
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SignedCheckpointProposalSummary {
```

# Fix Pattern

Replace a broadly implementable public marker trait on a signing helper boundary with a sealed, centralized registration surface.

## How It Was Fixed

The patch changes SignableBytes bounds to use the sealed bcs_signable::BcsSignable trait, adds safety documentation requiring centralized registration and serde_name compatibility, and removes local BcsSignable implementations from checkpoint message types.

# Why It Matters

1. BCS signing helpers are security-sensitive code.

2. Centralized registration makes signable type eligibility easier to audit.

3. The serde_name assumption is now documented as an invariant.

4. No concrete exploitability is demonstrated by the supplied evidence.

# Evidence Notes

The evidence shows trait sealing, centralized registration, removed local marker implementations, and a changed trace_name error path. It does not show malformed network input, signature confusion, replay, consensus divergence, storage corruption, or a confirmed denial-of-service path. The commit message frames the change as increasing scrutiny, which supports security relevance but not a validated vulnerability fix. Protocol security invariant: Only centrally reviewed types should be eligible for BCS-based signing helpers, and those types must be compatible with the serde_name-derived name machinery used by the signing-byte implementation. Verification notes: No concrete malformed network input path is shown. No exploitability or signature forgery is proven by the patch. No added runtime validation is shown; the main control is compile-time trait sealing. The expect() change is justified only by the sealed registration invariant, not by new input checks. The evidence supports hardening of signing type eligibility, not a confirmed consensus or storage corruption fix. No external context was used. No files or commands were inspected. Classification was downgraded from likely security-hardening kept in corpus to unclear and excluded from the security corpus due to lack of a demonstrated vulnerability thesis. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signing-type-registration-hardening`
Final impact type: `signature-integrity`
Final confidence: `medium`
Final tags: `cryptography, signature, bcs, trait-sealing, type-safety, security-hardening`

The supplied evidence supports retaining this as security hardening, not as a concrete vulnerability fix. The patch restricts a public marker trait used by BCS signing helpers behind a sealed, centralized registration pattern, and the commit text explicitly frames the change as protecting sensitive functions and increasing scrutiny. The evidence does not prove an exploitable bug, liveness failure, consensus failure, or denial of service, so the original liveness-focused metadata is too specific and should be replaced with a conservative hardening classification.

## Security Evidence

1. BcsSignable is used to enable generic BCS-based Signable and SignableBytes implementations for hashing and signing.
2. The patch changes the bound from the public BcsSignable trait to bcs_signable::BcsSignable, indicating a sealed trait registration surface.
3. Safety comments state implementations must be added centrally and must comply with serde_name assumptions to avoid panics.
4. Local BcsSignable implementations are removed from checkpoint message types, consistent with moving eligibility into one audited location.
5. The commit subject and body explicitly describe protecting BcsSignable and increasing scrutiny over sensitive functions.

## Missing Evidence

1. No malformed input, network path, or attacker-controlled flow is shown.
2. No signature forgery, replay, type-confusion exploit, or consensus divergence is demonstrated.
3. No prior unsafe implementation outside the intended set is identified.
4. No concrete denial-of-service path is proven from the trace_name error handling change.

## Claim Boundaries

1. Validate only as security hardening of a signing eligibility boundary.
2. Do not claim a confirmed vulnerability or exploit fix.
3. Do not retain the liveness-failure classification from the generated finding.
4. Do not claim consensus, storage, or validator safety impact beyond the signing helper boundary shown in the patch.
