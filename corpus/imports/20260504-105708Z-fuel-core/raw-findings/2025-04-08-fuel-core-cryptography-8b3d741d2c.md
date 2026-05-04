---
case_id: case_20250408_8b3d741d2c
project: fuel-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2025-04-08
source_refs:
  - git:8b3d741d2cdc310d2c15af612adc6caf86cf048e
  - "crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/broadcast.rs:204"
  - "crates/services/consensus_module/poa/src/pre_confirmation_signature_service.rs:129"
  - "crates/services/consensus_module/poa/src/pre_confirmation_signature_service.rs:254"
  - "crates/types/src/services/p2p.rs:119"
bug_class: signature-binding-hardening
impact_type:
  - replay-risk-reduction
confidence: medium
tags:
  - cryptography
  - p2p
  - consensus
  - signature-binding
  - nonce
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes PoA pre-confirmation delegation so nonce is included in the sealed delegate-key entity instead of being carried separately on the p2p Delegate message. This is plausibly security-relevant signature-binding or replay-hardening work, but the provided evidence does not prove a concrete vulnerability, exploit path, or security impact.

## Observed Patch Facts

1. In `crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/broadcast.rs`, the patch replaces `};` with `nonce: u64,`.

2. In `crates/services/consensus_module/poa/src/pre_confirmation_signature_service.rs`, the patch replaces `create_delegate_key(&mut key_generator, &parent_signature, expiration)` with `let mut nonce = 0;`.

3. In `crates/services/consensus_module/poa/src/pre_confirmation_signature_service.rs`, the patch replaces `).await);` with `let nonce = 0;`.

4. In `crates/types/src/services/p2p.rs`, the patch replaces `Delegate {` with `Delegate(SignedByBlockProducerDelegation<DP, S>),`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature`, `crates/fuel-core/src/service/adapters/consensus_module/poa`, `crates/services/consensus_module/poa/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/parent_signature.rs`, `crates/types/src/services/executor.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/services/consensus_module/poa/src/pre_confirmation_signature_service/tests.rs`, `crates/types/src/blockchain/consensus.rs`. The strongest project-level identifiers around this patch are `nonce`, `expiration`, `sealed`, and `signature`. Nearby tests or test-like files include `crates/services/consensus_module/poa/src/service_test/trigger_tests.rs`, `crates/services/consensus_module/poa/src/service_test/manually_produce_tests.rs`.

## Before/After Behavior

Before the patch, delegate-key creation used public key and expiration, while the p2p Delegate message carried a sealed delegation plus a separate nonce field. Verification reconstructed DelegatePreConfirmationKey from public key and expiration only. After the patch, delegate-key creation receives nonce, DelegatePreConfirmationKey includes public key, expiration, and nonce, and the p2p Delegate message carries only the sealed delegation.

# Root Cause

The nonce was represented outside the sealed delegation entity. The evidence supports that this left nonce outside the signed delegate-key data, but does not prove that this caused an exploitable replay, forgery, or consensus issue.

## Walkthrough

1. The pre-confirmation signature service creates delegate keys during startup and key rotation.

2. Before the patch, create_delegate_key was called without nonce.

3. The p2p Delegate variant carried a signed delegation seal and a separate nonce field.

4. The matching helper reconstructed the expected signed entity from public key and expiration only.

5. The patch passes nonce into create_delegate_key and includes it in DelegatePreConfirmationKey.

6. The p2p Delegate variant is changed to carry only the sealed delegation.

7. The evidence shows signature-binding hardening, not a demonstrated vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/services/consensus_module/poa/src/pre_confirmation_signature_service.rs | 129 | initial delegate key creation now includes nonce in the sealed delegation entity |
| crates/services/consensus_module/poa/src/pre_confirmation_signature_service.rs | 254 | key rotation path now creates and broadcasts delegate keys with nonce bound into the signature |
| crates/types/src/services/p2p.rs | 119 | p2p Delegate message no longer carries nonce outside the sealed delegation |
| crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/broadcast.rs | 204 | delegate-key verification/test helper now expects nonce inside the signed DelegatePreConfirmationKey |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa/pre_confirmation_signature/broadcast.rs:204` (changes signature or replay validation logic)

Before
```rust
expiration: Tai64,
        signature: &ProtocolSignature,
    ) -> bool {
        let entity = DelegatePreConfirmationKey {
            public_key: delegate_key,
            expiration,
        };
        match &**inner {
```
After
```rust
expiration: Tai64,
        signature: &ProtocolSignature,
        nonce: u64,
    ) -> bool {
        let entity = DelegatePreConfirmationKey {
            public_key: delegate_key,
            expiration,
            nonce,
```

## Snippet 2

Context: `crates/services/consensus_module/poa/src/pre_confirmation_signature_service.rs:129` (changes signature or replay validation logic)

