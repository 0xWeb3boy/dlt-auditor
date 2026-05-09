---
case_id: case_20201020_25078d46ba
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: medium
date: 2020-10-20
source_refs:
  - git:25078d46baed14e4f9b8617a8afa36629a1fa047
  - "core/src/crds_gossip_push.rs:372"
  - "core/src/crds_gossip_pull.rs:282"
  - "core/src/crds_gossip_push.rs:794"
  - "core/src/crds_gossip_push.rs:677"
bug_class: gossip-stale-peer-fanout
impact_type:
  - availability
tags:
  - blockchain-core
  - gossip
  - crds
  - availability
  - dos-mitigation
  - validator
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Solana CRDS gossip push target selection by filtering inactive peers out of normal push options. The evidence supports a gossip-layer availability hardening for redundant traffic toward offline or stale nodes, not a consensus, signature, or funds-loss vulnerability.

## Observed Patch Facts

1. In `core/src/crds_gossip_push.rs`, the patch replaces `.filter(|v| v.value.contact_info().is_some())` with `let now = timestamp();`.

2. In `core/src/crds_gossip_pull.rs`, the patch replaces `let old = crds.insert(caller, now);` with `if let Ok(Some(val)) = crds.insert(caller, now) {`.

3. In `core/src/crds_gossip_push.rs`, the patch replaces `assert_eq!(crds.insert(peer_1.clone(), 0), Ok(None));` with `assert_eq!(crds.insert(peer_1.clone(), now), Ok(None));`.

4. In `core/src/crds_gossip_push.rs`, the patch replaces `crds.insert(me.clone(), 0).unwrap();` with `crds.insert(me.clone(), now).unwrap();`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `consensus` area of the project. Historical context from `core/src/crds_value.rs`, `core/src/crds_shards.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/verified_vote_packets.rs`, `core/src/rpc_service.rs`. The strongest project-level identifiers around this patch are `crds`, `insert`, `clone`, and `unwrap`.

## Before/After Behavior

Before the patch, the visible `CrdsGossipPush::push_options` path selected CRDS entries with contact info and applied other target filters, but the supplied evidence does not show a freshness cutoff based on `local_timestamp`. After the patch, `push_options` computes `now`, derives `active_cutoff` from `PUSH_ACTIVE_TIMEOUT_MS`, and filters candidates whose local timestamp is too old, with documented special handling for staked nodes. Tests were updated to insert peers using the current timestamp instead of `0`, consistent with old timestamps now being stale. The pull-side change to directly match `Ok(Some(val))` from `crds.insert(caller, now)` appears adjacent cleanup and is not established as an independent security fix.

# Root Cause

The root cause supported by the evidence is missing freshness filtering in CRDS gossip push target selection. Stale or offline peers could remain eligible push targets, which the commit message says caused redundant duplicate gossip traffic to be pushed toward nodes that were no longer active.

## Walkthrough

1. `core/src/crds_gossip_push.rs` selects gossip push targets in `CrdsGossipPush::push_options`.

2. The before snippet filters for values with `contact_info()` but does not show a `local_timestamp` freshness cutoff.

3. The patch adds `timestamp()` and computes `active_cutoff` using `PUSH_ACTIVE_TIMEOUT_MS`.

4. The candidate pipeline changes to `filter_map`, allowing the code to drop entries without contact info and reject stale entries in one path.

5. The new guard checks whether `value.local_timestamp < active_cutoff` and comments that nodes not active recently should stop receiving pushes.

6. The commit message ties this to offline nodes seeing traffic spikes from redundant duplicate push messages.

7. Staked-node retry behavior is described in the commit message and comments as an eclipse-mitigation tradeoff.

8. Tests in `crds_gossip_push.rs` now use current timestamps so fixtures remain active under the new filtering rule.

