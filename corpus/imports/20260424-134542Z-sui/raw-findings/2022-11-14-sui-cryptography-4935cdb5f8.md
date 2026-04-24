---
case_id: case_20221114_4935cdb5f8
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2022-11-14
source_refs:
  - git:4935cdb5f81df649c70997f8d3f261f0db774708
  - "crates/sui-types/src/crypto.rs:1386"
  - "crates/sui-core/src/authority.rs:2315"
  - "crates/sui-types/src/crypto.rs:431"
  - "crates/sui-types/src/crypto.rs:465"
bug_class: missing-epoch-binding
impact_type:
  - cross-epoch-replay-risk
confidence: medium
tags:
  - cryptography
  - signature
  - epoch-binding
  - domain-separation
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Sui authority signatures from signing only the message value to signing the value plus EpochId, and updates checkpoint fragment verification to supply the current committee epoch. This supports a likely security fix for missing epoch binding in authority-signed checkpoint material, with no proof in the provided evidence of an actual deployed exploit or concrete impact.

## Observed Patch Facts

1. In `crates/sui-types/src/crypto.rs`, the patch replaces `impl<T> SignableBytes for T` with `impl<W> Signable<W> for EpochId`.

2. In `crates/sui-core/src/authority.rs`, the patch replaces `fragment.verify().map_err(|err| {` with `fragment`.

3. In `crates/sui-types/src/crypto.rs`, the patch replaces `fn new<T>(value: &T, secret: &dyn Signer<Self>) -> Self` with `fn new<T>(value: &T, epoch_id: EpochId, secret: &dyn Signer<Self>) -> Self`.

4. In `crates/sui-types/src/crypto.rs`, the patch replaces `fn verify<T>(&self, value: &T, author: AuthorityPublicKeyBytes) -> Result<(), SuiError>` with `epoch_id.write(&mut message);`.

## Project Context

The changed code sits primarily in `crates/sui-types/src`, `crates/sui-types`, `crates/sui-core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-types/src/messages_checkpoint.rs`, `crates/sui-types/src/messages.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/messages_checkpoint.rs`, `crates/sui-types/src/messages.rs`. The strongest project-level identifiers around this patch are `verify`, `value`, `fragment`, and `author`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/messages_tests.rs`, `crates/sui-core/src/unit_tests/authority_tests.rs`.

## Before/After Behavior

Before the patch, SuiAuthoritySignature::new and verify did not take an EpochId, and AuthoritySignature signing wrote only the value into the message buffer. Checkpoint fragment verification called fragment.verify() without an epoch. After the patch, signing and verification require EpochId, the AuthoritySignature implementation appends the serialized epoch to the signed message bytes, EpochId is made Signable via BCS serialization, and authority consensus checkpoint verification calls fragment.verify(self.committee.load().epoch).

# Root Cause

Authority signatures in the affected path did not include EpochId in the signed bytes, so the cryptographic signature material itself was not epoch-bound. The evidence does not establish whether another layer fully mitigated this before the patch.

## Walkthrough

1. crates/sui-types/src/crypto.rs changes the SuiAuthoritySignature API so new() and verify() require an EpochId.

2. The AuthoritySignature implementation writes the value and then writes epoch_id before signing the message buffer.

3. EpochId receives a Signable implementation using BCS serialization so it has a defined signed-byte representation.

4. crates/sui-core/src/authority.rs changes checkpoint fragment verification from fragment.verify() to fragment.verify(self.committee.load().epoch).

5. The provided context connects this path to checkpoint message handling, but does not prove exploitability or impact beyond the missing cryptographic binding.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/crypto.rs | 431 | Authority signature API changed so signing and verification require an epoch identifier. |
| crates/sui-types/src/crypto.rs | 461 | AuthoritySignature implementation appends EpochId to the signed message before signing and uses it during verification. |
| crates/sui-types/src/crypto.rs | 1386 | EpochId is made signable via BCS serialization so it can be included in authority signature material. |
| crates/sui-core/src/authority.rs | 2315 | Consensus checkpoint fragment verification now checks signatures against the current committee epoch. |
| crates/sui-types/src/messages_checkpoint.rs | 7 | Checkpoint message types are in the traced business-logic path using authority signature verification. |

## Code Snippets

## Snippet 1

Context: `crates/sui-types/src/crypto.rs:1386` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

impl<T> SignableBytes for T
where
```
After
```rust
}

impl<W> Signable<W> for EpochId
where
    W: std::io::Write,
{
    fn write(&self, writer: &mut W) {
        bcs::serialize_into(writer, &self).expect("Message serialization should not fail");
```

## Snippet 2

Context: `crates/sui-core/src/authority.rs:2315` (changes signature or replay validation logic)

