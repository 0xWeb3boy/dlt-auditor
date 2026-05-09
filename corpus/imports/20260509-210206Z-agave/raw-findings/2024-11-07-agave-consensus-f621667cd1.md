---
case_id: case_20241107_f621667cd1
project: agave
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2024-11-07
source_refs:
  - git:f621667cd1d159142a57922ee4e9fb49ec0182ff
  - "gossip/src/crds_value.rs:96"
  - "gossip/src/crds_data.rs:541"
  - "gossip/src/protocol.rs:662"
  - "gossip/src/cluster_info.rs:812"
bug_class: unauthenticated-constructor-exposure
impact_type:
  - message-authentication
  - authenticity
confidence: high
tags:
  - blockchain-core
  - gossip
  - crds
  - signature
  - api-hardening
  - message-authentication
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is security-relevant API hardening for Agave gossip CRDS construction, but the provided evidence does not establish an actual vulnerability or exploitable production path. The strongest supported claim is that unsigned CrdsValue construction was removed from the normal public interface and kept only for cfg(test).

## Observed Patch Facts

1. In `gossip/src/crds_value.rs`, the patch replaces `pub fn new_unsigned(data: CrdsData) -> Self {` with `pub fn new(data: CrdsData, keypair: &Keypair) -> Self {`.

2. In `gossip/src/crds_data.rs`, the patch replaces `let vote = CrdsValue::new_signed(CrdsData::Vote(MAX_VOTES, vote), &keypair);` with `let vote = CrdsValue::new(CrdsData::Vote(MAX_VOTES, vote), &keypair);`.

3. In `gossip/src/protocol.rs`, the patch replaces `let vote = CrdsValue::new_signed(CrdsData::Vote(1, vote), &Keypair::new());` with `let vote = CrdsValue::new(CrdsData::Vote(1, vote), &Keypair::new());`.

4. In `gossip/src/cluster_info.rs`, the patch replaces `let vote = CrdsValue::new_signed(vote, &self.keypair());` with `let vote = CrdsValue::new(vote, &self.keypair());`.

## Project Context

The changed code sits primarily in `gossip/src`, which anchors the finding in the `consensus` area of the project. Historical context from `gossip/src/crds_gossip_pull.rs`, `gossip/src/crds.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `gossip/src/crds_gossip_pull.rs`, `gossip/src/crds.rs`. The strongest project-level identifiers around this patch are `vote`, `CrdsData::Vote`, `Keypair::new`, and `CrdsValue::new_signed`.

## Before/After Behavior

Before the patch, CrdsValue exposed a public new_unsigned(data) constructor that created a value with Signature::default(), while signed construction existed separately as new_signed. After the patch, CrdsValue::new(data, keypair) serializes the CrdsData and signs it with the provided keypair, and new_unsigned is restricted to #[cfg(test)] pub(crate). Runtime vote construction shown in ClusterInfo::push_vote_at_index uses the signed constructor before inserting into CRDS. Most other shown call-site changes are mechanical renames from new_signed to new.

# Root Cause

The production API allowed unsigned CRDS value construction as a public constructor, so the intended invariant that normal CRDS values are signed was not encoded in the public construction interface. The evidence does not show that production code actually misused that constructor.

## Walkthrough

1. CrdsValue represents data stored and propagated through gossip CRDS.

2. The pre-patch evidence shows new_unsigned constructing a CrdsValue with Signature::default().

3. The patch introduces CrdsValue::new(data, keypair) as the public constructor that signs serialized CrdsData.

4. The unsigned constructor is moved behind #[cfg(test)] and pub(crate), limiting it to test builds.

5. ClusterInfo::push_vote_at_index constructs local vote CRDS values through the signed constructor before CRDS insertion.

6. Test and protocol call sites are updated from new_signed to new, mostly reflecting the rename.

7. A traced gossip push test still uses new_unsigned, but only in test context.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| gossip/src/crds_value.rs | 96 | Defines CrdsValue production construction as signed and restricts unsigned construction to tests. |
| gossip/src/cluster_info.rs | 812 | Creates local vote CRDS values for insertion into gossip CRDS using the signed constructor. |
| gossip/src/crds_data.rs | 541 | Updates vote-related tests to use the signed default constructor name. |
| gossip/src/protocol.rs | 662 | Updates protocol size tests to use the signed default constructor name. |
| gossip/src/crds_gossip_push.rs | 297 | Shows unsigned CRDS construction remains available only inside test code paths. |

## Code Snippets

## Snippet 1

Context: `gossip/src/crds_value.rs:96` (changes signature or replay validation logic)

Before
```rust
impl CrdsValue {
    pub fn new_unsigned(data: CrdsData) -> Self {
        Self {
            signature: Signature::default(),
```
After
```rust
impl CrdsValue {
    pub fn new(data: CrdsData, keypair: &Keypair) -> Self {
        let bincode_serialized_data = bincode::serialize(&data).unwrap();
        let signature = keypair.sign_message(&bincode_serialized_data);
        Self { signature, data }
    }
```

## Snippet 2

Context: `gossip/src/crds_data.rs:541` (changes a consensus- or validator-sensitive branch)

Before
```rust
let keypair = Keypair::new();
        let vote = Vote::new(keypair.pubkey(), new_test_vote_tx(&mut rng), timestamp()).unwrap();
        let vote = CrdsValue::new_signed(CrdsData::Vote(MAX_VOTES, vote), &keypair);
        assert!(vote.sanitize().is_err());
    }
```
After
```rust
let keypair = Keypair::new();
        let vote = Vote::new(keypair.pubkey(), new_test_vote_tx(&mut rng), timestamp()).unwrap();
        let vote = CrdsValue::new(CrdsData::Vote(MAX_VOTES, vote), &keypair);
        assert!(vote.sanitize().is_err());
    }
```

## Snippet 3

Context: `gossip/src/protocol.rs:662` (changes a consensus- or validator-sensitive branch)

Before
```rust
)
        .unwrap();
        let vote = CrdsValue::new_signed(CrdsData::Vote(1, vote), &Keypair::new());
        assert!(bincode::serialized_size(&vote).unwrap() <= PUSH_MESSAGE_MAX_PAYLOAD_SIZE as u64);
    }
