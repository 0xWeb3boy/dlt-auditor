---
case_id: case_20200427_9c6f613f8c
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2020-04-27
source_refs:
  - git:9c6f613f8c2074f07a8225cbb2dbe1a954b2d51c
  - "core/src/crds_value.rs:78"
  - "core/src/epoch_slots.rs:219"
  - "core/src/crds_value.rs:173"
  - "sdk/src/transaction.rs:88"
bug_class: protocol-input-validation
tags:
  - protocol-input-validation
  - deserialization
  - sanitization
  - gossip
  - transaction-validation
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely security fix for missing sanitization of deserialized Solana protocol objects. The patch adds explicit `Sanitize` implementations and structural checks for `CrdsData`, `Vote`, `EpochSlots`, and `Transaction`. The commit subject claims financial impact, but the provided hunks do not establish the exact SOL-earning mechanism, exploit path, or affected call sites.

## Observed Patch Facts

1. In `core/src/crds_value.rs`, the patch replaces `#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]` with `impl Sanitize for CrdsData {`.

2. In `core/src/epoch_slots.rs`, the patch replaces `impl EpochSlots {` with `impl Sanitize for EpochSlots {`.

3. In `core/src/crds_value.rs`, the patch replaces `impl Vote {` with `impl Sanitize for Vote {`.

4. In `sdk/src/transaction.rs`, the patch replaces `impl Transaction {` with `impl Sanitize for Transaction {`.

## Project Context

The changed code sits primarily in `core/src`, `sdk/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `sdk/src/sanitize.rs`, `core/src/contact_info.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/contact_info.rs`, `sdk/src/message.rs`. The strongest project-level identifiers around this patch are `sanitize`, `SanitizeError`, `impl`, and `std::result::Result`.

## Before/After Behavior

Before the patch, the shown CRDS, vote, epoch-slot, and transaction structures were serializable/deserializable without the shown explicit local sanitization implementations. After the patch, those types reject out-of-range CRDS vote indices, excessive wallclock values, invalid nested fields via recursive `sanitize()` calls, and transactions whose signature counts are inconsistent with required signatures or account keys.

# Root Cause

Missing type-level validation for deserialized protocol objects. The supplied evidence shows that malformed CRDS data, votes, epoch slots, or transactions could be represented unless equivalent validation occurred elsewhere; it does not show whether all deserialization paths actually accepted such values unchecked.

## Walkthrough

1. `CrdsData` gains a `Sanitize` implementation that dispatches validation by enum variant.

2. `CrdsData::Vote` now rejects vote indices greater than or equal to `MAX_VOTES`.

3. `Vote` now rejects wallclocks greater than or equal to `MAX_WALLCLOCK`, validates `from`, and sanitizes the embedded transaction.

4. `EpochSlots` now rejects wallclocks greater than or equal to `MAX_WALLCLOCK`, validates `from`, and sanitizes its slot vector.

5. `Transaction` now checks required-signature and signature/account-key count consistency before sanitizing its message.

6. The shared `Sanitize` trait and `SanitizeError` enum provide the validation contract used by the new checks.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/crds_value.rs | 78 | Adds CRDS data sanitization dispatch and rejects out-of-range vote indices before nested values are accepted. |
| core/src/crds_value.rs | 173 | Adds vote sanitization for wallclock bounds, vote source pubkey, and embedded transaction validity. |
| core/src/epoch_slots.rs | 219 | Adds epoch-slot sanitization for wallclock bounds, source pubkey, and slot vector contents. |
| sdk/src/transaction.rs | 88 | Adds transaction structural checks tying required signatures, signature vector length, and account key count before message sanitization. |
| sdk/src/sanitize.rs | 1 | Defines the Sanitize trait and error categories used by the new validation path. |

## Code Snippets

## Snippet 1

Context: `core/src/crds_value.rs:78` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct SnapshotHash {
```
After
```rust
}

impl Sanitize for CrdsData {
    fn sanitize(&self) -> Result<(), SanitizeError> {
        match self {
            CrdsData::ContactInfo(val) => val.sanitize(),
            CrdsData::Vote(ix, val) => {
                if *ix >= MAX_VOTES {
```

## Snippet 2

Context: `core/src/epoch_slots.rs:219` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

