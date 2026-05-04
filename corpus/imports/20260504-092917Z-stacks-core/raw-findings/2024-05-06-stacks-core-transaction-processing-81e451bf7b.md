---
case_id: case_20240506_81e451bf7b
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-05-06
source_refs:
  - git:81e451bf7be595b7eb95f853126cedbc0e517611
  - "stacks-signer/src/signer.rs:638"
  - "testnet/stacks-node/src/nakamoto_node/sign_coordinator.rs:496"
  - "libsigner/src/messages.rs:341"
  - "testnet/stacks-node/src/nakamoto_node/miner.rs:429"
bug_class: protocol-context-binding
impact_type:
  - cross-context-message-processing
confidence: medium
tags:
  - validator-ops
  - signer-messages
  - reward-cycle
  - protocol-context-binding
  - consensus-adjacent
  - replay-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes signer message handling so messages carry a reward_cycle and consumers check or unwrap that reward-cycle-scoped structure before processing payloads. The evidence supports a protocol-context binding improvement, but it does not establish an exploitable vulnerability or concrete security impact.

## Observed Patch Facts

1. In `stacks-signer/src/signer.rs`, the patch replaces `let packets: Vec<Packet> = messages` with `let packets: Vec<Packet> =`.

2. In `testnet/stacks-node/src/nakamoto_node/sign_coordinator.rs`, the patch replaces `.filter_map(|msg| match msg {` with `.filter_map(|msg| match msg.message {`.

3. In `libsigner/src/messages.rs`, the patch replaces `impl SignerMessage {` with `/// Serialize the internal components of DkgResults (this eliminates a clone)`.

4. In `testnet/stacks-node/src/nakamoto_node/miner.rs`, the patch replaces `match signer_message {` with `if signer_message.reward_cycle != next_reward_cycle {`.

## Project Context

