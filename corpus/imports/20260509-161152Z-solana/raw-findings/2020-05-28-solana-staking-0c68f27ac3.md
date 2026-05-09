---
case_id: case_20200528_0c68f27ac3
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
source_quality: high
date: 2020-05-28
source_refs:
  - git:0c68f27ac3c8d66935ed5f79dcf9fca1dc17883b
  - "core/src/serve_repair.rs:867"
  - "core/src/serve_repair.rs:533"
bug_class: denial-of-service
impact_type:
  - availability
  - resource-exhaustion
confidence: medium
tags:
  - blockchain-core
  - repair
  - denial-of-service
  - resource-exhaustion
  - bounded-work
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Commit 0c68f27ac3 changes `core/src/serve_repair.rs` in the orphan repair response path. The supported issue is a denial-of-service/resource-exhaustion risk where `ServeRepair::run_orphan` could keep walking parent slot metadata after packet construction failed, because no packet was pushed and the response-count limit did not advance.

## Observed Patch Facts

1. In `core/src/serve_repair.rs`, the patch adds `#[test]`.

2. In `core/src/serve_repair.rs`, the patch adds `} else {`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `staking` area of the project. Historical context from `core/src/broadcast_stage.rs`, `core/src/banking_stage.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/broadcast_stage.rs`, `core/src/banking_stage.rs`. The strongest project-level identifiers around this patch are `Blockstore::destroy`, `solana_logger::setup`, `PacketsRecycler::default`, and `packet`.

## Before/After Behavior

Before the patch, `run_orphan` attempted to build a repair response packet and pushed it only when `repair_response_packet` returned `Some(packet)`. If packet construction returned `None`, execution still reached the parent traversal condition, and `res.packets.len()` had not increased. After the patch, the `None` case explicitly breaks out of the loop, stopping orphan repair traversal on packet construction failure. A regression test named `run_orphan_corrupted_shred_size` was added for an oversized/corrupted shred scenario.

# Root Cause

The loop used successfully generated packets as its response bound but did not terminate when packet generation failed. A corrupted or oversized shred could cause `repair_response_packet` to return `None`, leaving the response count unchanged while allowing parent-slot traversal to continue.

## Walkthrough

1. `run_orphan` creates a `Packets` batch and walks blockstore metadata starting from the requested orphan slot.

2. For each slot with received data, it calls `repair_response::repair_response_packet` to build an outbound repair response.

3. Before the fix, successful packet construction pushed a packet, but failed construction had no terminating branch.

4. The loop then checked whether the slot had a parent and whether `res.packets.len()` was still within `max_responses`.

5. Because a failed construction did not increase `res.packets.len()`, the loop could keep walking parent slots without making response-count progress.

6. After the fix, `None` from `repair_response_packet` immediately breaks the loop.

7. The added test anchors the failure mode to corrupted oversized shred data in orphan repair handling.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/serve_repair.rs | 511 | orphan repair response loop walks blockstore slot metadata and constructs repair response packets |
| core/src/serve_repair.rs | 533 | new guard stops processing when packet construction fails |
| core/src/serve_repair.rs | 867 | regression test for corrupted oversized shred in orphan repair handling |

## Code Snippets

## Snippet 1

Context: `core/src/serve_repair.rs:867` (changes signature or replay validation logic)

Before
```rust
Blockstore::destroy(&ledger_path).expect("Expected successful database destruction");
    }
}
```
After
```rust
Blockstore::destroy(&ledger_path).expect("Expected successful database destruction");
    }

    #[test]
    fn run_orphan_corrupted_shred_size() {
        solana_logger::setup();
        let recycler = PacketsRecycler::default();
        let ledger_path = get_tmp_ledger_path!();
```

## Snippet 2

Context: `core/src/serve_repair.rs:533` (changes a sensitive control or state-update path)

Before
```rust
if let Some(packet) = packet {
                    res.packets.push(packet);
                }
                if meta.is_parent_set() && res.packets.len() <= max_responses {
```
After
```rust
if let Some(packet) = packet {
                    res.packets.push(packet);
                } else {
                    break;
                }
                if meta.is_parent_set() && res.packets.len() <= max_responses {
```

# Fix Pattern

Fail closed in bounded response-generation loops: if an outbound packet cannot be constructed, stop traversal instead of continuing with unchanged progress counters.

## How It Was Fixed

`ServeRepair::run_orphan` now handles `repair_response_packet(...) == None` with `else { break; }`, preventing the loop from reaching the parent-slot traversal branch after packet construction failure. The patch also adds a regression test for corrupted oversized shred handling.

# Why It Matters

1. Keeps orphan repair response work bounded by progress or termination.

2. Prevents corrupted oversized shred data from causing continued ancestor traversal with no response-count progress.

3. Supported impact is repair-path DoS/resource exhaustion, not consensus failure, fund loss, staking impact, or arbitrary state corruption.

# Evidence Notes

The strongest evidence is the added `else { break; }` after `if let Some(packet) = packet { res.packets.push(packet); }` in `core/src/serve_repair.rs`, plus the surrounding `run_orphan` loop over `blockstore.meta(slot)` and parent traversal guarded by `res.packets.len() <= max_responses`. The test name and changed comments support the corrupted oversized shred failure mode. Claims about staking, cryptographic logic, replay safety, fund loss, consensus failure, or arbitrary state corruption are not supported by the provided evidence. Protocol security invariant: Orphan repair response generation must stop when a repair response packet cannot be constructed, so corrupted or oversized stored shred data cannot make the repair path continue parent-slot traversal without response-count progress. Verification notes: Patch evidence does not prove remote exploitability by itself. Patch evidence does not show consensus safety or fund-loss impact. Patch evidence does not support classifying this as staking-related. Patch evidence does not prove arbitrary state corruption; it shows bounded-work failure handling in repair response generation. Used only the provided mapper, draft, commit metadata, and code excerpts. Did not verify remote exploitability; the evidence supports likely DoS risk in a repair service path. Kept the finding in the security corpus because the commit title names DoS and the code change fixes bounded-work failure handling. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `denial-of-service`
Final impact type: `availability, resource-exhaustion`
Final confidence: `medium`
Final tags: `blockchain-core, repair, denial-of-service, resource-exhaustion, bounded-work`

The supplied evidence supports a security-relevant repair-path hardening/fix for a denial-of-service style failure mode: packet construction failure now terminates parent traversal instead of continuing with no response-count progress, and the commit subject explicitly names repair DoS. However, the evidence does not prove remote exploitability, consensus impact, staking involvement, or state corruption, so the original metadata is too specific and too strong.

## Security Evidence

1. Commit subject is "Fix repair dos".
2. `ServeRepair::run_orphan` now breaks when `repair_response_packet` returns `None`.
3. Before the patch, failed packet construction did not increment `res.packets.len()` before the parent traversal condition.
4. Added regression test is named `run_orphan_corrupted_shred_size`, tying the change to corrupted oversized shred handling.

## Missing Evidence

1. No proof that an unauthenticated remote actor can create the corrupted oversized shred condition.
2. No evidence of consensus failure, fund loss, or arbitrary state corruption.
3. No evidence that the touched path is staking-specific.
4. No quantitative bound or exploit trace showing actual resource exhaustion.

## Claim Boundaries

1. Classify as repair-path DoS/bounded-work hardening, not staking state corruption.
2. Supported impact is availability/resource exhaustion only.
3. Keep remote exploitability as unproven from the supplied patch evidence.
4. Do not claim cryptographic, replay, consensus, or fund-safety impact.
