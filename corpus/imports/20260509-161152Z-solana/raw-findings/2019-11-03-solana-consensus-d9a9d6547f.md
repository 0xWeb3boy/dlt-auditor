---
case_id: case_20191103_d9a9d6547f
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2019-11-03
source_refs:
  - git:d9a9d6547f738169215accdadf3a19f12c9ed130
  - "core/src/crds_value.rs:180"
  - "core/src/cluster_info.rs:1164"
  - "core/src/crds_value.rs:64"
  - "core/src/crds_value.rs:81"
bug_class: signature-identity-binding
impact_type:
  - authenticity
  - identity-binding
tags:
  - blockchain-core
  - gossip
  - crds
  - signature
  - identity-binding
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for incorrect CRDS gossip signing. The evidence shows removal of `Signable` implementations for `CrdsValue`, `Vote`, and `EpochSlots`, and a related gossip pull-request identity check changed to compare `ContactInfo.id` directly. This supports a signature/identity-binding issue, but the supplied snippets do not prove exploitability, forged ledger state, economic impact, or direct consensus failure.

## Observed Patch Facts

1. In `core/src/crds_value.rs`, the patch replaces `impl Signable for CrdsValue {` with `#[cfg(test)]`.

2. In `core/src/cluster_info.rs`, the patch replaces `if caller.contact_info().unwrap().pubkey()` with `if caller.contact_info().unwrap().id == me.read().unwrap().gossip.id {`.

3. In `core/src/crds_value.rs`, the patch replaces `impl Signable for EpochSlots {` with `#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]`.

4. In `core/src/crds_value.rs`, the patch replaces `impl Signable for Vote {` with `/// Type of the replicated value`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `consensus` area of the project. Historical context from `core/src/contact_info.rs`, `core/src/window_service.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/window_service.rs`, `core/src/validator.rs`. The strongest project-level identifiers around this patch are `contact_info`, `CrdsValue::ContactInfo`, `CrdsValue`, and `sign`.

## Before/After Behavior

Before the patch, `CrdsValue` had a `Signable` implementation that delegated signing and verification to concrete variants, and `Vote` and `EpochSlots` had their own `Signable` implementations with signing payload construction. Pull-request loopback detection compared `caller.contact_info().unwrap().pubkey()` to the local gossip id. After the patch, the shown CRDS signing implementations are removed, and the loopback guard compares the embedded `ContactInfo.id` directly to the local gossip id.

# Root Cause

The supported root cause is an incorrect signing or identity-binding path for CRDS gossip values. The evidence indicates that signing logic was available through wrapper or per-variant `Signable` implementations and that at least one gossip identity check used a derived `pubkey()` accessor rather than the embedded `ContactInfo.id`. The exact replacement design and exploit path are not shown.

## Walkthrough

1. A gossip blob is deserialized and handled as a `Protocol::PullRequest(filter, caller)` in `ClusterInfo::handle_blobs`.

2. The caller is verified with `caller.verify()` before contact information is used.

3. Before the patch, `CrdsValue` implemented `Signable` by delegating signing and verification across variants.

4. Before the patch, `Vote` and `EpochSlots` also implemented `Signable` and built their own signable payloads.

5. The patch removes the shown signing implementations from `core/src/crds_value.rs`.

6. The patch changes self-loop detection to compare `ContactInfo.id` directly with the local gossip id.

7. Together with the commit title, this supports a likely CRDS signature-binding fix, without proving a concrete remote attack.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/crds_value.rs | 180 | Removed wrapper-level Signable implementation for CrdsValue that delegated signing and verification across value variants. |
| core/src/crds_value.rs | 64 | Removed EpochSlots Signable implementation and its canonical signable_data construction. |
| core/src/crds_value.rs | 81 | Removed Vote Signable implementation and its canonical signable_data construction. |
| core/src/cluster_info.rs | 1164 | Changed gossip PullRequest self-loop detection to compare the embedded ContactInfo.id against the local gossip id. |

## Code Snippets

## Snippet 1

Context: `core/src/crds_value.rs:180` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