The changed code sits primarily in `stacks-signer/src`, `testnet/stacks-node/src/nakamoto_node`, `testnet/stacks-node/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `stacks-signer/src/runloop.rs`, `libsigner/src/libsigner.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stacks-signer/src/runloop.rs`, `libsigner/src/libsigner.rs`. The strongest project-level identifiers around this patch are `SignerMessage`, `SignerMessage::Transactions`, `SignerMessage::DkgResults`, and `SignerMessage::BlockResponse`. Nearby tests or test-like files include `testnet/stacks-node/src/tests/signer.rs`, `testnet/stacks-node/src/tests/nakamoto_integrations.rs`.

## Before/After Behavior

Before the change, the shown paths matched directly on SignerMessage variants such as Packet and Transactions. The provided snippets do not show a per-message reward_cycle mismatch check before extracting packets in stacks-signer/src/signer.rs or before accepting Transactions in testnet/stacks-node/src/nakamoto_node/miner.rs. After the change, signer.rs ignores messages whose msg.reward_cycle differs from self.reward_cycle, miner.rs skips signer messages whose reward_cycle differs from next_reward_cycle, and coordinator code matches the inner msg.message as StackerDBMessage. libsigner/src/messages.rs reflects related message API and serialization restructuring.

# Root Cause

The supported root cause is incomplete explicit reward-cycle scoping in the shown message consumption paths. The evidence does not prove that this allowed attacker-controlled replay, signature bypass, invalid block acceptance, fund loss, or consensus failure.

## Walkthrough

1. Signer-related messages include payloads such as Packet, Transactions, DkgResults, BlockResponse, and EncryptedSignerState.

2. Before the patch, the provided snippets show consumers matching directly on SignerMessage variants.

3. The patch introduces or uses a wrapper with reward_cycle and an inner message payload represented as StackerDBMessage in the changed paths.

4. In stacks-signer/src/signer.rs, handle_signer_messages now skips messages whose reward_cycle does not match the signer's reward_cycle before extracting packets.

5. In testnet/stacks-node/src/nakamoto_node/miner.rs, get_signer_transactions now skips messages whose reward_cycle does not match next_reward_cycle before processing Transactions.

6. In testnet/stacks-node/src/nakamoto_node/sign_coordinator.rs, packet handling was updated to match msg.message as StackerDBMessage::Packet.

7. The evidence shows better cycle scoping, but does not establish a concrete vulnerability thesis.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stacks-signer/src/signer.rs | 633 | filters incoming signer messages by the signer's active reward cycle before extracting WSTS packets |
| testnet/stacks-node/src/nakamoto_node/sign_coordinator.rs | 496 | reads packet-bearing StackerDBMessage from the reward-cycle-wrapped signer message structure for coordinator processing |
| testnet/stacks-node/src/nakamoto_node/miner.rs | 369 | collects signer-submitted transactions for the next reward cycle and skips messages tagged for another cycle |
| libsigner/src/messages.rs | 323 | defines signer message slot mapping and serialization surface affected by the reward-cycle message wrapper |

## Code Snippets

## Snippet 1

Context: `stacks-signer/src/signer.rs:638` (changes a sensitive control or state-update path)

Before
```rust
current_reward_cycle: u64,
    ) {
        let packets: Vec<Packet> = messages
            .iter()
            .filter_map(|msg| match msg {
                SignerMessage::DkgResults { .. }
                | SignerMessage::BlockResponse(_)
                | SignerMessage::EncryptedSignerState(_)
```
After
```rust
current_reward_cycle: u64,
    ) {
        let packets: Vec<Packet> =
            messages
                .iter()
                .filter_map(|msg| {
                    if msg.reward_cycle != self.reward_cycle {
                        debug!(
```

## Snippet 2

Context: `testnet/stacks-node/src/nakamoto_node/sign_coordinator.rs:496` (changes signature or replay validation logic)

Before
```rust
let packets: Vec<_> = messages
                .into_iter()
                .filter_map(|msg| match msg {
                    SignerMessage::DkgResults { .. }
                    | SignerMessage::BlockResponse(_)
                    | SignerMessage::EncryptedSignerState(_)
                    | SignerMessage::Transactions(_) => None,
                    SignerMessage::Packet(packet) => {
```
After
```rust
let packets: Vec<_> = messages
                .into_iter()
                .filter_map(|msg| match msg.message {
                    StackerDBMessage::DkgResults { .. }
                    | StackerDBMessage::BlockResponse(_)
                    | StackerDBMessage::EncryptedSignerState(_)
                    | StackerDBMessage::Transactions(_) => None,
                    StackerDBMessage::Packet(packet) => {
```

## Snippet 3

Context: `libsigner/src/messages.rs:341` (changes a consensus- or validator-sensitive branch)

Before
```rust
}
    }
}

impl SignerMessage {
    /// Provide an interface for consensus serializing a DkgResults `SignerMessage`
    ///  without constructing the DkgResults struct (this eliminates a clone)
    pub fn serialize_dkg_result<'a, W: Write, I>(
```
After
```rust
}
    }

    /// Serialize the internal components of DkgResults (this eliminates a clone)
```

## Snippet 4

Context: `testnet/stacks-node/src/nakamoto_node/miner.rs:429` (changes a sensitive control or state-update path)

Before
```rust
let mut filtered_transactions: HashMap<StacksAddress, StacksTransaction> = HashMap::new();
        for (_slot, signer_message) in signer_messages {
            match signer_message {
                SignerMessage::Transactions(transactions) => {
                    NakamotoSigners::update_filtered_transactions(
                        &mut filtered_transactions,
```
After
```rust
let mut filtered_transactions: HashMap<StacksAddress, StacksTransaction> = HashMap::new();
        for (_slot, signer_message) in signer_messages {
            if signer_message.reward_cycle != next_reward_cycle {
                continue;
            }
            match signer_message.message {
                StackerDBMessage::Transactions(transactions) => {
                    NakamotoSigners::update_filtered_transactions(
```

# Fix Pattern

Add explicit protocol-context metadata to serialized messages and check that context before dispatching or consuming message payloads.

## How It Was Fixed

Signer message payloads were moved under a reward-cycle-scoped structure. Runtime consumers were updated to inspect the reward_cycle field and ignore mismatches in the signer and miner paths, and to match the inner StackerDBMessage payload in coordinator handling. Message slot and serialization code was adjusted to support the new structure.

# Why It Matters

1. Reduces accidental processing of wrong-cycle signer messages in the shown paths.

2. Makes reward-cycle context explicit at message consumption points.

3. May reduce replay-like risks across reward cycles, but the provided evidence does not prove exploitability.

# Evidence Notes

Grounded evidence comes from stacks-signer/src/signer.rs:633, testnet/stacks-node/src/nakamoto_node/miner.rs:369, testnet/stacks-node/src/nakamoto_node/sign_coordinator.rs:496, and libsigner/src/messages.rs:323. The security claim must be limited: no unauthenticated injection path, attacker capability, concrete replay exploit, consensus split, invalid block acceptance, or financial impact is shown. Protocol security invariant: Signer messages consumed by Nakamoto signer, coordinator, and miner paths should be associated with the reward cycle they are intended for, and consumers should ignore messages tagged for a different cycle before using their payloads. Verification notes: No direct proof that an unauthenticated remote attacker can inject these messages is shown. No direct proof of signature forgery, private key exposure, or cryptographic break is shown. No concrete consensus split, fund loss, or invalid block acceptance scenario is demonstrated by the patch evidence. Some changes are schema/serialization plumbing; security relevance comes from the new reward-cycle filtering in runtime paths. Verified only against the provided snippets and draft text. No files, commands, or external context were used. Classified as unclear because the patch may be security relevant, but the vulnerability thesis is not established by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-context-binding`
Final impact type: `cross-context-message-processing`
Final confidence: `medium`
Final tags: `validator-ops, signer-messages, reward-cycle, protocol-context-binding, consensus-adjacent, replay-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a concrete security fix. The change adds reward-cycle context to signer messages and rejects mismatched-cycle messages before processing signer packets or signer-submitted transactions in validator/miner paths. That is a clear tightening of protocol-context binding in security-sensitive signer and consensus-adjacent message handling, but the evidence does not prove an attacker capability, exploit path, invalid block acceptance, signature bypass, or financial impact.

## Security Evidence

1. Signer message handling now checks msg.reward_cycle against self.reward_cycle before extracting packets.
2. Miner transaction collection now skips signer messages whose reward_cycle differs from next_reward_cycle.
3. Message handling was refactored so a reward-cycle-scoped wrapper carries the inner StackerDBMessage payload.
4. The changed paths process signer packets, DKG/signing-related messages, and signer-submitted transactions, which are consensus-adjacent and replay-sensitive contexts.

## Missing Evidence

1. No proof that unauthenticated or malicious actors could inject old or wrong-cycle messages.
2. No concrete replay scenario across reward cycles is demonstrated.
3. No evidence of invalid block acceptance, consensus split, signature forgery, key compromise, or fund loss.
4. No commit message or tests in the provided input explicitly frame the change as a security vulnerability fix.

## Claim Boundaries

1. Classify as security hardening, not a confirmed vulnerability fix.
2. Limit the bug class to missing or incomplete protocol-context binding for signer messages.
3. Do not claim signature validation bypass, request forgery, or proven replay exploit.
4. Do not claim concrete consensus failure or financial impact from the supplied evidence alone.
