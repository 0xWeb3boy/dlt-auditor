---
case_id: case_20200427_8ef097bf6f
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2020-04-27
source_refs:
  - git:8ef097bf6f730fcb0bd8c63a2884df32375c8588
  - "core/src/crds_value.rs:78"
  - "core/src/crds_value.rs:173"
  - "core/src/epoch_slots.rs:219"
  - "sdk/src/transaction.rs:88"
bug_class: missing-input-validation
impact_type:
  - state-integrity
confidence: medium
tags:
  - input-validation
  - deserialization
  - transaction-validation
  - gossip-protocol
  - consensus-adjacent
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is best characterized as a likely security fix for missing structural validation after deserialization. The provided evidence shows new `Sanitize` implementations for CRDS payloads, gossip votes, epoch slots, and transactions, with bounds and consistency checks added before nested values are trusted. The exact exploit path or monetary impact is not established by the supplied snippets.

## Observed Patch Facts

1. In `core/src/crds_value.rs`, the patch replaces `#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]` with `impl Sanitize for CrdsData {`.

2. In `core/src/crds_value.rs`, the patch replaces `impl Vote {` with `impl Sanitize for Vote {`.

3. In `core/src/epoch_slots.rs`, the patch replaces `impl fmt::Debug for EpochSlots {` with `impl Sanitize for EpochSlots {`.

4. In `sdk/src/transaction.rs`, the patch replaces `impl Transaction {` with `impl Sanitize for Transaction {`.

## Project Context