Before
```rust
}
            ConsensusTransactionKind::Checkpoint(fragment) => {
                fragment.verify().map_err(|err| {
                    warn!(
                        "Ignoring malformed fragment (failed to verify) from {}: {:?}",
                        transaction.consensus_output.certificate.header.author, err
                    );
                })?;
```
After
```rust
}
            ConsensusTransactionKind::Checkpoint(fragment) => {
                fragment
                    .verify(self.committee.load().epoch)
                    .map_err(|err| {
                        warn!(
                            "Ignoring malformed fragment (failed to verify) from {}: {:?}",
                            transaction.consensus_output.certificate.header.author, err
```

## Snippet 3

Context: `crates/sui-types/src/crypto.rs:431` (changes signature or replay validation logic)

Before
```rust
pub trait SuiAuthoritySignature {
    fn new<T>(value: &T, secret: &dyn Signer<Self>) -> Self
    where
        T: Signable<Vec<u8>>;

    fn verify<T>(&self, value: &T, author: AuthorityPublicKeyBytes) -> Result<(), SuiError>
    where
```
After
```rust
pub trait SuiAuthoritySignature {
    fn new<T>(value: &T, epoch_id: EpochId, secret: &dyn Signer<Self>) -> Self
    where
        T: Signable<Vec<u8>>;

    fn verify<T>(
        &self,
```

## Snippet 4

Context: `crates/sui-types/src/crypto.rs:465` (changes signature or replay validation logic)

Before
```rust
let mut message = Vec::new();
        value.write(&mut message);
        secret.sign(&message)
    }

    fn verify<T>(&self, value: &T, author: AuthorityPublicKeyBytes) -> Result<(), SuiError>
    where
        T: Signable<Vec<u8>>,
```
After
```rust
let mut message = Vec::new();
        value.write(&mut message);
        epoch_id.write(&mut message);
        secret.sign(&message)
    }

    fn verify<T>(
        &self,
```

# Fix Pattern

Add protocol-domain binding to signed bytes by including the epoch in both signing and verification inputs.

## How It Was Fixed

The patch updated the authority signature trait and implementation to require EpochId, serialized that EpochId into the signed message, and passed the current committee epoch when verifying checkpoint fragments in the authority consensus path.

# Why It Matters

1. Pre-patch signatures in this path were not cryptographically bound to an epoch.

2. Epoch binding reduces the risk that an otherwise valid authority signature is accepted outside its intended epoch.

3. The evidence supports a replay/domain-separation issue shape, not signature forgery or proven financial impact.

# Evidence Notes

Grounded evidence is limited to the shown diffs and context: AuthoritySignature API changes, epoch serialization into signed bytes, and checkpoint fragment verification with the current epoch. Unsupported claims removed: no confirmed deployed exploit, no proven validator key reuse across epochs, no demonstrated consensus break, chain halt, or loss. Protocol security invariant: Authority signatures used for epoch-scoped checkpoint or consensus messages should cryptographically bind the signed bytes to the epoch in which the message is valid. Verification notes: The patch does not prove that cross-epoch replay was exploitable in a deployed configuration. The evidence does not show whether authority keys are reused across epochs or rotated in a way that affects practical impact. The patch does not establish forgery of signatures, only missing epoch binding in signed material. No financial loss, consensus safety break, or chain halt is proven by the provided diff alone. Security relevance is supported by direct cryptographic signing and verification changes. Bug class is narrowed to missing epoch binding rather than broad replay or signature validation failure. Confidence is medium because the missing binding is clear, but exploitability and impact are not established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-epoch-binding`
Final impact type: `cross-epoch-replay-risk`
Final confidence: `medium`
Final tags: `cryptography, signature, epoch-binding, domain-separation, consensus`

The supplied patch evidence clearly shows authority signatures being changed to include EpochId in both signing and verification, and checkpoint fragment verification now supplies the current committee epoch. That is a security-sensitive tightening of signature domain binding in consensus/checkpoint code. However, the evidence does not prove a concrete exploitable replay, deployed impact, or that prior layers failed to prevent misuse, so this is better retained as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. AuthoritySignature::new now requires EpochId and appends it to signed message bytes before signing.
2. AuthoritySignature::verify now requires EpochId, indicating verification is against epoch-bound bytes.
3. EpochId is made Signable via BCS serialization, giving it a defined signed representation.
4. Consensus checkpoint fragment verification now calls verify with self.committee.load().epoch.
5. The touched path is cryptographic authority signature handling in consensus/checkpoint processing.

## Missing Evidence

1. No advisory, CVE, exploit description, or explicit vulnerability statement is provided.
2. No proof that signatures could actually be replayed across epochs in deployed configurations.
3. No evidence about authority key reuse or committee/key rotation behavior across epochs.
4. No demonstrated consensus safety break, chain halt, financial loss, or unauthorized action.
5. No full regression test details proving rejection of a previously accepted malicious cross-epoch message.

## Claim Boundaries

1. Supports missing epoch/domain binding in authority signature material.
2. Supports security hardening against cross-epoch replay risk.
3. Does not support claims of signature forgery.
4. Does not prove a concrete exploit or production incident.
5. Impact should be framed as replay risk, not confirmed request forgery or consensus compromise.
