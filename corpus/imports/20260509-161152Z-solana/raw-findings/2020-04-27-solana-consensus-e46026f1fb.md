---
case_id: case_20200427_e46026f1fb
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2020-04-27
source_refs:
  - git:e46026f1fb6613c3400aef7b695a155eacae281a
  - "core/src/crds_value.rs:94"
  - "core/src/crds_value.rs:209"
  - "core/src/crds_value.rs:181"
  - "sdk/src/transaction.rs:85"
bug_class: missing-deserialization-validation
impact_type:
  - protocol-integrity
  - input-validation
confidence: medium
tags:
  - input-validation
  - deserialization
  - sanitize
  - consensus
  - transaction
  - gossip
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best classified as a likely security fix for missing post-deserialization validation. The provided hunks show new `Sanitize` implementations for CRDS slot-related values, votes, and transactions, adding bounds checks and structural consistency checks that were not shown before. The commit subject directly frames the issue as unsanitized deserialized input with SOL-impacting consequences, but the supplied evidence does not establish the full exploit path or prove remote exploitability.

## Observed Patch Facts

1. In `core/src/crds_value.rs`, the patch replaces `#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]` with `impl Sanitize for EpochIncompleteSlots {`.

2. In `core/src/crds_value.rs`, the patch replaces `impl Vote {` with `impl Sanitize for Vote {`.

3. In `core/src/crds_value.rs`, the patch replaces `#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]` with `impl Sanitize for EpochSlots {`.

4. In `sdk/src/transaction.rs`, the patch replaces `impl Transaction {` with `impl Sanitize for Transaction {`.

## Project Context

The changed code sits primarily in `core/src`, `sdk/src`, which anchors the finding in the `consensus` area of the project. Historical context from `sdk/src/sanitize.rs`, `core/src/contact_info.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/contact_info.rs`, `sdk/src/sanitize.rs`. The strongest project-level identifiers around this patch are `SanitizeError::Failed`, `SanitizeError`, `sanitize`, and `impl`.

## Before/After Behavior

Before the patch, the supplied snippets show `EpochIncompleteSlots`, `EpochSlots`, `Vote`, and `Transaction` as serializable/deserializable data structures without the shown `sanitize()` implementations enforcing these invariants. After the patch, these types reject out-of-range slots and wallclocks, validate nested public keys/stashes/transactions/messages, and reject inconsistent transaction signature/account-key lengths.

# Root Cause

Protocol objects could be deserialized without the specific local invariant checks shown in the patch. The supported root cause is missing or incomplete sanitization after deserialization, not a proven cryptographic bypass or a fully demonstrated balance-manipulation exploit.

## Walkthrough

1. `sdk/src/sanitize.rs` defines the shared `Sanitize` trait and `SanitizeError` types used by the patch.

2. `core/src/crds_value.rs` adds sanitization for `EpochIncompleteSlots`, rejecting `first >= MAX_SLOT`.

3. `core/src/crds_value.rs` adds sanitization for `EpochSlots`, rejecting invalid wallclock, lowest slot, root slot, and contained slot values, then validating nested state.

4. `core/src/crds_value.rs` adds sanitization for `Vote`, checking wallclock and validating the origin public key plus embedded transaction.

5. `sdk/src/transaction.rs` adds sanitization for `Transaction`, rejecting mismatches between required signatures, signature vector length, and account keys, then delegating to message sanitization.

6. The supplied evidence supports missing validation on deserialized protocol data, but not the exact path by which SOL could be earned.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/crds_value.rs | 94 | Adds sanitization for EpochIncompleteSlots, rejecting first slots outside MAX_SLOT before accepting deserialized CRDS data. |
| core/src/crds_value.rs | 181 | Adds sanitization for EpochSlots, bounding wallclock, lowest, root, and contained slots, then validating nested stash and origin pubkey. |
| core/src/crds_value.rs | 209 | Adds sanitization for Vote, bounding wallclock and validating the origin pubkey and embedded transaction. |
| sdk/src/transaction.rs | 85 | Adds transaction structural checks tying required signatures, signature vector length, account keys, and nested message sanitization. |
| sdk/src/sanitize.rs | 1 | Defines the Sanitize trait and error types used as the validation mechanism for deserialized inputs. |

## Code Snippets

## Snippet 1

Context: `core/src/crds_value.rs:94` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct SnapshotHash {
```
After
```rust
}