The changed code sits primarily in `core/src`, `sdk/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `sdk/src/sanitize.rs`, `core/src/contact_info.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/contact_info.rs`, `sdk/src/message.rs`. The strongest project-level identifiers around this patch are `sanitize`, `SanitizeError`, `std::result::Result`, and `impl`.

## Before/After Behavior

Before the patch, the shown CRDS, vote, epoch-slot, and transaction structures were serializable/deserializable without the displayed post-deserialization `Sanitize` implementations. After the patch, CRDS variants dispatch to nested sanitizers, vote indexes are bounded, wallclocks are range-checked, public keys and slot vectors are sanitized, and transactions reject inconsistent signature/account-key/message cardinalities before message sanitization.

# Root Cause

Deserialized protocol and transaction objects lacked the structural validation now required by the patch. The grounded issue is missing post-deserialization sanitization, not a proven cryptographic bypass, memory corruption issue, or fully demonstrated SOL-earning exploit path.

## Walkthrough

1. A CRDS gossip payload can be deserialized into `CrdsData` variants such as contact info, votes, hashes, or epoch slots.

2. The patch adds `CrdsData::sanitize`, which routes each variant to the appropriate nested sanitizer and checks vote indexes against `MAX_VOTES`.

3. The patch adds `Vote::sanitize`, rejecting wallclocks at or above `MAX_WALLCLOCK`, sanitizing the sender pubkey, and sanitizing the embedded transaction.

4. The patch adds `EpochSlots::sanitize`, rejecting wallclocks at or above `MAX_WALLCLOCK`, sanitizing the sender pubkey, and sanitizing the slot vector.

5. The patch adds `Transaction::sanitize`, rejecting required-signature counts greater than available signatures and signature counts greater than account keys before sanitizing the message.

6. The provided evidence supports a validation-boundary fix but does not show all deserialization call sites or the complete exploit mechanics.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/crds_value.rs | 78 | Dispatches sanitization for each CRDS gossip payload variant and bounds-checks vote indexes before accepting nested values. |
| core/src/crds_value.rs | 173 | Sanitizes gossip vote records by bounding wallclock, validating the sender pubkey, and sanitizing the embedded transaction. |
| core/src/epoch_slots.rs | 219 | Sanitizes epoch slot gossip records by bounding wallclock, validating the sender pubkey, and sanitizing compressed slot vectors. |
| sdk/src/transaction.rs | 88 | Sanitizes deserialized transactions by enforcing signature count versus required signatures and account keys before message validation. |

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

## Snippet 3

Context: `core/src/epoch_slots.rs:219` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

use std::fmt;
impl fmt::Debug for EpochSlots {
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

Add explicit post-deserialization sanitization on protocol data types, reject out-of-range or structurally inconsistent fields, and recursively sanitize nested values before downstream processing.

## How It Was Fixed

The patch introduced `Sanitize` implementations for CRDS data, vote records, epoch-slot records, and transactions. These implementations enforce bounds on indexes and wallclocks, validate nested public keys and vectors, and check transaction signature/account-key consistency before delegating to message sanitization.

# Why It Matters

1. CRDS gossip carries network-supplied structured data.

2. Votes and epoch slots are consensus-adjacent data and need structural bounds before use.

3. Transactions require signature and account-key cardinality invariants before later validation.

4. The supplied evidence does not prove the specific monetary exploit path.

# Evidence Notes

The strongest evidence is the commit subject and body: `Input values are not sanitized after they are deserialized` plus `sanitize gossip protocol messages`, `sanitize transactions`, and `crds protocol sanitize`. Code evidence shows new sanitizers in `core/src/crds_value.rs`, `core/src/epoch_slots.rs`, and `sdk/src/transaction.rs`. Claims about cryptographic signature bypass, validator takeover, memory corruption, denial of service, consensus failure, or the exact way SOL could be earned are not established by the provided snippets. Protocol security invariant: Deserialized CRDS gossip values and transactions must be structurally validated before later gossip, consensus-adjacent, or runtime logic relies on their indexes, wallclocks, public keys, slot vectors, signatures, account keys, or messages. Verification notes: The patch does not by itself prove the full path by which SOL could be earned. The patch does not show a cryptographic signature verification bypass; it enforces structural transaction validity before later processing. The patch does not prove remote code execution, memory corruption, or validator takeover. The patch does not show every deserialization call site or prove all callers invoke `sanitize`. The patch does not establish whether malformed inputs caused consensus failure, denial of service, or incorrect accounting in a specific scenario. Validated as security-relevant input validation based on commit metadata and changed sanitization logic. Downgraded from confirmed/high to likely/medium because call sites and exploit mechanics are not shown. Kept in security corpus because the patch directly addresses missing validation after deserialization rather than cleanup or refactor work. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `missing-input-validation`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `input-validation, deserialization, transaction-validation, gossip-protocol, consensus-adjacent`

The supplied evidence supports keeping this as a security-relevant fix, but with narrower framing than the generated finding. The commit metadata explicitly describes unsanitized deserialized inputs and a SOL-earning consequence, and the patch adds structural validation for deserialized CRDS gossip values, votes, epoch slots, and transactions. The snippets do not prove the full exploit path, cryptographic bypass, or precise monetary mechanics, so the finding should be retained as a likely security fix for missing input validation after deserialization rather than as a broad cryptography or state-corruption case.

## Security Evidence

1. Commit subject states deserialized input values were not sanitized and links the issue to earning SOL.
2. Patch adds Sanitize implementations for CRDS protocol data, gossip votes, epoch slots, and transactions.
3. Transaction sanitizer rejects inconsistent required-signature, signature, and account-key counts before message sanitization.
4. Gossip-related sanitizers reject out-of-range vote indexes and wallclock values and recursively sanitize nested values.
5. Changed files are in transaction, gossip, and validator-adjacent code paths rather than maintenance-only areas.

## Missing Evidence

1. No call site evidence shows exactly where sanitize is invoked after deserialization.
2. No proof-of-concept or execution trace demonstrates how malformed input earns SOL.
3. No evidence proves a cryptographic signature verification bypass.
4. No evidence establishes denial of service, validator compromise, or memory corruption.
5. No tests are shown demonstrating the vulnerable pre-patch behavior.

## Claim Boundaries

1. Validate as missing post-deserialization input validation in security-sensitive Solana protocol and transaction data.
2. Do not claim confirmed exploitability from the snippets alone.
3. Do not classify primarily as cryptography; the shown fix is structural validation.
4. Do not claim snapshot, RPC, memory safety, or validator takeover impact from the provided evidence.
5. Economic impact is suggested by commit metadata but not mechanically demonstrated by the patch evidence.
