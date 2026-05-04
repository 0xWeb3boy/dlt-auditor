---
case_id: case_20240628_2ecf14d5d8
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2024-06-28
source_refs:
  - git:2ecf14d5d88f9bc4da73740eb8553af432bf9363
  - "stackslib/src/chainstate/burn/db/sortdb.rs:1817"
  - "stackslib/src/chainstate/burn/db/sortdb.rs:1073"
bug_class: canonical-tip-monotonicity
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - consensus
  - nakamoto
  - sortition-db
  - canonical-tip
  - state-integrity
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Nakamoto canonical tip handling in the sortition DB so an accepted block only advances the memoized canonical tip when it is higher than the current tip for the same sortition history. This is plausibly important consensus state maintenance, but the provided evidence does not establish an exploitable vulnerability or concrete security impact.

## Observed Patch Facts

1. In `stackslib/src/chainstate/burn/db/sortdb.rs`, the patch replaces `self.update_canonical_stacks_tip(` with `// arbitrarily.`.

2. In `stackslib/src/chainstate/burn/db/sortdb.rs`, the patch replaces `/// is the given block a descendant of 'potential_ancestor'?` with `/// Get the block ID of the highest-processed Nakamoto block on this history.`.

## Project Context

The changed code sits primarily in `stackslib/src/chainstate/burn/db`, `stackslib/src/chainstate/burn`, which anchors the finding in the `consensus` area of the project. Historical context from `stackslib/src/chainstate/burn/operations/leader_block_commit.rs`, `stackslib/src/chainstate/burn/db/processing.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stackslib/src/chainstate/burn/sortition.rs`, `stackslib/src/chainstate/burn/operations/leader_block_commit.rs`. The strongest project-level identifiers around this patch are `block`, `StacksEpochId::Epoch30`, `Nakamoto`, and `processed`. Nearby tests or test-like files include `stackslib/src/chainstate/burn/operations/test/serialization.rs`, `stackslib/src/chainstate/burn/operations/test/mod.rs`.

## Before/After Behavior

Before the patch, the Epoch30/Nakamoto branch in set_stacks_block_accepted_at_tip directly updated the canonical Stacks tip for an accepted block. After the patch, the code first queries stacks_chain_tips for the current highest tip for burn_tip.sortition_id and uses that current state to gate canonical tip advancement. The added get_nakamoto_tip_block_id helper derives a StacksBlockId from get_nakamoto_tip and appears to be support code.

# Root Cause

The code relied on the general assumption that Nakamoto blocks are processed in order and therefore treated each accepted Nakamoto block as eligible to update the canonical tip. The patch comments identify exceptions involving same-height malleableized siblings and late tenure-change processing, where that assumption can be too broad.

## Walkthrough

1. set_stacks_block_accepted_at_tip receives an accepted Stacks block and resolves its burn-chain snapshot and epoch.

2. For Epoch30 or later, the function enters Nakamoto-specific canonical tip handling.

3. Before the fix, this path called update_canonical_stacks_tip without first comparing against the existing memoized tip for the sortition.

4. The patch documents cases where Nakamoto processing may see same-height siblings or late tenure-change processing.

5. The fixed path queries stacks_chain_tips for the highest existing block_height for the same sortition_id.

6. Canonical Nakamoto tip advancement is then intended to occur only when the incoming block is higher than the existing tip.

7. get_nakamoto_tip_block_id is added as a convenience helper and is not itself shown to be the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stackslib/src/chainstate/burn/db/sortdb.rs | 1799 | Updates accepted Stacks block state at a burn tip and branches into Nakamoto-specific canonical tip handling. |
| stackslib/src/chainstate/burn/db/sortdb.rs | 1817 | Adds current-tip lookup from stacks_chain_tips so canonical Nakamoto tip advancement can be gated by block height. |
| stackslib/src/chainstate/burn/db/sortdb.rs | 1073 | Adds SortitionHandle helper to return the highest processed Nakamoto tip as a StacksBlockId. |

## Code Snippets

## Snippet 1

Context: `stackslib/src/chainstate/burn/db/sortdb.rs:1817` (changes bounds, limits, or capacity handling)

Before
```rust
if cur_epoch.epoch_id >= StacksEpochId::Epoch30 {
            // Nakamoto blocks are always processed in order since the chain can't fork
            self.update_canonical_stacks_tip(
                &burn_tip.sortition_id,
```
After
```rust
if cur_epoch.epoch_id >= StacksEpochId::Epoch30 {
            // Nakamoto blocks are always processed in order since the chain can't fork
            // arbitrarily.
            // However, two kinds of forks can happen:
            // * one of a set of malleableized siblings can be confirmed (but they all have the
            // same sighash and same height).
            // * a late tenure-change can be processed.
            // As a result, only update the canonical Nakamoto tip if the given block is higher
```