impl Sanitize for EpochIncompleteSlots {
    fn sanitize(&self) -> Result<(), SanitizeError> {
        if self.first >= MAX_SLOT {
            return Err(SanitizeError::Failed);
        }
        //rest of the data doesn't matter since we no longer decompress
```

## Snippet 2

Context: `core/src/crds_value.rs:209` (changes a consensus- or validator-sensitive branch)

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

Context: `core/src/crds_value.rs:181` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct Vote {
```
After
```rust
}

impl Sanitize for EpochSlots {
    fn sanitize(&self) -> Result<(), SanitizeError> {
        if self.wallclock >= MAX_WALLCLOCK {
            return Err(SanitizeError::Failed);
        }
        if self.lowest >= MAX_SLOT {
```

## Snippet 4

Context: `sdk/src/transaction.rs:85` (changes a sensitive control or state-update path)

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

Add explicit `Sanitize` implementations at deserialization-facing protocol data boundaries, reject invalid values with `SanitizeError`, and recursively validate nested protocol objects before downstream use.

## How It Was Fixed

The patch implements validation methods for affected CRDS, vote, and transaction structures. It bounds slot and wallclock values, validates nested public keys/stashes/transactions/messages, and enforces transaction signature/account-key consistency.

# Why It Matters

1. Rejects malformed CRDS slot data before later processing.

2. Ensures vote objects validate their timestamp, origin, and embedded transaction.

3. Prevents structurally inconsistent transactions from passing the new sanitization hook.

4. Security impact is plausible from the commit subject and critical data paths, but exploitability is not fully proven by the hunks.

# Evidence Notes

Grounded evidence comes from `core/src/crds_value.rs` additions for `EpochIncompleteSlots`, `EpochSlots`, and `Vote`; `sdk/src/transaction.rs` additions for `Transaction`; and `sdk/src/sanitize.rs` defining the validation trait. Claims about exact SOL theft mechanics, remote exploitability, cryptographic signature bypass, or bank/runtime effects are not established by the provided snippets. Protocol security invariant: Deserialized protocol objects consumed by gossip/CRDS, vote handling, and transaction handling must be explicitly sanitized before later processing: slot and wallclock fields must remain within protocol bounds, nested public keys/messages/transactions must validate, and transaction signature counts must be consistent with required signatures and account keys. Verification notes: The patch evidence does not show the full exploit path for earning SOL. The patch evidence does not prove remote exploitability by itself. The patch evidence does not show whether every deserialization call site invokes sanitize after this change. The change is broader input validation, not proof of a cryptographic signature bypass. Runtime bank effects are listed in the commit files but not substantiated by the provided hunks. No full exploit path is shown in the provided evidence. No call-site proof shows every deserialization path invokes `sanitize()`. Runtime bank effects are listed only by changed-file name, not substantiated by supplied hunks. Classification is therefore likely security fix with medium confidence, not confirmed. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-deserialization-validation`
Final impact type: `protocol-integrity, input-validation`
Final confidence: `medium`
Final tags: `input-validation, deserialization, sanitize, consensus, transaction, gossip`

The supplied evidence supports retaining this as security hardening rather than a fully proven security fix. The patch adds explicit Sanitize implementations for deserialized CRDS, vote, epoch slot, and transaction objects, enforcing bounds and structural invariants in consensus- and transaction-sensitive data. The commit subject claims an economic consequence, but the provided hunks do not prove the exploit path or show that malformed inputs could actually be used to earn SOL.

## Security Evidence

1. Adds validation for deserialized protocol objects via Sanitize implementations.
2. Rejects out-of-range slot and wallclock values in CRDS-related structures.
3. Validates nested public keys, stash data, transactions, and messages.
4. Rejects transactions where required signatures exceed provided signatures or signatures exceed account keys.
5. Touched files are in consensus, gossip, SDK transaction, and runtime-adjacent paths.

## Missing Evidence

1. No demonstrated exploit path showing how malformed deserialized input leads to SOL theft.
2. No call-site evidence proving all relevant deserialization paths invoke sanitize after this patch.
3. No runtime or bank hunk showing direct prevention of unauthorized balance changes.
4. No proof of cryptographic signature bypass or consensus state corruption from the supplied snippets.

## Claim Boundaries

1. Classify as security-hardening, not confirmed security-fix, from the supplied patch evidence alone.
2. Supported root cause is missing post-deserialization validation of protocol data.
3. Do not claim proven remote exploitability or proven SOL theft mechanics.
4. Do not retain the more specific state-corruption classification without additional evidence.
