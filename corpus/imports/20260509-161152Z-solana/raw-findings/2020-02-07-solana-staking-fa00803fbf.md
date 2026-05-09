---
case_id: case_20200207_fa00803fbf
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2020-02-07
source_refs:
  - git:fa00803fbf6e60d4d5ad4bea52aee71fce59993d
  - "core/src/crds_gossip_pull.rs:222"
  - "core/src/cluster_info.rs:1641"
  - "core/src/crds_gossip_push.rs:139"
  - "core/src/cluster_info.rs:1292"
bug_class: gossip-freshness-validation
impact_type:
  - network-state-integrity
  - state-consistency
confidence: medium
tags:
  - blockchain-core
  - gossip
  - crds
  - freshness-validation
  - untrusted-input
  - timestamp-overflow
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds freshness validation for CrdsValue entries received through gossip pull responses before inserting them into CRDS. It also threads stake/epoch-aware timeout data into packet handling and makes related push-message timeout arithmetic overflow-aware. This is plausibly security relevant because the data is peer-supplied gossip input, but the provided evidence does not prove a vulnerability impact beyond stale or future-timestamped values reaching local gossip state.

## Observed Patch Facts

1. In `core/src/crds_gossip_pull.rs`, the patch replaces `let old = crds.insert(r, now);` with `// Check if the crds value is older than the msg_timeout`.

2. In `core/src/cluster_info.rs`, the patch replaces `staking_utils::staked_nodes(&bank_forks.read().unwrap().working_bank())` with `let epoch_ms;`.

3. In `core/src/crds_gossip_push.rs`, the patch replaces `if now > value.wallclock() + self.msg_timeout {` with `if now`.

4. In `core/src/cluster_info.rs`, the patch replaces `packets.packets.iter().for_each(|packet| {` with `epoch_ms: u64,`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `staking` area of the project. Historical context from `core/src/crds_gossip.rs`, `core/src/validator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/crds_gossip.rs`, `core/src/validator.rs`. The strongest project-level identifiers around this patch are `msg_timeout`, `staking_utils::staked_nodes`, `wallclock`, and `bank_forks`.

## Before/After Behavior

Before the patch, process_pull_response iterated over pull-response CrdsValue entries and called crds.insert(r, now) without the explicit wallclock timeout checks shown in the patched code. After the patch, it checks whether each value is expired or too far in the future, applies ContactInfo-specific stake/epoch-derived timeout handling, and only then proceeds toward insertion. ClusterInfo now computes epoch_ms and timeout maps for this policy. The push-message path also replaces direct wallclock + msg_timeout arithmetic with checked_add.

# Root Cause

The supported root cause is incomplete freshness validation in the CRDS pull-response insertion path, plus direct timestamp addition that could overflow in related timeout checks. The evidence does not support broader claims about consensus compromise, privilege bypass, theft, or serialized state representation bugs.

## Walkthrough

1. A node receives a gossip pull response containing CrdsValue entries.

2. Before the patch, the supplied diff shows those values being passed directly to crds.insert(r, now).

3. The patched pull-response path checks r.wallclock() against now and self.msg_timeout before insertion.

4. The patch also checks for values whose wallclock is too far in the future relative to now.

5. For ContactInfo values, the patch consults stake/epoch-derived timeouts before deciding the value is expired.

6. ClusterInfo now derives epoch_ms and builds timeout data used by gossip packet handling.

7. The push-message timeout check now uses checked_add instead of direct addition.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/crds_gossip_pull.rs | 213 | validates CRDS values received via pull responses before inserting them into local CRDS |
| core/src/cluster_info.rs | 1287 | computes stake/epoch-aware CRDS timeouts used while handling incoming gossip packets |
| core/src/cluster_info.rs | 1632 | derives current bank stake map and epoch duration for gossip timeout policy |
| core/src/crds_gossip_push.rs | 134 | applies overflow-safe timeout validation to pushed CRDS values |

## Code Snippets

## Snippet 1