## Snippet 2

Context: `stackslib/src/chainstate/burn/db/sortdb.rs:1073` (changes a sensitive control or state-update path)

Before
```rust
fn get_nakamoto_tip(&self) -> Result<Option<(ConsensusHash, BlockHeaderHash, u64)>, db_error>;

    /// is the given block a descendant of `potential_ancestor`?
    ///  * block_at_burn_height: the burn height of the sortition that chose the stacks block to check
```
After
```rust
fn get_nakamoto_tip(&self) -> Result<Option<(ConsensusHash, BlockHeaderHash, u64)>, db_error>;

    /// Get the block ID of the highest-processed Nakamoto block on this history.
    fn get_nakamoto_tip_block_id(&self) -> Result<Option<StacksBlockId>, db_error> {
        let Some((ch, bhh, _)) = self.get_nakamoto_tip()? else {
            return Ok(None);
        };
        Ok(Some(StacksBlockId::new(&ch, &bhh)))
```

# Fix Pattern

Before mutating canonical consensus state, read the current persisted tip for the same history and enforce a monotonic height check instead of relying only on expected processing order.

## How It Was Fixed

The fix adds a current-tip lookup in stackslib/src/chainstate/burn/db/sortdb.rs within the Epoch30/Nakamoto branch. It selects consensus_hash, block_hash, and block_height from stacks_chain_tips for the active sortition_id ordered by block_height descending, then uses the result to avoid advancing the canonical Nakamoto tip with a non-higher block. It also adds SortitionHandle::get_nakamoto_tip_block_id as helper support code.

# Why It Matters

1. Touches canonical tip state in the sortition DB.

2. Prevents non-higher Nakamoto blocks from replacing a memoized tip.

3. Accounts for documented same-height and late-processing cases.

4. Security impact is plausible but not proven by the supplied evidence.

# Evidence Notes

The strongest evidence is the changed Epoch30/Nakamoto branch in stackslib/src/chainstate/burn/db/sortdb.rs and the new query against stacks_chain_tips. The commit subject and comments support a canonical-tip correctness fix. The evidence does not show attacker control, exploitability, denial of service, fund loss, chain split, or another concrete security consequence, so the security classification should remain unclear rather than confirmed or likely. Protocol security invariant: For Epoch30/Nakamoto processing, the sortition DB canonical Nakamoto tip for a sortition history should not be overwritten by a non-higher processed block; advancement should be gated by Stacks block height. Verification notes: The patch does not show a concrete attacker-controlled input path. The patch does not prove chain split, fund loss, or denial-of-service consequences by itself. The helper method addition alone is not security-relevant. The evidence supports a consensus state integrity fix, not a serialization or resource exhaustion vulnerability. No commands or external inspection were used. Classification is based only on the provided diff excerpts and mapper/drafter text. Helper method addition was treated as support code, not the vulnerability root cause. Excluded from the security corpus because the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `canonical-tip-monotonicity`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `consensus, nakamoto, sortition-db, canonical-tip, state-integrity, security-hardening`

The evidence supports retaining this as security hardening, not as a confirmed exploit fix. The patch changes Nakamoto consensus state handling so the canonical tip is only advanced when the accepted block is higher than the memoized tip, and the comments identify real exceptional fork/late-processing cases that violate the prior assumption. The supplied evidence does not prove attacker control or a concrete exploit outcome, so it should not be labeled a security-fix.

## Security Evidence

1. Patch touches Nakamoto canonical tip handling in the sortition DB, a consensus-sensitive state path.
2. Before the patch, accepted Nakamoto blocks directly updated the canonical Stacks tip under the Epoch30 branch.
3. After the patch, the code queries the current highest tip for the same sortition_id before allowing canonical tip advancement.
4. Patch comments identify same-height malleableized siblings and late tenure-change processing as cases where the old processing-order assumption can fail.
5. The commit subject explicitly says the canonical Nakamoto fork should only advance if actually higher than the memoized fork.

## Missing Evidence

1. No evidence of attacker-controlled input or adversarial trigger path is provided.
2. No demonstrated chain split, invalid acceptance, denial of service, fund loss, or consensus safety failure is shown.
3. No tests, vulnerability report, or exploit scenario are included in the supplied evidence.
4. The helper get_nakamoto_tip_block_id addition is support code and does not independently prove security relevance.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim a proven exploitable vulnerability from the patch alone.
3. Do not claim concrete financial loss, DoS, or chain split impact.
4. The supported claim is limited to hardening consensus state integrity by enforcing monotonic canonical Nakamoto tip advancement.