Before
```rust
} = self;

        // The first key rotation is triggered immediately
        let expiration = key_rotation_trigger.next_rotation().await?;
        let (new_delegate_key, sealed) =
            create_delegate_key(&mut key_generator, &parent_signature, expiration)
                .await
                .map_err(|e| anyhow::anyhow!(e))?;
```
After
```rust
} = self;

        let mut nonce = 0;
        // The first key rotation is triggered immediately
        let expiration = key_rotation_trigger.next_rotation().await?;
        let (new_delegate_key, sealed) =
            create_delegate_key(&mut key_generator, &parent_signature, expiration, nonce)
                .await
```

## Snippet 3

Context: `crates/services/consensus_module/poa/src/pre_confirmation_signature_service.rs:254` (changes signature or replay validation logic)

Before
```rust
let expiration = try_or_stop!(res);

                let (new_delegate_key, sealed) = try_or_stop!(create_delegate_key(
                    &mut self.key_generator,
                    &self.parent_signature,
                    expiration,
                ).await);
```
After
```rust
let expiration = try_or_stop!(res);

                let nonce = 0;
                let (new_delegate_key, sealed) = try_or_stop!(create_delegate_key(
                    &mut self.key_generator,
                    &self.parent_signature,
                    expiration,
                    nonce,
```

## Snippet 4

Context: `crates/types/src/services/p2p.rs:119` (changes signature or replay validation logic)

Before
```rust
pub enum PreConfirmationMessage<DP, DS, S> {
    /// Notification of key delegation
    Delegate {
        /// The sealed key delegation.
        seal: SignedByBlockProducerDelegation<DP, S>,
        /// The nonce of the p2p message to make it unique.
        nonce: u64,
    },
```
After
```rust
pub enum PreConfirmationMessage<DP, DS, S> {
    /// Notification of key delegation
    Delegate(SignedByBlockProducerDelegation<DP, S>),
    /// Notification of pre-confirmations
    Preconfirmations(SignedPreconfirmationByDelegate<DS>),
```

# Fix Pattern

Move uniqueness-related metadata into the signed entity and update creation, transport, and verification code to use that representation consistently.

## How It Was Fixed

The patch adds nonce to DelegatePreConfirmationKey construction, passes nonce through delegate-key creation paths, removes the separate nonce field from PreConfirmationMessage::Delegate, and updates the delegate-key matching helper to compare a sealed entity that includes nonce.

# Why It Matters

1. Nonce is now bound to the sealed delegate-key data.

2. The previous unsigned nonce representation could differ from the signed entity.

3. No provided evidence proves block forgery, consensus compromise, or persistent-state misuse.

# Evidence Notes

Grounded evidence is limited to changed code excerpts in pre_confirmation_signature_service.rs, p2p.rs, and broadcast.rs. The commit subject and diff support a nonce/signature-binding hardening interpretation. Claims of an actual replay vulnerability, attacker exploitability, block-producer signature forgery, transaction execution impact, or consensus safety compromise are unsupported by the provided evidence. Protocol security invariant: If a nonce is intended to affect delegate-key uniqueness or replay handling, it should be part of the signed delegate-key entity rather than unsigned p2p message metadata. The evidence shows the patch moves nonce into DelegatePreConfirmationKey, but does not establish an exploitable violation of this invariant. Verification notes: No evidence proves block production, transaction execution, or consensus safety could be directly compromised. No evidence proves an attacker could forge a block producer signature. No evidence shows the old unsigned nonce was accepted into persistent state by itself. No exploitability beyond replay or message-uniqueness binding risk is established by the patch. No tests or execution results were provided. No exploit scenario was demonstrated. No evidence shows how old unsigned nonce values were consumed beyond p2p message structure and helper validation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-binding-hardening`
Final impact type: `replay-risk-reduction`
Final confidence: `medium`
Final tags: `cryptography, p2p, consensus, signature-binding, nonce, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a proven security fix. The change moves the nonce from unsigned p2p Delegate message metadata into the sealed delegate-key entity and updates creation and validation paths accordingly. That clearly tightens signature binding in a consensus-adjacent pre-confirmation path, but the evidence does not prove an exploitable replay, forgery, or consensus compromise.

## Security Evidence

1. Nonce is added to DelegatePreConfirmationKey, making it part of the sealed entity.
2. PreConfirmationMessage::Delegate no longer carries nonce separately outside the signed delegation.
3. Delegate-key creation paths now pass nonce into create_delegate_key.
4. Validation/test helper now reconstructs expected signed entity with nonce included.
5. The changed code is in PoA pre-confirmation delegation and p2p consensus messaging paths.

## Missing Evidence

1. No exploit path shows that an attacker could abuse the old unsigned nonce field.
2. No evidence shows the old nonce was used for replay protection or state acceptance in a vulnerable way.
3. No tests or commit body demonstrate a concrete security regression or attack.
4. No evidence proves block forgery, transaction impact, or consensus safety compromise.

## Claim Boundaries

1. Classify as hardening of signature-bound delegation metadata, not a confirmed vulnerability fix.
2. Do not claim arbitrary replay or request forgery was exploitable from this evidence alone.
3. Do not claim block producer signature forgery or consensus compromise.
4. Keep impact limited to replay-risk reduction and signature-binding hardening.
