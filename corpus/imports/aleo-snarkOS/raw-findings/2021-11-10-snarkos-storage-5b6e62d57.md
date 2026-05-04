---
case_id: case_20211110_5b6e62d57
project: snarkos
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2021-11-10
source_refs:
  - git:5b6e62d574119f9792089e93051c1b46e0ba26b5
  - "src/network/ledger.rs:827"
  - "src/network/ledger.rs:856"
  - "src/network/ledger.rs:315"
bug_class: consensus-fork-choice
impact_type:
  - state-consistency
  - consensus-divergence
confidence: medium
tags:
  - blockchain-core
  - network-sync
  - ledger-reorg
  - fork-choice
  - chain-weight
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes snarkOS network ledger synchronization from a height-based fork switch rule to a weight-based rule. The evidence supports a consensus-relevant fork-choice fix, but does not establish a concrete exploit path or broader impact beyond incorrect reorg behavior.

## Observed Patch Facts

1. In `src/network/ledger.rs`, the patch replaces `// and the peer has a higher block height, proceed to switch to the fork.` with `// and the peer has a heavier chain, proceed to switch to the fork.`.

2. In `src/network/ledger.rs`, the patch replaces `info!("Found a longer fork, rolling ledger back to block {}", maximum_common_ancestor);` with `info!("Found a heavier fork, rolling ledger back to block {}", maximum_common_ancestor);`.

3. In `src/network/ledger.rs`, the patch replaces `///` with `pub fn calculate_weight_from_height(&self, block_height: u32) -> Result<u128> {`.

## Project Context

The changed code sits primarily in `src/network`, which anchors the finding in the `storage` area of the project. Historical context from `src/network/peers.rs`, `src/network/server.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/network/server.rs`, `src/network/peers.rs`. The strongest project-level identifiers around this patch are `fork`, `latest_block_height`, `maximum_common_ancestor`, and `ledger`.

## Before/After Behavior

Before the patch, `update_block_requests` could enter the rollback path when a peer fork had a higher maximum block height than the local latest height and satisfied the existing fork-range checks. After the patch, the code computes local canonical weight from the common ancestor, computes peer fork weight, and only rolls back when the peer fork weight exceeds the canonical weight, with the same range and ancestor constraints still present.

# Root Cause

The synchronization path used higher peer block height as the deciding condition for switching forks, even though the patched logic indicates the intended fork-choice criterion is aggregate difficulty-target weight from the common ancestor.

## Walkthrough

1. A node examines peer ledger states in `update_block_requests` and selects a candidate peer with a high reported block height and block locators.

2. The code checks locator hashes that already exist locally and updates the common ancestor where applicable.

3. Before the patch, the fork-switch condition required the peer height to exceed the local latest height, plus range and common-ancestor checks.

4. The patch adds `calculate_weight_from_height` to sum local header `difficulty_target()` values from the common ancestor to the local latest height.

5. The patched path computes canonical weight and peer fork weight before deciding whether to roll back.

6. Rollback now requires `maximum_weight > canon_weight` along with the existing fork-range and ancestor checks.

7. Comments and logs were updated from longer or higher-height language to heavier-chain language.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/network/ledger.rs | 827 | Fork-choice decision in `update_block_requests`; replaces peer higher-height criterion with peer heavier-chain criterion before rollback. |
| src/network/ledger.rs | 315 | Adds `calculate_weight_from_height` helper to compute canonical chain aggregate difficulty target over local block headers. |
| src/network/ledger.rs | 856 | Rollback path for switching to a peer fork after the heavier-chain condition and fork-range checks pass. |

## Code Snippets

## Snippet 1

Context: `src/network/ledger.rs:827` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
// If this ledger is within the fork range of the peer,
                // and the common ancestor is within the fork range,
                // and the peer has a higher block height, proceed to switch to the fork.
                let latest_block_height = self.latest_block_height();
                if maximum_block_height.saturating_sub(latest_block_height) > 0
                    && maximum_block_height.saturating_sub(latest_block_height) <= MAXIMUM_LINEAR_BLOCK_LOCATORS
                    && maximum_block_height.saturating_sub(maximum_common_ancestor) > 0