9. The `crds_gossip_pull.rs` insertion-result simplification is treated as support cleanup, not the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/crds_gossip_push.rs | 366 | Selects CRDS gossip push targets and now applies active-peer freshness filtering before a peer can receive push messages. |
| core/src/crds_gossip_push.rs | 372 | Introduces current-time, active-cutoff, and randomized/stake-aware retry logic for inactive target exclusion and eclipse mitigation. |
| core/src/crds_gossip_pull.rs | 276 | Processes pull requests and records caller timestamps; changed insertion-result handling is adjacent freshness bookkeeping, not the core fix. |
| core/src/crds_gossip_push.rs | 646 | Regression test setup updated to insert peers with current timestamps so active filtering does not treat fixtures as stale. |
| core/src/crds_gossip_push.rs | 788 | Push-message personalization test updated to use current timestamps under the new active-peer selection invariant. |

## Code Snippets

## Snippet 1

Context: `core/src/crds_gossip_push.rs:372` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
gossip_validators: Option<&HashSet<Pubkey>>,
    ) -> Vec<(f32, &'a ContactInfo)> {
        crds.table
            .values()
            .filter(|v| v.value.contact_info().is_some())
            .map(|v| (v.value.contact_info().unwrap(), v))
            .filter(|(info, _)| {
                info.id != *self_id
```
After
```rust
gossip_validators: Option<&HashSet<Pubkey>>,
    ) -> Vec<(f32, &'a ContactInfo)> {
        let now = timestamp();
        let mut rng = rand::thread_rng();
        let max_weight = u16::MAX as f32 - 1.0;
        let active_cutoff = now.saturating_sub(PUSH_ACTIVE_TIMEOUT_MS);
        crds.table
            .values()
```

## Snippet 2

Context: `core/src/crds_gossip_pull.rs:282` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
requests.into_iter().for_each(|(caller, _)| {
            let key = caller.label().pubkey();
            let old = crds.insert(caller, now);
            if let Some(val) = old.ok().and_then(|opt| opt) {
                self.purged_values
                    .push_back((val.value_hash, val.local_timestamp));
```
After
```rust
requests.into_iter().for_each(|(caller, _)| {
            let key = caller.label().pubkey();
            if let Ok(Some(val)) = crds.insert(caller, now) {
                self.purged_values
                    .push_back((val.value_hash, val.local_timestamp));
```

## Snippet 3

Context: `core/src/crds_gossip_push.rs:794` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
0,
        )));
        assert_eq!(crds.insert(peer_1.clone(), 0), Ok(None));
        let peer_2 = CrdsValue::new_unsigned(CrdsData::ContactInfo(ContactInfo::new_localhost(
            &Pubkey::new_rand(),
            0,
        )));
        assert_eq!(crds.insert(peer_2.clone(), 0), Ok(None));
```
After
```rust
0,
        )));
        assert_eq!(crds.insert(peer_1.clone(), now), Ok(None));
        let peer_2 = CrdsValue::new_unsigned(CrdsData::ContactInfo(ContactInfo::new_localhost(
            &Pubkey::new_rand(),
            0,
        )));
        assert_eq!(crds.insert(peer_2.clone(), now), Ok(None));
```

## Snippet 4

Context: `core/src/crds_gossip_push.rs:677` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}));

        crds.insert(me.clone(), 0).unwrap();
        crds.insert(spy.clone(), 0).unwrap();
        crds.insert(node_123.clone(), 0).unwrap();
        crds.insert(node_456, 0).unwrap();

        // shred version 123 should ignore nodes with versions 0 and 456
```
After
```rust
}));

        crds.insert(me.clone(), now).unwrap();
        crds.insert(spy.clone(), now).unwrap();
        crds.insert(node_123.clone(), now).unwrap();
        crds.insert(node_456, now).unwrap();

        // shred version 123 should ignore nodes with versions 0 and 456
```

# Fix Pattern

Add freshness-aware eligibility checks at the gossip push target-selection point, excluding stale peers from routine fanout while preserving bounded retry behavior for staked peers.

## How It Was Fixed

