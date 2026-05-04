---
case_id: case_20260417_f7826d1c1b
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2026-04-17
source_refs:
  - git:f7826d1c1b58cdfeabbf44bc7b671a7b14ea3039
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:809"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:798"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:1575"
  - "crates/fuel-core/src/service/adapters/consensus_module/poa.rs:829"
bug_class: consensus-liveness
impact_type:
  - consensus-liveness-failure
  - availability
confidence: medium
tags:
  - blockchain-core
  - consensus
  - poa
  - quorum
  - liveness
  - redis
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a Redis-backed PoA reconciliation livelock where the same block stored on multiple Redis nodes with different epoch metadata was counted as separate vote groups. The fix changes vote grouping from `(epoch, BlockId)` to `BlockId` and tracks the maximum epoch only as tie-breaker metadata. Evidence supports a consensus-liveness issue in this reconciliation path, but not attacker triggerability, invalid block acceptance, authorization bypass, cryptographic failure, theft, or RCE.

## Observed Patch Facts

1. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `HashMap::<(u64, BlockId), (usize, SealedBlock)>::new(),` with `HashMap::<BlockId, (u64, usize, SealedBlock)>::new(),`.

2. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `let votes = blocks_by_node` with `// Group votes by block_id only (not epoch). The same block can`.

3. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `#[tokio::test(flavor = "multi_thread")]` with `/// Reproduces the devnet deadlock from April 17, 2026.`.

4. In `crates/fuel-core/src/service/adapters/consensus_module/poa.rs`, the patch replaces `.max_by_key(|((epoch, _), _)| *epoch)` with `.max_by_key(|(_, (max_epoch, _, _))| *max_epoch)`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src/service/adapters/consensus_module`, `crates/fuel-core/src/service/adapters`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/fuel-core/src/service/adapters/block_importer.rs`, `crates/fuel-core/src/service/adapters/sync.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/fuel-core/src/service/adapters/sync.rs`, `crates/fuel-core/src/service/adapters/producer.rs`. The strongest project-level identifiers around this patch are `block`, `count`, `epoch`, and `votes`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the change, reconciliation grouped votes using `HashMap::<(u64, BlockId), (usize, SealedBlock)>` and `vote_key = (*epoch, block.entity.id())`, so identical blocks with different epoch stamps could be split below quorum. Winner selection used the highest epoch group and returned only that group's count, which could lead to repair attempts that failed because all nodes already had an entry at the height. After the change, reconciliation groups by `BlockId`, increments a shared count for matching block IDs, tracks `max_epoch` within the grouped value, and selects the winner using that tracked max epoch while returning the grouped count.

# Root Cause

The reconciliation logic treated epoch metadata as part of vote identity. During re-promotion storms, identical block IDs could appear with different epochs, causing votes for the same sealed block to fragment across groups and making a quorum-present state appear below quorum.

## Walkthrough

1. Redis-backed PoA reconciliation reads candidate blocks for a height from multiple Redis nodes.

2. The old accumulator keyed votes by `(epoch, BlockId)`.

3. The provided commit and test describe a re-promotion storm where the same block ID was present on different nodes with different epoch metadata.

4. Those entries were counted as separate vote groups even though they represented the same sealed block.

5. Winner selection chose the highest-epoch group, but that group's count could remain below quorum.

6. Repair then attempted to write the selected block, but nodes already had an entry at that height and returned `HEIGHT_EXISTS`, so repair did not reach quorum.

7. The patch changes the vote key to `BlockId` so identical blocks count together regardless of epoch metadata.

8. The code keeps the maximum epoch per block ID and uses it only when choosing among grouped candidates.

