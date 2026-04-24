---
case_id: case_20230227_d009e82fa3
project: sui
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: high
source_quality: high
date: 2023-02-27
source_refs:
  - git:d009e82fa35bda4f2b3e7a86a9529d36c32a8159
  - "crates/sui-types/src/crypto.rs:1539"
  - "crates/sui-types/src/crypto.rs:435"
  - "crates/sui-types/src/crypto.rs:475"
  - "crates/sui-types/src/crypto.rs:454"
bug_class: missing-signature-domain-separation
impact_type:
  - signature-domain-confusion
tags:
  - cryptography
  - authority-signature
  - intent-scope
  - domain-separation
  - validator
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes authority signature construction, verification, and batch verification to include an explicit intent scope by signing/verifying serialized `IntentMessage<T>` values. The evidence supports a security-hardening classification for missing signature domain separation, but it does not prove a concrete exploit, cross-scope byte collision, or consensus failure.

## Observed Patch Facts

1. In `crates/sui-types/src/crypto.rs`, the patch replaces `pub fn add_message<T>(&mut self, message_value: &T, epoch: EpochId) -> usize` with `pub fn add_message<T>(&mut self, message_value: &T, epoch: EpochId, intent: Intent) -...`.

2. In `crates/sui-types/src/crypto.rs`, the patch replaces `fn new<T>(value: &T, epoch_id: EpochId, secret: &dyn Signer<Self>) -> Self` with `fn verify_secure<T>(`.

3. In `crates/sui-types/src/crypto.rs`, the patch replaces `let message = bcs::to_bytes(&value).expect("Message serialization should not fail");` with `let mut message = Vec::new();`.

4. In `crates/sui-types/src/crypto.rs`, the patch replaces `fn new<T>(value: &T, epoch_id: EpochId, secret: &dyn Signer<Self>) -> Self` with `fn new_secure<T>(value: &IntentMessage<T>, epoch: &EpochId, secret: &dyn Signer<Self>...`.

## Project Context

The changed code sits primarily in `crates/sui-types/src`, `crates/sui-types`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-types/src/messages.rs`, `crates/sui-types/src/messages_checkpoint.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/messages.rs`, `crates/sui-types/src/base_types.rs`. The strongest project-level identifiers around this patch are `message`, `Vec::new`, `bcs::to_bytes`, and `value`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/messages_tests.rs`, `crates/sui-types/src/unit_tests/multisig_tests.rs`.

## Before/After Behavior

Before the change, authority signatures and verification operated on raw signable or serialized message payload bytes plus epoch. `VerificationObligation::add_message` queued raw message bytes with an epoch. After the change, signing and verification operate on BCS-serialized `IntentMessage<T>` plus epoch, and batch verification requires an explicit `Intent` before serializing the message for verification.

# Root Cause

Authority signature bytes did not include an explicit signed intent/domain component. The signed material was bound to the payload and epoch, but the provided evidence indicates it was not explicitly bound to the intended message scope.

## Walkthrough

1. `SuiAuthoritySignature` changed from raw `new`/`verify` methods over `Signable<Vec<u8>>` payloads to `new_secure`/`verify_secure` methods over `IntentMessage<T>`.

2. The implementation serializes `IntentMessage<T>` with BCS, appends the epoch, and uses that buffer for signing or verification.

3. `VerificationObligation::add_message` now accepts an `Intent`, wraps the message using `IntentMessage::new(intent, message_value)`, and queues the serialized wrapper.

4. The commit message states that authority signatures now commit to intent scope for sender signed transactions, transaction effects, and checkpoint summaries.

5. The evidence does not establish that an attacker could exploit the old behavior in practice.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/crypto.rs | 446 | authority signature API now signs IntentMessage<T> through new_secure instead of raw Signable payloads |
| crates/sui-types/src/crypto.rs | 468 | authority signature verification serializes IntentMessage<T> plus epoch before public-key verification |
| crates/sui-types/src/crypto.rs | 1535 | batch verification obligation records messages with explicit Intent scope before verifying signatures |
| crates/sui-types/src/messages.rs | 1 | authority message types import Intent, IntentMessage, and IntentScope for transaction and effects message paths |
| crates/sui-types/src/messages_checkpoint.rs | 1 | checkpoint summary message path participates in intent-scoped authority signing |

## Code Snippets

## Snippet 1

Context: `crates/sui-types/src/crypto.rs:1539` (changes a consensus- or validator-sensitive branch)

Before
```rust
/// Add a new message to the list of messages to be verified.
    /// Returns the index of the message.
    pub fn add_message<T>(&mut self, message_value: &T, epoch: EpochId) -> usize
    where
        T: Signable<Vec<u8>>,
    {
        let mut message = Vec::new();
        message_value.write(&mut message);
```
After
```rust
/// Add a new message to the list of messages to be verified.
    /// Returns the index of the message.
    pub fn add_message<T>(&mut self, message_value: &T, epoch: EpochId, intent: Intent) -> usize
    where
        T: Serialize,
    {
        let mut message = Vec::new();
        let intent_msg = IntentMessage::new(intent, message_value);
```

## Snippet 2

Context: `crates/sui-types/src/crypto.rs:435` (changes signature or replay validation logic)