```
After
```rust
)
        .unwrap();
        let vote = CrdsValue::new(CrdsData::Vote(1, vote), &Keypair::new());
        assert!(bincode::serialized_size(&vote).unwrap() <= PUSH_MESSAGE_MAX_PAYLOAD_SIZE as u64);
    }
```

## Snippet 4

Context: `gossip/src/cluster_info.rs:812` (changes a consensus- or validator-sensitive branch)

Before
```rust
let vote = Vote::new(self_pubkey, vote, now).unwrap();
        let vote = CrdsData::Vote(vote_index, vote);
        let vote = CrdsValue::new_signed(vote, &self.keypair());
        let mut gossip_crds = self.gossip.crds.write().unwrap();
        if let Err(err) = gossip_crds.insert(vote, now, GossipRoute::LocalMessage) {
```
After
```rust
let vote = Vote::new(self_pubkey, vote, now).unwrap();
        let vote = CrdsData::Vote(vote_index, vote);
        let vote = CrdsValue::new(vote, &self.keypair());
        let mut gossip_crds = self.gossip.crds.write().unwrap();
        if let Err(err) = gossip_crds.insert(vote, now, GossipRoute::LocalMessage) {
```

# Fix Pattern

Make the authenticated constructor the default public API and confine unauthenticated construction helpers to test-only visibility.

## How It Was Fixed

The patch renamed the signed constructor to CrdsValue::new, made it serialize CrdsData and sign the bytes with a Keypair, and changed new_unsigned to #[cfg(test)] pub(crate). Existing signed call sites were updated to the new constructor name.

# Why It Matters

1. CRDS gossip values rely on signatures for authenticity.

2. A public unsigned constructor can weaken API-level enforcement of signing expectations.

3. The patch reduces accidental creation of default-signature CRDS values in production code.

4. The evidence does not prove a remote exploit, missing verification, or consensus safety failure.

# Evidence Notes

Supported by gossip/src/crds_value.rs showing signed construction and test-only unsigned construction, plus gossip/src/cluster_info.rs showing a runtime vote path using CrdsValue::new before CRDS insertion. The shown crds_data.rs and protocol.rs hunks are test renames. The evidence does not prove production code previously created unsigned CRDS values, does not show acceptance of unsigned remote gossip values, and does not establish exploitability. Protocol security invariant: Production CRDS values should be signed over their serialized CrdsData by the appropriate keypair before storage or gossip propagation. The patch makes signed construction the default public constructor and restricts unsigned construction to test code. Verification notes: The patch does not prove that production code was actually constructing unsigned CRDS values before the change. The patch does not show missing signature verification on received gossip messages. The patch does not establish a remote exploit path. The patch does not prove a consensus safety violation; the directly affected subsystem is gossip CRDS. Most call-site changes are constructor renames without behavioral change. Treat as security-relevant hardening, not a confirmed vulnerability fix. Do not classify as consensus state corruption based on the provided evidence. Do not claim a remote attack path or missing signature verification. Exclude from the vulnerability security corpus unless additional evidence shows production misuse or exploitability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unauthenticated-constructor-exposure`
Final impact type: `message-authentication, authenticity`
Final confidence: `high`
Final tags: `blockchain-core, gossip, crds, signature, api-hardening, message-authentication`

The supplied evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The patch makes signed CRDS value construction the default public API and confines unsigned construction to test builds, directly tightening a signature/authentication invariant for gossip CRDS values. The evidence does not prove prior production misuse, remote acceptance of unsigned values, or consensus state corruption.

## Security Evidence

1. Commit message states that except for cfg(test), all CrdsValues should be signed.
2. CrdsValue::new now serializes CrdsData and signs it with the provided Keypair.
3. new_unsigned is restricted to #[cfg(test)] pub(crate), removing it from the normal public interface.
4. Runtime vote construction continues through the signed constructor before CRDS insertion.

## Missing Evidence

1. No evidence that production code previously called new_unsigned.
2. No evidence that unsigned remote gossip values were accepted without verification.
3. No exploit path or attacker-controlled input path is shown.
4. No demonstrated consensus safety failure or state corruption is shown.

## Claim Boundaries

1. Classify as API-level security hardening around CRDS signatures.
2. Do not classify as a proven vulnerability fix.
3. Do not claim remote exploitability from the provided patch alone.
4. Do not retain the original state-corruption or snapshot framing.