9. The added regression test documents the unresolved backlog scenario and verifies that same-block different-epoch entries now reconcile without repair.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 798 | documents reconciliation invariant: group identical block_ids across differing epochs and use max epoch only for real forks |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 809 | changes vote accumulator key from `(epoch, BlockId)` to `BlockId` and tracks max epoch per block |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 829 | selects reconciliation winner by max epoch associated with each block_id group while returning the grouped quorum count |
| crates/fuel-core/src/service/adapters/consensus_module/poa.rs | 1575 | regression test for same block written with different epochs causing unresolved backlog before the fix |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:809` (changes a consensus- or validator-sensitive branch)

Before
```rust
.flat_map(|blocks_by_epoch| blocks_by_epoch.iter())
                .fold(
                    HashMap::<(u64, BlockId), (usize, SealedBlock)>::new(),
                    |mut votes, (epoch, block)| {
                        let vote_key = (*epoch, block.entity.id());
                        match votes.get_mut(&vote_key) {
                            Some((count, _)) => {
                                *count = count.saturating_add(1);
```
After
```rust
.flat_map(|blocks_by_epoch| blocks_by_epoch.iter())
                .fold(
                    HashMap::<BlockId, (u64, usize, SealedBlock)>::new(),
                    |mut votes, (epoch, block)| {
                        let vote_key = block.entity.id();
                        match votes.get_mut(&vote_key) {
                            Some((max_epoch, count, _)) => {
                                *count = count.saturating_add(1);
```

## Snippet 2

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:798` (changes a sensitive control or state-update path)

Before
```rust
}

            let votes = blocks_by_node
                .iter()
```
After
```rust
}

            // Group votes by block_id only (not epoch). The same block can
            // be written to different nodes with different epochs during
            // re-promotion storms — but if the block_id matches, it's the
            // same block and all copies count toward quorum. We track the
            // max epoch per block_id as the tiebreaker for fork resolution
            // when block_ids genuinely differ.
```

## Snippet 3

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:1575` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    #[tokio::test(flavor = "multi_thread")]
    async fn leader_state__when_same_height_entry_exists_on_less_than_quorum_nodes_then_repairs_it()
```
After
```rust
}

    /// Reproduces the devnet deadlock from April 17, 2026.
    ///
    /// The same block was written to all 3 nodes during re-promotion storms,
    /// so each node has the same block_id but with different epoch metadata.
    /// The old `(epoch, block_id)` vote grouping fragmented these into
    /// separate vote groups, with the max-epoch group having a count below
```

## Snippet 4

Context: `crates/fuel-core/src/service/adapters/consensus_module/poa.rs:829` (changes a consensus- or validator-sensitive branch)

Before
```rust
let winner = votes
                .into_iter()
                .max_by_key(|((epoch, _), _)| *epoch)
                .map(|(_, (count, block))| (count, block));

            if let Some((count, block)) = winner {
```
After
```rust
let winner = votes
                .into_iter()
                .max_by_key(|(_, (max_epoch, _, _))| *max_epoch)
                .map(|(_, (_, count, block))| (count, block));

            if let Some((count, block)) = winner {
```

# Fix Pattern

Canonicalize reconciliation vote identity around the consensus object being voted on, while retaining mutable metadata only for tie-breaking.

## How It Was Fixed

`RedisLeaderLeaseAdapter` now builds `HashMap::<BlockId, (u64, usize, SealedBlock)>` instead of `HashMap::<(u64, BlockId), (usize, SealedBlock)>`. Existing entries increment the shared count and update `max_epoch` when a higher epoch is observed. Winner selection now reads the stored `max_epoch` for each block ID group and returns the grouped count and block. A regression test was added for same-block different-epoch reconciliation.

# Why It Matters

1. Prevents a documented PoA reconciliation livelock.

2. Preserves quorum counting for identical sealed blocks across Redis nodes.

3. Avoids repair attempts that cannot progress when every node already has a same-height entry.

4. Security impact is limited to consensus liveness based on the provided evidence.

# Evidence Notes

Primary evidence is in `crates/fuel-core/src/service/adapters/consensus_module/poa.rs` around the vote accumulator, winner selection, explanatory comment, and regression test. The evidence directly supports the same-block vote fragmentation and livelock thesis. The evidence does not establish adversarial triggerability or any safety violation beyond liveness. Protocol security invariant: Redis-backed PoA reconciliation should count votes for quorum by sealed block identity at a height. Epoch metadata may be used to choose among genuinely different block IDs, but identical block IDs across Redis nodes should not be split into separate quorum groups because their epoch stamps differ. Verification notes: The patch does not prove an attacker can trigger re-promotion storms or control epoch metadata. The patch does not show invalid block acceptance or chain safety violation. The patch does not modify cryptographic verification, signatures, or authorization checks. The evidence supports a liveness/deadlock failure, not theft, data corruption, or remote code execution. The fix is specific to Redis-backed PoA reconciliation behavior, not all consensus paths. No independent file inspection or command execution was performed. Assessment relies only on the provided commit message, code snippets, mapper output, and draft. Confidence is downgraded from high to medium because the security classification depends on treating the documented liveness deadlock as a protocol security issue, while exploitability is not shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-liveness`
Final impact type: `consensus-liveness-failure, availability`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, poa, quorum, liveness, redis`

The supplied evidence supports a real Redis-backed PoA reconciliation livelock in consensus-adjacent quorum handling: identical blocks with different epoch metadata were counted as separate vote groups, preventing quorum recognition and causing repair failure. This is best retained as security-hardening for a consensus liveness condition, not as a concrete security-fix, because the patch does not show attacker triggerability, invalid block acceptance, consensus safety violation, signature failure, or authorization bypass.

## Security Evidence

1. Patch changes vote identity from `(epoch, BlockId)` to `BlockId`, preventing identical sealed blocks from being split across vote groups.
2. Winner selection still uses maximum epoch as tie-breaker while returning the grouped block count, preserving fork-selection behavior for differing block IDs.
3. Commit and regression test describe a permanent reconciliation livelock where repair cannot reach quorum because every Redis node already has an entry at the height.
4. Changed code is in PoA consensus module reconciliation logic and affects quorum recognition.

## Missing Evidence

1. No evidence that an external attacker can trigger re-promotion storms or manipulate epoch metadata.
2. No evidence of invalid block acceptance, chain fork finalization, theft, cryptographic failure, or authorization bypass.
3. No evidence that the bug affected mainnet or adversarial production conditions beyond the described devnet incident.

## Claim Boundaries

1. Classify as consensus liveness hardening, not consensus safety.
2. Do not retain misleading tags such as `p2p`, `signature`, or generic `database` for the final corpus entry.
3. Do not claim exploitability or attacker control from the supplied patch alone.
4. Scope is Redis-backed PoA reconciliation, not all consensus paths.
