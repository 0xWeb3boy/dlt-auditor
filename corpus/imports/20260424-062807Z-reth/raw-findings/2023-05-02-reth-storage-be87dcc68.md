---
case_id: case_20230502_be87dcc68
project: reth
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
impact_type:
  - state-integrity
source_quality: high
date: 2023-05-02
source_refs:
  - git:be87dcc68221eecc19be814297806a25c859192b
  - "crates/stages/src/stages/merkle.rs:169"
  - "crates/stages/src/stages/merkle.rs:199"
  - "crates/stages/src/stages/merkle.rs:183"
  - "crates/trie/src/progress.rs:28"
bug_class: checkpoint-target-mismatch
confidence: medium
tags:
  - blockchain-core
  - storage
  - merkle-trie
  - checkpoint-validation
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is a concrete correctness fix for Merkle rebuild checkpoint handling. The provided diff supports that older code could resume from any stored checkpoint, save partial progress without an explicit target at the save site, and leave stale checkpoint metadata around during a rebuild. The evidence does not establish an exploitable vulnerability, remote triggerability, or consensus failure, so this should remain classified as unclear rather than a confirmed security fix.

## Observed Patch Facts

1. In `crates/stages/src/stages/merkle.rs`, the patch replaces `if let Some(checkpoint) = &checkpoint {` with `if let Some(checkpoint) = checkpoint.as_ref().filter(|c| c.target_block == to_block) {`.

2. In `crates/stages/src/stages/merkle.rs`, the patch replaces `self.save_execution_checkpoint(tx, Some((*state).into()))?;` with `let checkpoint = MerkleCheckpoint::new(`.

3. In `crates/stages/src/stages/merkle.rs`, the patch replaces `tx.clear::<tables::StoragesTrie>()?;` with `previous_checkpoint = ?checkpoint,`.

4. In `crates/trie/src/progress.rs`, the patch replaces `impl From<IntermediateStateRootState> for MerkleCheckpoint {` with `impl From<MerkleCheckpoint> for IntermediateStateRootState {`.

## Project Context

The changed code sits primarily in `crates/stages/src/stages`, `crates/stages/src`, `crates/trie/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/stages/src/stages/headers.rs`, `crates/stages/src/stages/hashing_storage.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/stages/src/stages/headers.rs`, `crates/stages/src/stages/hashing_storage.rs`. The strongest project-level identifiers around this patch are `checkpoint`, `state`, `StoredSubNode::from`, and `value`.

## Before/After Behavior

Before the patch, the long-rebuild path reused any existing checkpoint (`if let Some(checkpoint) = &checkpoint`), saved partial progress through a generic conversion, and cleared trie tables without first resetting persisted checkpoint state. After the patch, resume only happens when `checkpoint.target_block == to_block`, stale checkpoint state is explicitly cleared before rebuilding from scratch, and partial progress is saved through `MerkleCheckpoint::new(to_block, ...)` so the checkpoint is tied to the rebuild target.

# Root Cause

Persisted Merkle rebuild progress was not strictly bound to the current rebuild target at the resume/save boundary, and stale checkpoint metadata was not explicitly invalidated before a fresh rebuild.

## Walkthrough

1. `MerkleStage::execute` loads the current block range and any saved execution checkpoint before entering the long rebuild path.

2. In the pre-fix code, the rebuild path resumed whenever a checkpoint existed, with no shown check that the checkpoint belonged to the current `to_block`.

3. When partial progress was produced, the pre-fix code saved `(*state).into()` as a checkpoint, while the supporting conversion in `crates/trie/src/progress.rs` shows only state-field copying and does not itself demonstrate target validation at that call site.

4. The patched code changes the resume condition to `checkpoint.as_ref().filter(|c| c.target_block == to_block)`, so only a checkpoint for the current target is reused.

5. If the checkpoint does not match, the patched path logs the previous checkpoint, clears the saved execution checkpoint, and then clears trie tables for a fresh rebuild.

6. For partial progress, the patched code now constructs `MerkleCheckpoint::new(to_block, ...)` before saving, making the saved checkpoint explicitly target-aware.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/stages/src/stages/merkle.rs | 169 | resume guard for Merkle rebuild checkpoints; only continue when checkpoint target matches current `to_block` |
| crates/stages/src/stages/merkle.rs | 183 | stale-checkpoint invalidation before clearing trie tables for a fresh rebuild |
| crates/stages/src/stages/merkle.rs | 199 | partial-progress persistence; constructs and saves a checkpoint with explicit target block metadata |
| crates/trie/src/progress.rs | 28 | progress/checkpoint conversion boundary adjusted so persisted checkpoints are created with explicit target context |

## Code Snippets

## Snippet 1

Context: `crates/stages/src/stages/merkle.rs:169` (changes a consensus- or validator-sensitive branch)

Before
```rust
} else if to_block - from_block > threshold || from_block == 1 {
            // if there are more blocks than threshold it is faster to rebuild the trie
            if let Some(checkpoint) = &checkpoint {
                debug!(
                    target: "sync::stages::merkle::exec",
```
After
```rust
} else if to_block - from_block > threshold || from_block == 1 {
            // if there are more blocks than threshold it is faster to rebuild the trie
            if let Some(checkpoint) = checkpoint.as_ref().filter(|c| c.target_block == to_block) {
                debug!(
                    target: "sync::stages::merkle::exec",
```

## Snippet 2

Context: `crates/stages/src/stages/merkle.rs:199` (changes a consensus- or validator-sensitive branch)

