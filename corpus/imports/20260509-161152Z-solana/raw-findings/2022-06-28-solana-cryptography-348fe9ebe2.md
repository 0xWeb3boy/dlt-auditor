---
case_id: case_20220628_348fe9ebe2
project: solana
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: medium
date: 2022-06-28
source_refs:
  - git:348fe9ebe2656da5ce76998d29edcd2a2bf2d7bc
  - "ledger/src/shred.rs:707"
  - "core/src/shred_fetch_stage.rs:205"
  - "ledger/src/shred.rs:687"
  - "ledger/src/shred.rs:681"
bug_class: late-network-input-validation
impact_type:
  - resource-exhaustion
confidence: medium
tags:
  - validator
  - network-input
  - shred-validation
  - early-rejection
  - dos-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch moves basic shred discard checks into the fetch stage so malformed, stale, out-of-range, wrong-version, or out-of-bounds-index shreds are dropped earlier. The evidence supports a resource-saving validation change on network input, but it does not establish a concrete vulnerability, exploit path, consensus bypass, or demonstrated denial-of-service condition.

## Observed Patch Facts

1. In `ledger/src/shred.rs`, the patch replaces `return None;` with `return true;`.

2. In `core/src/shred_fetch_stage.rs`, the patch replaces `let slot = match get_shred_slot_index_type(packet, stats) {` with `if should_discard_shred(packet, root, shred_version, slot_bounds, stats) {`.

3. In `ledger/src/shred.rs`, the patch replaces `return None;` with `return true;`.

4. In `ledger/src/shred.rs`, the patch replaces `return None;` with `return true;`.

## Project Context

