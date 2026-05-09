---
case_id: case_20200214_535ee281e8
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2020-02-14
source_refs:
  - git:535ee281e8ac013dc4486cd9faa038f34cf5952e
  - "core/src/crds_gossip_pull.rs:222"
  - "core/src/cluster_info.rs:1637"
  - "core/src/crds_gossip_push.rs:139"
  - "core/src/cluster_info.rs:1288"
bug_class: peer-gossip-freshness-validation
impact_type:
  - gossip-state-integrity
  - stale-peer-data-rejection
confidence: medium
tags:
  - blockchain-core
  - gossip
  - crds
  - peer-input-validation
  - freshness-check
  - checked-arithmetic
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit stale and future wallclock filtering for CRDS gossip pull responses before insertion into CRDS, threads stake/epoch-derived timeout data into packet handling, and changes a push timeout check to use checked_add. This is plausibly security relevant because gossip data is peer supplied, but the provided evidence does not establish a concrete vulnerability, exploit path, consensus impact, or direct safety failure.

## Observed Patch Facts

1. In `core/src/crds_gossip_pull.rs`, the patch replaces `let old = crds.insert(r, now);` with `// Check if the crds value is older than the msg_timeout`.

2. In `core/src/cluster_info.rs`, the patch replaces `staking_utils::staked_nodes(&bank_forks.read().unwrap().working_bank())` with `let epoch_ms;`.

3. In `core/src/crds_gossip_push.rs`, the patch replaces `if now > value.wallclock() + self.msg_timeout {` with `if now`.

4. In `core/src/cluster_info.rs`, the patch replaces `packets.packets.iter().for_each(|packet| {` with `epoch_ms: u64,`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `staking` area of the project. Historical context from `core/src/crds_gossip.rs`, `core/src/validator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/crds_gossip.rs`, `core/src/validator.rs`. The strongest project-level identifiers around this patch are `msg_timeout`, `staking_utils::staked_nodes`, `wallclock`, and `bank_forks`.

## Before/After Behavior

Before the patch, the shown pull-response loop took each CrdsValue owner and immediately called crds.insert(r, now), with no explicit freshness filter visible in the provided snippet. After the patch, process_pull_response checks whether the value is older than msg_timeout or too far in the future before insertion, with ContactInfo-specific handling that may use a timeout map. ClusterInfo now builds that timeout map using stakes and epoch_ms. The push path changes one timeout comparison from direct addition to checked_add.

# Root Cause

The grounded root cause is incomplete explicit freshness validation in the shown CRDS gossip pull-response ingestion path. Claims about a proven security exploit, consensus failure, arbitrary wallclock control, or direct fund impact are not supported by the provided evidence.

## Walkthrough

1. A peer sends CRDS values as a gossip pull response.

2. Before the patch, the provided loop inserted each response value into CRDS without an explicit age or future-time check shown at that call site.

3. After the patch, each value is compared against local now and msg_timeout before insertion.

4. Values too old or too far in the future enter rejection or label-specific handling.

5. ClusterInfo now passes epoch_ms into packet handling so gossip can build stake/epoch-based timeout policy.

6. The push message timeout check now uses checked_add for the wallclock-plus-timeout comparison.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/crds_gossip_pull.rs | 213 | validates CrdsValue freshness from pull responses before insertion into CRDS |
| core/src/cluster_info.rs | 1283 | builds stake and epoch-based timeout map used while handling gossip packets |
| core/src/cluster_info.rs | 1628 | derives current epoch duration and staked nodes from BankForks for gossip timeout policy |
| core/src/crds_gossip_push.rs | 134 | uses checked arithmetic for push message timeout validation |

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

Context: `core/src/cluster_info.rs:1637` (changes how canonical state is encoded, returned, or reconstructed)

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

Context: `core/src/cluster_info.rs:1288` (changes how canonical state is encoded, returned, or reconstructed)

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