Before
```rust
pub trait SuiAuthoritySignature {
    fn new<T>(value: &T, epoch_id: EpochId, secret: &dyn Signer<Self>) -> Self
    where
        T: Signable<Vec<u8>>;

    fn verify<T>(
        &self,
```
After
```rust
pub trait SuiAuthoritySignature {
    fn verify_secure<T>(
        &self,
        value: &IntentMessage<T>,
        epoch_id: EpochId,
        author: AuthorityPublicKeyBytes,
    ) -> Result<(), SuiError>
```

## Snippet 3

Context: `crates/sui-types/src/crypto.rs:475` (changes a consensus- or validator-sensitive branch)

Before
```rust
T: Serialize,
    {
        let message = bcs::to_bytes(&value).expect("Message serialization should not fail");
        let public_key = AuthorityPublicKey::try_from(author).map_err(|_| {
            SuiError::KeyConversionError(
```
After
```rust
T: Serialize,
    {
        let mut message = Vec::new();
        let intent_msg_bytes =
            bcs::to_bytes(&value).expect("Message serialization should not fail");
        message.extend(intent_msg_bytes);
        epoch.write(&mut message);
```

## Snippet 4

Context: `crates/sui-types/src/crypto.rs:454` (changes signature or replay validation logic)

Before
```rust
impl SuiAuthoritySignature for AuthoritySignature {
    fn new<T>(value: &T, epoch_id: EpochId, secret: &dyn Signer<Self>) -> Self
    where
        T: Signable<Vec<u8>>,
    {
        let mut message = Vec::new();
        value.write(&mut message);
```
After
```rust
impl SuiAuthoritySignature for AuthoritySignature {
    fn new_secure<T>(value: &IntentMessage<T>, epoch: &EpochId, secret: &dyn Signer<Self>) -> Self
    where
        T: Serialize,
    {
        let mut message = Vec::new();
        let intent_msg_bytes =
```

# Fix Pattern

Add cryptographic domain separation by signing a structured intent-scoped envelope instead of only the raw protocol payload bytes.

## How It Was Fixed

The patch introduced intent-scoped authority signature APIs, replaced raw `Signable<Vec<u8>>` message writing with BCS serialization of `IntentMessage<T>`, preserved epoch binding by appending the epoch, and updated batch verification to require an explicit `Intent`.

# Why It Matters

1. Prevents authority signatures from omitting the intended protocol scope.

2. Reduces ambiguity between signatures over different authority message domains.

3. Hardens sender transaction, transaction effect, and checkpoint summary signing paths named by the commit.

4. Does not by itself prove a prior exploitable replay or forgery.

# Evidence Notes

Strong evidence comes from `crates/sui-types/src/crypto.rs`, where signing, verification, and `VerificationObligation::add_message` now use `IntentMessage<T>` and explicit `Intent` values. The commit body directly says authority signatures now commit to intent scope. Unsupported stronger claims removed: no proven exploit path, no demonstrated identical serialization across scopes, no proven consensus safety violation, and no claim about proof-of-possession or Narwhal headers because the commit excludes them. Protocol security invariant: Authority signatures for protocol messages should bind the signed payload to its intended message scope/domain, in addition to the serialized message bytes and epoch. Verification notes: No concrete exploit path is proven by the provided patch evidence. No evidence shows that differently scoped messages had identical serialized bytes in practice. No evidence proves a consensus safety violation or state mutation from an invalid signature. Proof-of-possession and Narwhal header signing are explicitly outside this commit. This does not establish that all remaining signature schemes in the project are intent-bound. Classified as security hardening, not a confirmed exploited vulnerability fix. Kept in the security corpus because the patch changes cryptographic signature domain binding. Confidence is high for the hardening behavior, lower for any specific exploit thesis. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-signature-domain-separation`
Final impact type: `signature-domain-confusion`
Final tags: `cryptography, authority-signature, intent-scope, domain-separation, validator, consensus`

The supplied evidence supports retaining this as security hardening: authority signatures and batch verification were changed to sign and verify an IntentMessage that includes explicit intent scope, and the commit message directly states that authority signatures now commit to intent scope. The patch does not prove a concrete exploitable replay, forgery, serialization collision, or consensus failure, so it should not be elevated to a security-fix case or retain a specific request-forgery/replay impact claim.

## Security Evidence

1. Authority signature APIs changed from raw Signable payloads to IntentMessage<T>-based secure signing and verification.
2. VerificationObligation::add_message now requires an explicit Intent and serializes IntentMessage before verification.
3. The commit body states authority signatures now commit to intent scope for sender transactions, transaction effects, and checkpoint summaries.
4. The affected code is cryptographic authority signature construction and verification in validator/consensus-related paths.

## Missing Evidence

1. No demonstrated exploit path against the previous signature format.
2. No proof that two distinct message scopes could share valid signed bytes in practice.
3. No evidence of an observed replay, forgery, or consensus safety violation.
4. No evidence that excluded proof-of-possession or Narwhal signing headers were fixed here.

## Claim Boundaries

1. Classify as domain-separation hardening, not a confirmed vulnerability fix.
2. Do not claim a concrete request forgery or replay impact from the patch alone.
3. Do not claim this fixed all signature domain-separation issues in the project.
4. Do not include proof-of-possession or Narwhal header signing in the validated finding.