impl EpochSlots {
    pub fn new(from: Pubkey, now: u64) -> Self {
```
After
```rust
}

impl Sanitize for EpochSlots {
    fn sanitize(&self) -> std::result::Result<(), SanitizeError> {
        if self.wallclock >= MAX_WALLCLOCK {
            return Err(SanitizeError::ValueOutOfRange);
        }
        self.from.sanitize()?;
```

## Snippet 3

Context: `core/src/crds_value.rs:173` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

impl Vote {
    pub fn new(from: &Pubkey, transaction: Transaction, wallclock: u64) -> Self {
```
After
```rust
}

impl Sanitize for Vote {
    fn sanitize(&self) -> Result<(), SanitizeError> {
        if self.wallclock >= MAX_WALLCLOCK {
            return Err(SanitizeError::Failed);
        }
        self.from.sanitize()?;
```

## Snippet 4

Context: `sdk/src/transaction.rs:88` (changes a sensitive control or state-update path)

Before
```rust
}

impl Transaction {
    pub fn new_unsigned(message: Message) -> Self {
```
After
```rust
}

impl Sanitize for Transaction {
    fn sanitize(&self) -> std::result::Result<(), SanitizeError> {
        if self.message.header.num_required_signatures as usize > self.signatures.len() {
            return Err(SanitizeError::IndexOutOfBounds);
        }
        if self.signatures.len() > self.message.account_keys.len() {
```

# Fix Pattern

Add explicit sanitization implementations at deserialization-facing protocol types, enforce scalar bounds and cross-field consistency, and recursively validate nested protocol values.

## How It Was Fixed

The patch implements `Sanitize` for the affected types and returns `SanitizeError` when structural invariants fail. Validation now covers CRDS variant contents, vote indices, wallclock bounds, pubkey fields, slot vectors, and transaction signature/account-key relationships.

# Why It Matters

1. Deserialized peer or transaction data is untrusted until validated.

2. Malformed indices or inconsistent transaction structure can violate assumptions in later protocol code.

3. The patch affects gossip-, vote-, epoch-slot-, and transaction-bearing structures.

4. The exact financial-impact path is not proven by the provided evidence.

# Evidence Notes

Grounded evidence comes from added `Sanitize` implementations in `core/src/crds_value.rs`, `core/src/epoch_slots.rs`, and `sdk/src/transaction.rs`, plus the `Sanitize` trait definition in `sdk/src/sanitize.rs`. The security classification is supported by the commit subject and the nature of the added validation, but confidence is medium because the provided evidence does not show deserialization call sites, exploitability, signature-verification bypass, consensus divergence, denial of service, or the specific unauthorized SOL-earning path. Protocol security invariant: Deserialized protocol values that enter CRDS gossip, vote, epoch-slot, or transaction processing must be explicitly sanitized so out-of-range indices, wallclocks, malformed nested fields, and inconsistent transaction signature/account-key structure are rejected before downstream code relies on them. Verification notes: The patch does not prove the exact unauthorized SOL-earning path. The patch does not by itself prove signature verification bypass. The patch does not show a proof of remote exploitability. The patch does not establish whether malformed values caused consensus divergence, denial of service, or accounting error in practice. The provided evidence does not show all call sites where sanitize is invoked after deserialization. No call-site evidence was provided showing where sanitization is invoked after deserialization. No proof-of-concept or failing test was provided. The patch is more than cleanup or refactor because it adds runtime validation checks. Subsystem was downgraded from cryptography to protocol-input-sanitization because the shown changes are validation-focused, not cryptographic logic changes. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-input-validation`
Final tags: `protocol-input-validation, deserialization, sanitization, gossip, transaction-validation, state-integrity`

The supplied evidence supports keeping this as security hardening, not a fully proven security fix. The patch adds explicit sanitization for deserialized Solana protocol and transaction-bearing objects, enforcing bounds and cross-field consistency in CRDS, votes, epoch slots, and transactions. The commit subject claims a concrete financial impact, but the provided hunks do not show the deserialization call sites, exploit path, or mechanism by which malformed values allowed earning SOL.

## Security Evidence

1. Commit subject states deserialized input values were not sanitized and claims financial impact.
2. CRDS data now dispatches through Sanitize and rejects vote indices greater than or equal to MAX_VOTES.
3. Vote and EpochSlots now reject excessive wallclock values and recursively sanitize nested fields.
4. Transaction now rejects inconsistent signature counts relative to required signatures and account keys.
5. The changed types are serialized/deserialized protocol objects in core and sdk paths.

## Missing Evidence

1. No call site shows sanitize being invoked immediately after deserialization.
2. No exploit path demonstrates how malformed values led to earning SOL.
3. No proof shows signature verification bypass, accounting error, consensus divergence, or remote exploitability.
4. No tests or proof-of-concept are included in the supplied evidence.

## Claim Boundaries

1. This should not be labeled primarily as cryptography based on the supplied hunks.
2. The evidence supports protocol input sanitization and validation hardening.
3. The unauthorized SOL impact is supported only by the commit subject, not reconstructed from code evidence.
4. Do not claim a specific state-corruption mechanism beyond malformed deserialized values violating downstream assumptions.