Validate peer-supplied gossip records at the ingestion boundary before updating shared CRDS state, and use checked arithmetic for timeout comparisons where changed.

## How It Was Fixed

The fix added wallclock freshness checks in core/src/crds_gossip_pull.rs, threaded epoch_ms through ClusterInfo packet handling, constructed timeout policy from stakes and epoch duration, and replaced one direct wallclock + msg_timeout calculation in crds_gossip_push.rs with checked_add.

# Why It Matters

1. CRDS gossip state is populated from peer-supplied network data.

2. Stale or future-dated records can affect node-visible gossip state if accepted.

3. Stake and epoch context appear to influence ContactInfo timeout policy.

4. The evidence supports correctness or hardening, not a confirmed vulnerability.

# Evidence Notes

Strong evidence supports a CRDS gossip freshness-validation change. The heuristic baseline claiming staking serialization or canonical object transfer is unsupported and should be discarded. The mapper's high-confidence security classification is too strong because the evidence does not prove exploitability or concrete security impact. Protocol security invariant: CRDS gossip should avoid accepting peer-supplied records from pull responses when their wallclock is outside the allowed freshness window. The patch also makes one timeout addition in the push path overflow-aware. Verification notes: The patch does not prove remote code execution, key compromise, or direct fund loss. The patch does not show that stale CRDS values necessarily cause consensus failure. The evidence does not prove an attacker can choose arbitrary accepted wallclock values beyond sending gossip data. The stake-based ContactInfo timeout behavior is inferred from the changed parameters and comments, not fully proven from complete implementation context. The push-path checked_add change shows overflow-safe validation, but no concrete pre-patch overflow exploit is demonstrated. No evidence of RCE, key compromise, direct fund loss, or proven consensus failure. No complete ContactInfo timeout implementation was provided, so stake-derived behavior is only partially grounded. The checked_add change is real, but no pre-patch overflow exploit is demonstrated. Treat as plausible hardening/correctness unless additional advisory or exploit evidence is supplied. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `peer-gossip-freshness-validation`
Final impact type: `gossip-state-integrity, stale-peer-data-rejection`
Final confidence: `medium`
Final tags: `blockchain-core, gossip, crds, peer-input-validation, freshness-check, checked-arithmetic, validator`

The patch clearly adds freshness validation for peer-supplied CRDS gossip pull responses before inserting them into shared gossip state, adds future-wallclock rejection, threads stake/epoch-derived timeout policy into packet handling, and makes one timeout comparison overflow-aware. The evidence does not prove a concrete exploit, consensus failure, or direct asset impact, so this should not be treated as a confirmed security fix. It is still reasonable security hardening because it tightens validation at a network gossip ingestion boundary in validator core code.

## Security Evidence

1. Pull responses previously inserted each CRDS value without the shown explicit stale or future wallclock filter at that call site.
2. After the patch, CRDS values from pull responses are checked against msg_timeout before insertion.
3. The changed path processes peer-supplied gossip data in core validator networking code.
4. ClusterInfo now computes stake and epoch-derived timeout data and passes it into packet handling for gossip validation.
5. The push path changes wallclock plus timeout arithmetic to checked_add, avoiding unchecked overflow in a timeout guard.

## Missing Evidence

1. No advisory, CVE, exploit, or attack scenario is provided.
2. No proof that stale or future CRDS values caused consensus failure, fund loss, key compromise, or validator takeover.
3. No complete evidence showing how accepted stale ContactInfo values would be abused in practice.
4. No regression test details are supplied in the provided evidence.
5. No proof that the unchecked addition was exploitable before the patch.

## Claim Boundaries

1. Validate only as security hardening, not a concrete security fix.
2. Do not claim RCE, fund loss, key compromise, or proven consensus divergence.
3. Do not retain the original serialization-or-state-representation classification.
4. Do not infer access control or privilege-check changes from the supplied patch.
5. Security relevance is limited to peer gossip input validation and timeout arithmetic hardening.
