---
case_id: case_20250311_8b3eb35018
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2025-03-11
source_refs:
  - git:8b3eb35018f747ae5231c54a0509c1ff54208598
  - "crates/services/tx_status_manager/src/service.rs:150"
  - "crates/services/tx_status_manager/src/service.rs:434"
  - "crates/services/tx_status_manager/src/service.rs:366"
  - "crates/services/tx_status_manager/src/service.rs:404"
bug_class: missing-signature-verification
impact_type:
  - integrity
tags:
  - blockchain-core
  - transaction-processing
  - p2p
  - signature-verification
  - authentication
  - integrity
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a missing authentication gate in the transaction status preconfirmation path. Before the change, `PreConfirmationMessage::Preconfirmations(sealed)` discarded the sealed signature and applied embedded preconfirmation statuses directly. After the change, the handler calls `signature_verification.check_preconfirmation_signature(&sealed).await` before proceeding with the preconfirmation update path.

## Observed Patch Facts

1. In `crates/services/tx_status_manager/src/service.rs`, the patch replaces `let Sealed {` with `if self`.

2. In `crates/services/tx_status_manager/src/service.rs`, the patch adds `#[tokio::test]`.

3. In `crates/services/tx_status_manager/src/service.rs`, the patch replaces `#[tokio::test]` with `fn arbitrary_pre_confirmation_message(`.

4. In `crates/services/tx_status_manager/src/service.rs`, the patch replaces `FakeSignatureVerification::new_with_handles(true);` with `FakeSignatureVerification::new_with_handles(true, true);`.

## Project Context

