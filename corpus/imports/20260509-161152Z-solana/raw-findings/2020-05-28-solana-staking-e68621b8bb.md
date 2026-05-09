---
case_id: case_20200528_e68621b8bb
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
confidence: medium
source_quality: high
date: 2020-05-28
source_refs:
  - git:e68621b8bbc5e68d8a99a065efa9bcfb8e399473
  - "core/src/serve_repair.rs:867"
  - "core/src/serve_repair.rs:533"
bug_class: denial-of-service
impact_type:
  - availability
tags:
  - blockchain-core
  - repair-service
  - ledger-repair
  - denial-of-service
  - corrupted-shred
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely denial-of-service fix in Solana's orphan repair handling. The functional change in `core/src/serve_repair.rs` makes `ServeRepair::run_orphan` break when `repair_response::repair_response_packet(...)` returns `None`. The added regression test covers corrupted oversized shred data in the orphan repair path. The evidence supports a repair-service DoS fix, but does not establish consensus impact, cryptographic failure, or the exact exhausted resource.

## Observed Patch Facts

1. In `core/src/serve_repair.rs`, the patch adds `#[test]`.

2. In `core/src/serve_repair.rs`, the patch adds `} else {`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `staking` area of the project. Historical context from `core/src/broadcast_stage.rs`, `core/src/banking_stage.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/broadcast_stage.rs`, `core/src/banking_stage.rs`. The strongest project-level identifiers around this patch are `Blockstore::destroy`, `solana_logger::setup`, `PacketsRecycler::default`, and `packet`.

## Before/After Behavior

Before the patch, if repair response packet construction returned `None`, no packet was pushed but the loop could continue into parent-slot traversal logic. After the patch, `None` immediately breaks the loop. A new test creates corrupted oversized shred data to exercise this failure path.

# Root Cause

The orphan repair loop did not treat failure to construct a repair response packet as terminal for the current traversal, so processing could continue after encountering invalid shred data.

## Walkthrough

1. `ServeRepair::run_orphan` walks blockstore metadata for a slot and its parents.

2. For each slot with received data, it calls `repair_response::repair_response_packet(...)`.

3. Before the fix, a `None` result skipped pushing a packet but did not immediately stop traversal.

4. The patch adds an `else { break; }` branch for the `None` case.

5. The new `run_orphan_corrupted_shred_size` test covers the corrupted oversized shred path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/serve_repair.rs | 511 | orphan repair request handling walks parent slots and builds repair response packets from blockstore metadata and shreds |
| core/src/serve_repair.rs | 533 | new failure guard breaks traversal when a repair response packet cannot be created |
| core/src/serve_repair.rs | 867 | regression test constructs corrupted oversized shred data for the orphan repair path |

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

Fail closed on repair response construction failure by terminating the current orphan traversal.

## How It Was Fixed

`core/src/serve_repair.rs` now breaks out of the orphan repair loop when packet construction fails, and adds a regression test for corrupted oversized shred data.

# Why It Matters

1. Repair handling serves ledger shred data from blockstore.

2. Malformed or oversized shred data is now handled as a bounded failure in this path.

3. The commit subject explicitly identifies this as a repair DoS fix.

4. No evidence shows consensus, forgery, or cryptographic verification impact.

# Evidence Notes

Primary evidence is the `else { break; }` added after failed packet construction in `core/src/serve_repair.rs`, the surrounding `run_orphan` traversal context, the new `run_orphan_corrupted_shred_size` test, and the commit subject `Fix repair dos (#10299)`. Related broadcast, banking, window service, RPC, and vote packet contexts do not establish additional impact. Protocol security invariant: The repair service should stop orphan repair traversal when it cannot construct a valid repair response packet from blockstore data, so malformed or oversized shred data is handled as a bounded failure instead of allowing continued response processing. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show a consensus violation or ledger forgery issue. The patch does not establish cryptographic verification failure. The exact resource exhausted by the DoS is not shown in the provided evidence. Related broadcast, banking, and vote packet contexts do not appear to be the fixed business-logic path. Supported: ledger repair subsystem, not staking. Supported: denial-of-service classification from commit subject and corrupted-shred repair test. Not supported: state corruption, consensus violation, ledger forgery, or cryptographic failure. Not shown: exact resource exhausted or full remote exploit path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `denial-of-service`
Final impact type: `availability`
Final tags: `blockchain-core, repair-service, ledger-repair, denial-of-service, corrupted-shred`

The evidence supports retaining this as a security-relevant repair-service hardening case, but the original metadata overstates and mislabels the issue. The patch changes orphan repair traversal to stop when repair response packet construction fails, and the added test targets corrupted oversized shred data. Combined with the commit subject naming a repair DoS, this is plausibly availability-focused security work. The evidence does not support staking, state corruption, consensus integrity, cryptographic, or database-impact claims, nor does it prove the precise exploitable DoS mechanism from code alone.

## Security Evidence

1. Commit subject is "Fix repair dos (#10299)".
2. Runtime behavior changes from ignoring a failed packet construction to breaking orphan traversal on None.
3. New regression test is named run_orphan_corrupted_shred_size and constructs corrupted oversized shred data.
4. Affected code is in ServeRepair::run_orphan, a ledger repair response path.

## Missing Evidence

1. No full remote exploit path is shown.
2. No exact exhausted resource or failure amplification mechanism is shown.
3. No evidence of consensus violation, ledger forgery, or state corruption is shown.
4. No evidence supports the finding's staking subsystem label.

## Claim Boundaries

1. Supported claim: repair-service handling of corrupted oversized shred data was made fail-closed.
2. Supported claim: availability/DoS relevance is likely based on commit subject and guard behavior.
3. Not supported: staking-specific issue.
4. Not supported: state-integrity or state-corruption impact.
5. Not supported: cryptographic, replay, or consensus-security failure.