The patch computes a current active cutoff inside `CrdsGossipPush::push_options` and filters CRDS contact candidates whose `local_timestamp` is older than that cutoff. It updates tests to use current timestamps for active peer fixtures. It also simplifies pull-request insertion-result handling, but the supplied evidence does not make that pull-side change security-critical.

# Why It Matters

1. Reduces redundant gossip push traffic toward offline or stale peers.

2. Keeps gossip fanout focused on recently active contacts.

3. Addresses an availability concern described as offline-node DDOS traffic in the commit message.

4. Avoids claiming unsupported consensus, cryptographic, or funds-loss impact.

5. Staked-peer retry behavior limits the anti-eclipse tradeoff of filtering inactive nodes.

# Evidence Notes

Primary evidence is the `core/src/crds_gossip_push.rs` change adding `now`, `active_cutoff`, and a stale-peer guard in `CrdsGossipPush::push_options`. The commit body explicitly references an offline-node DDOS issue, redundant duplicate push messages, and periodic retries for staked nodes to mitigate eclipse attacks. Test changes from timestamp `0` to `now` support the conclusion that stale timestamps now affect push eligibility. The evidence does not prove attacker control, traffic magnitude, network-wide denial of service, consensus safety impact, or financial loss. Protocol security invariant: CRDS gossip push target selection should avoid routinely sending push traffic to peers that have not been recently active, while retaining bounded retry behavior for staked peers so inactive filtering does not create an eclipse risk. Verification notes: The patch does not prove an attacker can force peers offline. The patch does not prove a full network-wide denial of service from the old behavior. The patch does not show a consensus safety, signature, or funds-loss issue. The pull-request insertion cleanup is not proven to be independently security-relevant. The evidence does not quantify the traffic spike or remaining residual load. The patch is best treated as gossip availability hardening, not a confirmed exploit chain. Supported: inactive-peer filtering was added to gossip push target selection. Supported: tests were adjusted for current timestamps under the new freshness rule. Supported by commit text: the motivation was reducing offline-node traffic spikes and preserving staked-node retry behavior. Not supported: confirmed exploitability or quantified denial-of-service impact. Not supported: treating the pull-side cleanup as a separate vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gossip-stale-peer-fanout`
Final impact type: `availability`
Final tags: `blockchain-core, gossip, crds, availability, dos-mitigation, validator`

The supplied evidence supports retaining this as security hardening. The commit message explicitly ties the change to an offline-node DDOS traffic issue and eclipse-mitigation tradeoff, and the patch adds active-peer freshness filtering in CRDS gossip push target selection. The evidence does not support the original consensus, serialization/state-representation, RPC, snapshot, or signature framing.

## Security Evidence

1. Commit body references a DDOS issue involving nodes that go offline and redundant duplicate push traffic.
2. `push_options` now computes an active cutoff from the current timestamp and `PUSH_ACTIVE_TIMEOUT_MS`.
3. The new push-target logic filters out peers whose `local_timestamp` is older than the active cutoff.
4. Comments and commit text describe periodic retry behavior for staked nodes to mitigate eclipse attacks.
5. Tests were updated from timestamp `0` to current timestamps, consistent with stale peers now being excluded from normal push options.

## Missing Evidence

1. No proof of attacker-controlled offline status or an end-to-end exploit chain.
2. No quantified traffic amplification or demonstrated network-wide denial of service.
3. No evidence of consensus safety failure, funds loss, signature bypass, RPC exposure, or snapshot issue.
4. The `crds_gossip_pull.rs` change is not shown to be independently security-relevant.

## Claim Boundaries

1. Validated only as gossip-layer availability hardening.
2. The supported fix is filtering inactive or stale peers from routine CRDS gossip push targets.
3. Do not classify this as a consensus, serialization, state-consistency, signature, RPC, or snapshot vulnerability.
4. Do not claim a confirmed exploitable DoS beyond the commit-described DDOS mitigation context.