impl Signable for CrdsValue {
    fn sign(&mut self, keypair: &Keypair) {
        match self {
            CrdsValue::ContactInfo(contact_info) => contact_info.sign(keypair),
            CrdsValue::Vote(vote) => vote.sign(keypair),
            CrdsValue::EpochSlots(epoch_slots) => epoch_slots.sign(keypair),
```
After
```rust
}

#[cfg(test)]
mod test {
```

## Snippet 2

Context: `core/src/cluster_info.rs:1164` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
);
                        } else if caller.contact_info().is_some() {
                            if caller.contact_info().unwrap().pubkey()
                                == me.read().unwrap().gossip.id
                            {
                                warn!("PullRequest ignored, I'm talking to myself");
                                inc_new_counter_debug!("cluster_info-window-request-loopback", 1);
```
After
```rust
);
                        } else if caller.contact_info().is_some() {
                            if caller.contact_info().unwrap().id == me.read().unwrap().gossip.id {
                                warn!("PullRequest ignored, I'm talking to myself");
                                inc_new_counter_debug!("cluster_info-window-request-loopback", 1);
```

## Snippet 3

Context: `core/src/crds_value.rs:64` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

impl Signable for EpochSlots {
    fn pubkey(&self) -> Pubkey {
        self.from
    }

    fn signable_data(&self) -> Cow<[u8]> {
```
After
```rust
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct Vote {
    pub from: Pubkey,
    pub transaction: Transaction,
    pub wallclock: u64,
}
```

## Snippet 4

Context: `core/src/crds_value.rs:81` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

impl Signable for Vote {
    fn pubkey(&self) -> Pubkey {
        self.from
    }

    fn signable_data(&self) -> Cow<[u8]> {
```
After
```rust
}

/// Type of the replicated value
/// These are labels for values in a record that is associated with `Pubkey`
```

# Fix Pattern

Remove incorrect CRDS signing paths and use the concrete embedded identity for identity-sensitive gossip checks.

## How It Was Fixed

The patch removes the shown `Signable` implementations for `CrdsValue`, `Vote`, and `EpochSlots` from `core/src/crds_value.rs`. It also updates `core/src/cluster_info.rs` so pull-request loopback detection compares `caller.contact_info().unwrap().id` directly against `me.read().unwrap().gossip.id`.

# Why It Matters

1. CRDS gossip records are identity-sensitive replicated state.

2. Incorrect signing semantics can undermine authenticity assumptions for gossip data.

3. Using the embedded concrete identity reduces ambiguity in peer identity checks.

4. The evidence does not establish forged ledger entries, economic loss, or direct consensus failure.

# Evidence Notes

Grounded evidence is limited to the commit title, removal of CRDS-related `Signable` implementations in `core/src/crds_value.rs`, and the `contact_info().pubkey()` to `ContactInfo.id` loopback check change in `core/src/cluster_info.rs`. Claims about RPC boundaries, canonical serialized state transfer, consensus failure, or economic impact are unsupported by the provided snippets. Protocol security invariant: CRDS gossip records should be signed and verified using the identity and payload semantics of the concrete value being gossiped, so peers cannot rely on a mismatched wrapper or derived identity path for authenticity checks. Verification notes: The patch does not prove remote exploitability by itself. The evidence does not show forged ledger entries or direct consensus safety failure. The evidence does not prove economic loss or privilege escalation. The broader test changes are not shown, so regression coverage details cannot be assessed. This should not be classified as a generic serialization/RPC boundary issue from the provided patch evidence. Full replacement signing logic is not shown. Updated tests are listed but not included in the provided evidence. Exploitability is not demonstrated. Classification should stay narrower than consensus or RPC serialization. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-identity-binding`
Final impact type: `authenticity, identity-binding`
Final tags: `blockchain-core, gossip, crds, signature, identity-binding, validator`

The supplied evidence supports retaining this as a security-hardening case, not a proven security-fix. The commit title says incorrectly signed CRDS values, and the patch removes signing/verification paths for CRDS values while changing a gossip identity check to use the embedded ContactInfo id. That is clearly security-sensitive authenticity and identity-binding behavior, but the snippets do not prove exploitability, consensus compromise, forged ledger state, or concrete attacker impact.

## Security Evidence

1. Commit subject explicitly identifies incorrectly signed CrdsValues.
2. Patch removes Signable implementation for CrdsValue that delegated signing and verification across variants.
3. Patch removes Signable implementations for Vote and EpochSlots, both identity-bearing CRDS gossip values.
4. Gossip PullRequest handling verifies caller data and then changes self-loop detection from contact_info().pubkey() to the embedded ContactInfo.id.
5. Changed code is in network gossip/validator core paths where signatures and identity binding are security-sensitive.

## Missing Evidence

1. No test diff is provided showing the exact incorrect-signing regression or attack scenario.
2. No replacement signing design is shown, so the full before/after security invariant is incomplete.
3. No evidence proves remote exploitability, forged gossip acceptance, consensus safety failure, or economic impact.
4. No evidence supports the original RPC tag or broad client-view-divergence claim.

## Claim Boundaries

1. Classify as CRDS gossip signature and identity-binding hardening, not a demonstrated consensus exploit.
2. Do not claim ledger forgery, fund loss, privilege escalation, or direct consensus failure from the supplied patch alone.
3. Do not treat this as a generic serialization/state-representation bug without stronger evidence.
4. Keep impact limited to authenticity and identity binding of gossip values.