```
After
```rust
// If this ledger is within the fork range of the peer,
                // and the common ancestor is within the fork range,
                // and the peer has a heavier chain, proceed to switch to the fork.
                let latest_block_height = self.latest_block_height();
                let canon_weight = match self.calculate_weight_from_height(maximum_common_ancestor) {
                    Ok(weight) => weight,
                    Err(error) => {
                        error!("Failed to calculate canon chain weight: {}", error);
```

## Snippet 2

Context: `src/network/ledger.rs:856` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
&& latest_block_height.saturating_sub(maximum_common_ancestor) > 0
                {
                    info!("Found a longer fork, rolling ledger back to block {}", maximum_common_ancestor);

                    // Set the terminator bit to `true` to ensure it does not mine.
```
After
```rust
&& latest_block_height.saturating_sub(maximum_common_ancestor) > 0
                {
                    info!("Found a heavier fork, rolling ledger back to block {}", maximum_common_ancestor);

                    // Set the terminator bit to `true` to ensure it does not mine.
```

## Snippet 3

Context: `src/network/ledger.rs:315` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    ///
    /// Performs the given `request` to the ledger.
```
After
```rust
}

    pub fn calculate_weight_from_height(&self, block_height: u32) -> Result<u128> {
        Ok(self
            .get_block_headers(block_height, self.latest_block_height())?
            .iter()
            .fold(0u128, |acc, header| acc + header.difficulty_target() as u128))
    }
```

# Fix Pattern

Replace height-only fork-switch logic with aggregate chain-weight comparison from the common ancestor.

## How It Was Fixed

The patch adds a helper to calculate local canonical chain weight over block headers, handles errors by logging and returning, computes peer fork weight in the fork-choice path, and changes the rollback condition from peer height greater than local height to peer weight greater than canonical weight.

# Why It Matters

1. Prevents reorg decisions from relying only on peer-reported chain length.

2. Aligns synchronization behavior with a weight-based fork-choice invariant.

3. Affects consensus-relevant ledger rollback behavior.

4. Evidence does not support claims of key compromise, remote code execution, or unrelated data corruption.

# Evidence Notes

Grounded evidence is limited to `src/network/ledger.rs`: the fork-choice condition around line 827, the rollback log around line 856, and the new `calculate_weight_from_height` helper around line 315. The supplied evidence supports a fork-choice correctness and likely security fix. It does not prove how peer-supplied weights are validated, whether an attacker could practically exploit the old rule, or whether any funds or keys were directly at risk. The draft's claims about serialization, RPC boundaries, or canonical serialized state are unsupported and removed. Protocol security invariant: During peer ledger synchronization, a node should not roll back from its canonical chain to a peer fork solely because the peer reports a higher block height; the fork switch should compare aggregate chain weight from the common ancestor while preserving fork-range and common-ancestor checks. Verification notes: The patch does not prove that an attacker could cheaply construct or deliver a malicious fork. The patch does not show whether `difficulty_target` is independently validated elsewhere before this comparison. The patch does not prove remote code execution, data corruption outside ledger reorg behavior, or key compromise. The patch does not show test coverage or all peer-message validation surrounding `maximum_weight`. No external issue details or tests were provided. No evidence was provided for exploitability beyond incorrect fork-choice behavior. No evidence was provided for impacts outside ledger synchronization and reorg decisions. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-fork-choice`
Final impact type: `state-consistency, consensus-divergence`
Final confidence: `medium`
Final tags: `blockchain-core, network-sync, ledger-reorg, fork-choice, chain-weight, consensus`

The supplied patch evidence supports a security-sensitive hardening classification: fork switching during network ledger synchronization changed from accepting a higher-height peer fork to requiring a heavier aggregate-difficulty fork. That is consensus-relevant and removes a risky reorg condition, but the evidence does not prove a concrete exploit, attacker cost, validation model, or realized impact, so security-fix is too strong. The original storage/serialization framing is unsupported by the patch.

## Security Evidence

1. Fork-choice logic in src/network/ledger.rs changed from higher block height to heavier chain weight before rollback.
2. The rollback log changed from "longer fork" to "heavier fork", confirming the intended behavior shift.
3. A new helper calculates canonical chain weight from local block headers using difficulty_target().
4. The affected path processes peer ledger state and can trigger local ledger rollback, making it consensus-sensitive.

## Missing Evidence

1. No issue text or tests showing an exploitable attack scenario were provided.
2. No evidence shows whether peer-supplied fork weights or difficulty targets are independently validated.
3. No proof of funds loss, key compromise, remote code execution, or broader data corruption is present.
4. No evidence establishes that the old height-based rule was practically exploitable rather than protocol-correctness hardening.

## Claim Boundaries

1. Keep the finding scoped to network ledger synchronization and fork-choice/reorg behavior.
2. Do not describe this as a storage, serialization, RPC, or canonical encoding vulnerability.
3. Do not claim concrete exploitation or financial impact from the supplied patch alone.
4. Classify as security-hardening, not a confirmed security-fix.