The changed code sits primarily in `ledger/src`, `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `ledger/src/slot_stats.rs`, `ledger/src/shredder.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/slot_stats.rs`, `ledger/src/shredder.rs`. The strongest project-level identifiers around this patch are `slot`, `stats`, `None`, and `shred`.

## Before/After Behavior

Before the change, fetch-stage packet discard logic parsed enough shred data to obtain a slot, checked slot bounds, checked shred version separately, and then continued to packet hashing and dedup for packets not discarded there. Other slot or parent verification was described by the commit body as occurring later in window-service after sig-verification and deserialization. After the change, fetch-stage logic calls a shared boolean discard predicate that rejects malformed shred bytes, index overruns, bad shred type, missing or invalid slot, wrong shred version, and per-type index bounds violations before packet hashing and dedup.

# Root Cause

Basic shred-header validation was performed later or split across the ingress pipeline, so some invalid packets could reach more expensive downstream work before being rejected. The supplied evidence supports late validation and wasted work, not state corruption or acceptance of invalid shreds into consensus state.

## Walkthrough

1. A packet enters fetch-stage discard logic in core/src/shred_fetch_stage.rs.

2. Before the patch, should_discard_packet used get_shred_slot_index_type for partial parsing, then separately checked slot bounds and shred version.

3. The patch introduces or expands should_discard_shred in ledger/src/shred.rs as an explicit boolean reject predicate.

4. The predicate rejects absent shred bytes, index field overrun, bad shred type, missing slot, slot at or below root, and slot outside accepted bounds.

5. It also rejects malformed index data, shred version mismatch, and index values outside data/code shred limits.

6. core/src/shred_fetch_stage.rs now calls should_discard_shred before packet hashing and insertion into the received-shreds dedup structure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| ledger/src/shred.rs | 666 | Defines `should_discard_shred`, the shared early shred validation predicate over packet layout, slot/root bounds, version, type, and index limits. |
| ledger/src/shred.rs | 681 | Rejects packets whose shred index field overruns the available shred bytes instead of returning an optional parsed tuple. |
| ledger/src/shred.rs | 687 | Rejects bad shred type and slots that are at/below root or outside fetch slot bounds. |
| ledger/src/shred.rs | 707 | Rejects malformed index, shred version mismatch, and index bounds violations by shred type. |
| core/src/shred_fetch_stage.rs | 197 | Calls `should_discard_shred` from fetch-stage packet discard logic before packet hashing/dedup and later pipeline processing. |

## Code Snippets

## Snippet 1

Context: `ledger/src/shred.rs:707` (changes a sensitive control or state-update path)

Before
```rust
None => {
            stats.index_bad_deserialize += 1;
            return None;
        }
    };
    if index >= MAX_DATA_SHREDS_PER_SLOT as u32 {
        stats.index_out_of_bounds += 1;
        return None;
```
After
```rust
None => {
            stats.index_bad_deserialize += 1;
            return true;
        }
    };
    if layout::get_version(shred) != Some(shred_version) {
        stats.shred_version_mismatch += 1;
        return true;
```

## Snippet 2

Context: `core/src/shred_fetch_stage.rs:205` (changes a sensitive control or state-update path)

Before
```rust
stats: &mut ShredFetchStats,
) -> bool {
    let slot = match get_shred_slot_index_type(packet, stats) {
        None => return true,
        Some((slot, _index, _shred_type)) => slot,
    };
    if !slot_bounds.contains(&slot) {
        stats.slot_out_of_range += 1;
```
After
```rust
stats: &mut ShredFetchStats,
) -> bool {
    if should_discard_shred(packet, root, shred_version, slot_bounds, stats) {
        return true;
    }
```

## Snippet 3

Context: `ledger/src/shred.rs:687` (changes a sensitive control or state-update path)

Before
```rust
Err(_) => {
            stats.bad_shred_type += 1;
            return None;
        }
    };
    let slot = match layout::get_slot(shred) {
        Some(slot) => slot,
        None => {
```
After
```rust
Err(_) => {
            stats.bad_shred_type += 1;
            return true;
        }
    };
    let slot = match layout::get_slot(shred) {
        Some(slot) => {
            if slot <= root || !slot_bounds.contains(&slot) {
```

## Snippet 4

Context: `ledger/src/shred.rs:681` (changes a sensitive control or state-update path)

Before
```rust
if OFFSET_OF_SHRED_INDEX + SIZE_OF_SHRED_INDEX > shred.len() {
        stats.index_overrun += 1;
        return None;
    }
    let shred_type = match layout::get_shred_type(shred) {
```
After
```rust
if OFFSET_OF_SHRED_INDEX + SIZE_OF_SHRED_INDEX > shred.len() {
        stats.index_overrun += 1;
        return true;
    }
    let shred_type = match layout::get_shred_type(shred) {
```

# Fix Pattern

Consolidate basic packet-header validation into an early fetch-stage discard predicate and return explicit reject decisions with stats counters for each failure mode.

## How It Was Fixed

The patch changed shred parsing and validation from an optional tuple helper into a shared discard predicate that validates layout, shred type, slot/root bounds, version, and index bounds. The fetch-stage packet filter now invokes that predicate before hashing and deduplication.

# Why It Matters

1. Reduces wasted validator work on malformed or locally irrelevant shred packets.

2. Moves rejection closer to network ingress.

3. Keeps discard reasons visible through ShredFetchStats counters.

4. Does not prove forged-shred acceptance, ledger corruption, memory unsafety, or consensus divergence.

# Evidence Notes

Grounded evidence comes from ledger/src/shred.rs should_discard_shred and core/src/shred_fetch_stage.rs should_discard_packet. The commit body states that slot and parent verification previously occurred later after sig-verify and deserialization work, but the supplied hunks concretely show slot, version, type, layout, and index checks. Parent verification is not visible in the provided code excerpts. No measurements, attack scenario, or demonstrated resource-exhaustion threshold are provided. Protocol security invariant: Incoming shreds with malformed layout or locally invalid header fields should be rejected early in the validator ingress path before downstream processing consumes additional resources. Verification notes: The patch does not prove forged shreds could pass signature verification or be accepted into consensus state. The provided evidence does not show a direct memory safety issue. The provided evidence does not demonstrate ledger corruption or replay divergence. The parent verification mentioned in the commit body is not visible in the supplied hunks, so only the shown slot/version/type/index checks are mapped concretely. Exploitability as a network DoS is plausible but not proven by workload measurements or an attack scenario in the patch evidence. Classified as unclear rather than likely security because the evidence establishes resource-saving hardening but not a concrete vulnerability. Downgraded from security corpus inclusion because exploitability as network DoS is plausible but unsupported by the supplied evidence. Rejected unsupported labels such as cryptography bug, state corruption, replay divergence, or consensus bypass. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `late-network-input-validation`
Final impact type: `resource-exhaustion`
Final confidence: `medium`
Final tags: `validator, network-input, shred-validation, early-rejection, dos-hardening`

The supplied evidence supports retaining this as security hardening, not as a concrete security fix. The patch moves rejection of malformed, stale, wrong-version, out-of-range, and out-of-bounds shred packets earlier in a network-facing validator pipeline before hashing, signature verification, and deserialization can consume resources. That is a clear tightening of exposed input handling, but the evidence does not prove state corruption, cryptographic failure, consensus bypass, or a demonstrated denial-of-service exploit.

## Security Evidence

1. Commit body explicitly says invalid shred slot/parent checks occurred after sig-verify and deserialization, wasting resources.
2. Fetch-stage packet discard now calls should_discard_shred before packet hashing and deduplication.
3. The new discard predicate rejects malformed layout, bad shred type, invalid slot/root bounds, wrong shred version, and invalid index bounds.
4. The changed path handles network-origin shred packets in validator ingress logic.

## Missing Evidence

1. No concrete exploit scenario or attacker workload is supplied.
2. No measurements show practical resource exhaustion or validator degradation.
3. Parent verification is mentioned in the commit body but not shown in the provided hunks.
4. No evidence shows invalid shreds were accepted into consensus or ledger state.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim state corruption, consensus divergence, cryptographic break, or signature bypass.
3. Security relevance is limited to earlier rejection of risky network input to reduce wasted validator work.
4. The original state-corruption and state-integrity metadata is too strong for the supplied evidence.