The changed code sits primarily in `crates/services/tx_status_manager/src`, `crates/services/tx_status_manager`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/services/tx_status_manager/src/manager.rs`, `crates/services/tx_status_manager/src/update_sender.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/services/tx_status_manager/src/manager.rs`. The strongest project-level identifiers around this patch are `FakeSignatureVerification::new_with_handles`, `signature_verification`, `tracing::debug`, and `tokio::test`. Nearby tests or test-like files include `crates/services/tx_status_manager/src/tests/universe.rs`, `crates/services/tx_status_manager/src/tests/tests_service.rs`.

## Before/After Behavior

Before the patch, the preconfirmation branch destructured `Sealed { signature: _, entity }`, ignored the signature, iterated over `entity.preconfirmations`, converted each status to `TransactionStatus`, and called `self.manager.status_update(tx_id, status)`. The traced manager path records the status and sends a `TxUpdate`. After the patch, the branch keeps the sealed payload intact and gates processing on `check_preconfirmation_signature(&sealed).await`.

# Root Cause

The preconfirmation gossip handler trusted peer-provided sealed preconfirmation contents without first verifying the sealed signature. The supplied before-code explicitly ignored the signature before applying transaction status updates.

## Walkthrough

1. A P2P preconfirmation gossip message reaches `new_preconfirmations_from_p2p`.

2. For `PreConfirmationMessage::Preconfirmations(sealed)`, the old code destructured the sealed payload and discarded `signature`.

3. The old code applied each embedded preconfirmation by calling `manager.status_update`.

4. The downstream manager path records the transaction status and sends update notifications.

5. The patch adds a call to `check_preconfirmation_signature(&sealed).await` before the preconfirmation payload is applied.

6. Tests and helpers were added or updated for the verified preconfirmation path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/services/tx_status_manager/src/service.rs | 133 | P2P preconfirmation message handler dispatching delegate and preconfirmation gossip |
| crates/services/tx_status_manager/src/service.rs | 150 | new signature-verification gate before applying sealed preconfirmation statuses |
| crates/services/tx_status_manager/src/manager.rs | 140 | downstream status_update path that records and sends transaction status changes |
| crates/services/tx_status_manager/src/service.rs | 434 | regression test coverage for verified preconfirmations being sent/applied |

## Code Snippets

## Snippet 1

Context: `crates/services/tx_status_manager/src/service.rs:150` (changes signature or replay validation logic)

Before
```rust
PreConfirmationMessage::Preconfirmations(sealed) => {
                tracing::debug!("Received new preconfirmations from peer");
                let Sealed {
                    signature: _,
                    entity,
                } = sealed;
                entity.preconfirmations.into_iter().for_each(
                    |Preconfirmation { tx_id, status }| {
```
After
```rust
PreConfirmationMessage::Preconfirmations(sealed) => {
                tracing::debug!("Received new preconfirmations from peer");
                if self
                    .signature_verification
                    .check_preconfirmation_signature(&sealed)
                    .await
                {
                    tracing::debug!("Preconfirmation signature verified");
```

## Snippet 2

Context: `crates/services/tx_status_manager/src/service.rs:434` (changes bounds, limits, or capacity handling)

Before
```rust
assert_eq!(actual_protocol_signature, expected_protocol_signature);
    }
}
```
After
```rust
assert_eq!(actual_protocol_signature, expected_protocol_signature);
    }

    #[tokio::test]
    async fn run__when_pre_confirmations_pass_verification_then_send() {
        // given
        let (signature_verification, _) =
            FakeSignatureVerification::new_with_handles(true, true);
```

## Snippet 3

Context: `crates/services/tx_status_manager/src/service.rs:366` (changes signature or replay validation logic)

Before
```rust
}

    #[tokio::test]
    async fn run__when_receive_pre_confirmation_delegations_message_updates_delegate() {
```
After
```rust
}

    fn arbitrary_pre_confirmation_message(
        tx_ids: &[TxId],
    ) -> P2PPreConfirmationGossipData {
        let preconfirmations = tx_ids
            .iter()
            .map(|tx_id| Preconfirmation {
```

## Snippet 4

Context: `crates/services/tx_status_manager/src/service.rs:404` (changes a sensitive control or state-update path)

Before
```rust
// given
        let (signature_verification, mut new_delegate_handle) =
            FakeSignatureVerification::new_with_handles(true);
        let (mut task, sender) =
            new_task_with_signature_verification(signature_verification);
        let delegate_signature_message = arbitrary_delegate_signatures_message();
        let mut state_watcher = StateWatcher::started();
```
After
```rust
// given
        let (signature_verification, mut new_delegate_handle) =
            FakeSignatureVerification::new_with_handles(true, true);
        let (mut task, handles) = new_task_with_handles(signature_verification);
        let delegate_signature_message = arbitrary_delegate_signatures_message();
        let mut state_watcher = StateWatcher::started();
```

# Fix Pattern

Authenticate sealed peer-provided payloads before applying their contents to local protocol state.

## How It Was Fixed

The handler no longer immediately unpacks the sealed preconfirmation entity and ignores its signature. It first passes the full sealed payload to the signature-verification component and proceeds only through the verified branch shown in the after-code.

# Why It Matters

1. Unauthenticated peer gossip could previously influence transaction status state.

2. `status_update` records and broadcasts status changes, so verification must happen before that call.

3. The evidence supports missing signature verification, not replay protection, panic handling, or resource-exhaustion claims.

# Evidence Notes

Primary evidence comes from `crates/services/tx_status_manager/src/service.rs` around the `PreConfirmationMessage::Preconfirmations` branch and tests, plus traced downstream behavior in `crates/services/tx_status_manager/src/manager.rs::status_update`. The evidence does not establish cryptographic soundness of the verifier, freshness semantics, replay protection, or a concrete exploit beyond peer-provided gossip reaching this handler. Protocol security invariant: Incoming P2P preconfirmation gossip must not drive transaction status updates unless the sealed preconfirmation payload passes signature verification. Verification notes: The patch does not prove the signature verification implementation itself is cryptographically sound. The patch does not establish replay protection or freshness semantics for preconfirmation messages. The evidence does not prove a concrete exploit path or attacker capability beyond peer-provided gossip reaching this handler. The delegate-signature branch is not shown to have had the same missing-verification behavior. This is not supported as a malformed-input panic or resource-exhaustion fix by the provided evidence. Before-code shows `signature: _` was discarded in the preconfirmation branch. After-code shows `check_preconfirmation_signature(&sealed).await` was added before verified processing. Downstream `manager.status_update` records and sends transaction status updates. Provided test evidence covers the pass-verification path; reject-path coverage is not established by the supplied snippets. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `missing-signature-verification`
Final impact type: `integrity`
Final tags: `blockchain-core, transaction-processing, p2p, signature-verification, authentication, integrity`

The supplied patch evidence directly supports a security fix: incoming P2P preconfirmation payloads were previously unpacked while discarding the sealed signature and then applied to transaction status state, while the patched code requires check_preconfirmation_signature(&sealed).await before processing. The original liveness-focused classification is misleading; the supported issue is an authentication/signature-verification gate protecting transaction status integrity.

## Security Evidence

1. Before code explicitly ignored the Sealed signature in the Preconfirmations branch.
2. Before code iterated peer-provided preconfirmations and called status_update for each transaction.
3. After code preserves the sealed payload and checks check_preconfirmation_signature(&sealed).await before proceeding.
4. The affected input is incoming P2P preconfirmation gossip, a security-sensitive trust boundary.
5. Downstream status_update records and emits transaction status changes.

## Missing Evidence

1. No evidence that the signature verifier implementation is cryptographically correct.
2. No evidence of replay or freshness protection semantics.
3. No reject-path test is shown in the supplied snippets.
4. No concrete exploit demonstration beyond peer-provided gossip reaching the handler.

## Claim Boundaries

1. Supported as missing signature verification/authentication before applying preconfirmation status updates.
2. Supported impact is transaction status integrity, not liveness failure.
3. Do not claim replay protection, resource exhaustion, malformed-input panic, or verifier correctness from this patch.
4. Delegate-signature handling is not shown to have the same missing-verification issue.