Before
```rust
StateRootProgress::Progress(state, updates) => {
                    updates.flush(tx.deref_mut())?;
                    self.save_execution_checkpoint(tx, Some((*state).into()))?;
                    return Ok(ExecOutput { stage_progress: input.stage_progress(), done: false })
                }
```
After
```rust
StateRootProgress::Progress(state, updates) => {
                    updates.flush(tx.deref_mut())?;
                    let checkpoint = MerkleCheckpoint::new(
                        to_block,
                        state.last_account_key,
                        state.last_walker_key.hex_data,
                        state.walker_stack.into_iter().map(StoredSubNode::from).collect(),
                        state.hash_builder.into(),
```

## Snippet 3

Context: `crates/stages/src/stages/merkle.rs:183` (changes a consensus- or validator-sensitive branch)

Before
```rust
current = ?current_block,
                    target = ?to_block,
                    "Rebuilding trie"
                );
                tx.clear::<tables::AccountsTrie>()?;
                tx.clear::<tables::StoragesTrie>()?;
```
After
```rust
current = ?current_block,
                    target = ?to_block,
                    previous_checkpoint = ?checkpoint,
                    "Rebuilding trie"
                );
                // Reset the checkpoint and clear trie tables
                self.save_execution_checkpoint(tx, None)?;
                tx.clear::<tables::AccountsTrie>()?;
```

## Snippet 4

Context: `crates/trie/src/progress.rs:28` (changes persisted or aggregate state handling)

Before
```rust
}

impl From<IntermediateStateRootState> for MerkleCheckpoint {
    fn from(value: IntermediateStateRootState) -> Self {
        Self {
            last_account_key: value.last_account_key,
            last_walker_key: value.last_walker_key.hex_data,
            walker_stack: value.walker_stack.into_iter().map(StoredSubNode::from).collect(),
```
After
```rust
}

impl From<MerkleCheckpoint> for IntermediateStateRootState {
    fn from(value: MerkleCheckpoint) -> Self {
```

# Fix Pattern

Validate persisted resume state against the current execution target, invalidate stale checkpoint metadata before restarting, and persist future checkpoints with explicit target context.

## How It Was Fixed

The fix adds a target-block equality check before reusing a checkpoint, resets stored checkpoint state when a fresh rebuild is required, and replaces the generic progress-to-checkpoint save path with explicit construction of a `MerkleCheckpoint` that includes `to_block`.

# Why It Matters

1. It prevents reuse of persisted rebuild progress that may belong to a different target block.

2. It keeps checkpoint metadata aligned with the trie contents being rebuilt.

3. It reduces the risk of inconsistent local resume behavior in a critical state-reconstruction path.

4. The patch evidence supports a correctness and integrity improvement, not a proven security exploit.

# Evidence Notes

Grounded evidence comes from `crates/stages/src/stages/merkle.rs`: the resume guard changed from accepting any checkpoint to accepting only one whose `target_block` matches `to_block`; the rebuild path now clears the saved checkpoint before clearing trie tables; and partial progress is now saved via `MerkleCheckpoint::new(to_block, ...)` instead of direct `(*state).into()`. Supporting evidence from `crates/trie/src/progress.rs` shows the earlier generic conversion boundary for progress state. The supplied material supports a checkpoint-target mismatch/correctness thesis, but does not prove invalid chain acceptance, attacker control, or a security boundary breach. Protocol security invariant: If the Merkle stage resumes a multi-step trie rebuild from persisted progress, that checkpoint must correspond to the same `to_block` as the rebuild currently being executed; otherwise persisted progress and the rebuild target can diverge. Verification notes: The patch does not prove a remotely triggerable exploit path. The patch does not by itself show that invalid blocks were accepted on chain. The evidence supports local trie/state-root reconstruction inconsistency, not confidentiality or privilege impact. It is not proven whether pre-fix behavior always produced wrong roots versus only wasted work or failed resumes. No test diff or reproduction is provided in the supplied evidence. The evidence is sufficient to support a correctness fix in checkpoint handling. The security impact remains unproven from the patch alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `checkpoint-target-mismatch`
Final confidence: `medium`
Final tags: `blockchain-core, storage, merkle-trie, checkpoint-validation, state-integrity`

The patch does not prove a concrete exploitable vulnerability, but it does clearly harden a security-sensitive state-integrity path. The Merkle rebuild logic now refuses to resume from a checkpoint unless it matches the current `to_block`, explicitly clears stale checkpoint metadata before rebuilding trie tables, and persists future checkpoints with explicit target context. In a blockchain client, authenticated trie/state-root reconstruction is security-relevant enough to retain this as security-hardening, while avoiding stronger claims about exploitability or confirmed consensus failure.

## Security Evidence

1. Resume logic changed from accepting any saved checkpoint to accepting only one whose `target_block == to_block`.
2. Fresh rebuild path now clears the persisted execution checkpoint before clearing trie tables, removing stale checkpoint/trie combinations.
3. Partial progress is now saved via `MerkleCheckpoint::new(to_block, ...)`, explicitly binding persisted progress to the rebuild target.
4. The affected code is Merkle/state-root reconstruction for an authenticated trie, which is an integrity-sensitive validation/storage path.

## Missing Evidence

1. No proof that a remote peer or attacker could intentionally trigger the stale-checkpoint condition.
2. No test, incident report, or reproduction showing invalid state roots, bad block acceptance, or consensus divergence before the fix.
3. No evidence that the pre-fix behavior led to more than incorrect resume behavior, wasted work, or local rebuild inconsistency.
4. No confidentiality, privilege, or code-execution impact is shown by the supplied patch.

## Claim Boundaries

1. Supported: the change hardens checkpoint validation and stale-state handling in Merkle trie rebuilds.
2. Supported: the security relevance is integrity-oriented and tied to a sensitive blockchain state path.
3. Not supported: a confirmed exploitable vulnerability or attacker-controlled consensus break.
4. Not supported: broad 'state corruption' claims beyond mismatched checkpoint/trie rebuild integrity risk.