Context: `core/src/crds_gossip_pull.rs:222` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
for r in response {
            let owner = r.label().pubkey();
            let old = crds.insert(r, now);
            failed += old.is_err() as usize;
```
After
```rust
for r in response {
            let owner = r.label().pubkey();
            // Check if the crds value is older than the msg_timeout
            if now
                > r.wallclock()
                    .checked_add(self.msg_timeout)
                    .unwrap_or_else(|| 0)
                || now + self.msg_timeout < r.wallclock()
```

## Snippet 2

Context: `core/src/cluster_info.rs:1641` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
let timeout = Duration::new(1, 0);
        let reqs = requests_receiver.recv_timeout(timeout)?;
        let stakes: HashMap<_, _> = match bank_forks {
            Some(ref bank_forks) => {
                staking_utils::staked_nodes(&bank_forks.read().unwrap().working_bank())
            }
            None => HashMap::new(),
        };
```
After
```rust
let timeout = Duration::new(1, 0);
        let reqs = requests_receiver.recv_timeout(timeout)?;
        let epoch_ms;
        let stakes: HashMap<_, _> = match bank_forks {
            Some(ref bank_forks) => {
                let bank = bank_forks.read().unwrap().working_bank();
                let epoch = bank.epoch();
                let epoch_schedule = bank.epoch_schedule();
```

## Snippet 3

Context: `core/src/crds_gossip_push.rs:139` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
now: u64,
    ) -> Result<Option<VersionedCrdsValue>, CrdsGossipError> {
        if now > value.wallclock() + self.msg_timeout {
            return Err(CrdsGossipError::PushMessageTimeout);
        }
```
After
```rust
now: u64,
    ) -> Result<Option<VersionedCrdsValue>, CrdsGossipError> {
        if now
            > value
                .wallclock()
                .checked_add(self.msg_timeout)
                .unwrap_or_else(|| 0)
        {
```

## Snippet 4

Context: `core/src/cluster_info.rs:1292` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
packets: Packets,
        response_sender: &PacketSender,
    ) {
        // iter over the packets, collect pulls separately and process everything else
        let allocated = thread_mem_usage::Allocatedp::default();
        let mut gossip_pull_data: Vec<PullData> = vec![];
        packets.packets.iter().for_each(|packet| {
            let from_addr = packet.meta.addr();
```
After
```rust
packets: Packets,
        response_sender: &PacketSender,
        epoch_ms: u64,
    ) {
        // iter over the packets, collect pulls separately and process everything else
        let allocated = thread_mem_usage::Allocatedp::default();
        let mut gossip_pull_data: Vec<PullData> = vec![];
        let timeouts = me.read().unwrap().gossip.make_timeouts(&stakes, epoch_ms);
```

# Fix Pattern

Validate peer-supplied gossip state before inserting it into shared local state, using overflow-aware timestamp arithmetic and policy-specific timeout exceptions.

## How It Was Fixed

The fix adds pre-insertion timeout checks in core/src/crds_gossip_pull.rs, introduces stake/epoch-aware timeout computation through core/src/cluster_info.rs, and changes the related push-message timeout comparison in core/src/crds_gossip_push.rs to use checked_add.

# Why It Matters

1. Prevents expired CRDS values from being accepted through the shown pull-response path.

2. Rejects far-future wallclock values according to the patched freshness check.

3. Preserves special timeout handling for staked ContactInfo values.

4. Avoids direct timestamp addition overflow in the shown push-message timeout check.

5. Security impact is plausible but not established by the supplied evidence.

# Evidence Notes

The strongest evidence is the replacement of direct crds.insert(r, now) in core/src/crds_gossip_pull.rs with explicit wallclock freshness checks. Supporting evidence shows epoch_ms and stake-derived timeout data added in core/src/cluster_info.rs, and checked_add added in core/src/crds_gossip_push.rs. The heuristic baseline's staking serialization/state-representation theory is unsupported by the provided diff and should be discarded. The mapper's CRDS gossip freshness framing is better grounded, but its likely-security conclusion is stronger than the evidence proves. Protocol security invariant: Peer-supplied CRDS gossip values should be checked against the protocol freshness window before being inserted into local CRDS state, with stake/epoch-aware timeout handling for ContactInfo values. The provided evidence supports this freshness invariant but does not establish a concrete security exploit. Verification notes: The patch does not prove an attacker can cause consensus divergence. The patch does not prove theft, signature bypass, or privilege escalation. The patch does not show that all stale CRDS values were externally attacker-controlled in every path. The patch does not quantify network impact beyond preventing expired or future-timestamped gossip values from being accepted through pull responses. No evidence proves consensus divergence or network-wide impact. No evidence proves theft, signature bypass, or privilege escalation. No evidence quantifies exploitability of stale CRDS values. Treat as freshness/correctness hardening unless external security impact is shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gossip-freshness-validation`
Final impact type: `network-state-integrity, state-consistency`
Final confidence: `medium`
Final tags: `blockchain-core, gossip, crds, freshness-validation, untrusted-input, timestamp-overflow`

The supplied patch evidence supports a conservative security-hardening classification: peer-supplied CRDS gossip pull responses previously flowed directly into local CRDS insertion, and the patch adds explicit stale and future wallclock rejection plus stake/epoch-aware timeout handling. The related checked_add change also hardens timeout arithmetic against overflow. The evidence does not prove a concrete exploitable vulnerability or network-wide impact, so this should not be treated as a confirmed security fix.

## Security Evidence

1. Pull-response CrdsValue entries are externally supplied gossip input before insertion into local CRDS state.
2. The patch adds pre-insertion timeout checks for expired and far-future wallclock values.
3. The patch threads stake and epoch-derived timeout policy into packet handling for ContactInfo exceptions.
4. The push-message timeout path replaces direct timestamp addition with checked_add.

## Missing Evidence

1. No proof that accepting stale CRDS values caused consensus failure or validator compromise.
2. No demonstrated attacker workflow, exploitability threshold, or network-wide impact.
3. No evidence of theft, signature bypass, privilege escalation, or access-control failure.
4. No proof that the overflow case was reachable as an exploitable condition.

## Claim Boundaries

1. Classify as hardening of gossip freshness validation, not a concrete vulnerability fix.
2. Do not retain the original serialization-or-state-representation bug class.
3. Do not claim consensus divergence or snapshot-related impact from the supplied evidence.
4. Impact should be limited to local/network gossip state integrity and stale/future value rejection.
