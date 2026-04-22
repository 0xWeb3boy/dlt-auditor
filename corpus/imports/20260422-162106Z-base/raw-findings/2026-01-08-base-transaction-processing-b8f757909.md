---
case_id: case_20260108_b8f757909
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2026-01-08
source_refs:
  - git:b8f7579091908e6ca101745aae342529ccb6ac39
  - "fault-proof/src/challenger.rs:245"
  - "fault-proof/src/challenger.rs:648"
  - "fault-proof/src/challenger.rs:184"
bug_class: deadline-enforcement
impact_type:
  - challenge-decision-errors
confidence: medium
tags:
  - blockchain-core
  - fault-proof
  - offchain-challenger
  - deadline-check
  - state-sync
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a bug fix in the off-chain challenger sync logic, not a confirmed vulnerability fix. The key change makes deadline expiry depend directly on now_ts >= deadline for all in-progress games, instead of only when the proposal was already marked Challenged. That supports a claim that the challenger could previously mis-handle expired unchallenged games during state sync, but it does not establish that an invalid on-chain action would succeed or that protocol security was actually broken.

## Observed Patch Facts

1. In `fault-proof/src/challenger.rs`, the patch replaces `let is_game_over = match proposal_status {` with `let is_game_over = now_ts >= deadline;`.

2. In `fault-proof/src/challenger.rs`, the patch adds `// ==================== Integration Test Helpers ====================`.

3. In `fault-proof/src/challenger.rs`, the patch replaces `async fn sync_state(&self) -> Result<()> {` with `pub async fn sync_state(&self) -> Result<()> {`.

## Project Context

The changed code sits primarily in `fault-proof/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `fault-proof/src/proposer.rs`, `fault-proof/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `fault-proof/src/proposer.rs`, `fault-proof/src/lib.rs`. The strongest project-level identifiers around this patch are `game`, `GameStatus::IN_PROGRESS`, `ProposalStatus::Challenged`, and `ProposalStatus::Unchallenged`.

## Before/After Behavior

Before the patch, sync_state treated an in-progress game as over only when proposal_status was Challenged and now_ts >= deadline; otherwise is_game_over was forced false. That meant an expired game still marked Unchallenged could continue through the local branch that decides whether to challenge. After the patch, is_game_over is computed as now_ts >= deadline for every in-progress game before challenge or resolve decisions are derived.

# Root Cause

The challenger's local sync logic tied deadline expiry to proposal status instead of to the dispute deadline itself. As a result, expired but still Unchallenged games could be treated as locally challengeable during cache refresh.

## Walkthrough

1. sync_state refreshes cached dispute-game state and computes follow-up actions.

2. For each game, the challenger reads status, proposal status, and deadline from the dispute game contract.

3. In the pre-fix logic, is_game_over became true only for ProposalStatus::Challenged games whose deadline had passed.

4. The same branch used !is_game_over when deciding whether an unchallenged game should produce an update for challenge handling.

5. That allowed an expired game that remained Unchallenged to look active in the challenger's local decision path.

6. The fix computes game-over status directly from the live deadline for all in-progress games, removing the proposal-status gate.

7. The newly public sync_state method and added integration helpers appear to support regression testing and inspection, not define the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| fault-proof/src/challenger.rs | 184 | `sync_state` entrypoint that refreshes the challenger's cached view of dispute games and computes follow-up actions |
| fault-proof/src/challenger.rs | 223 | in-progress game action-selection logic that reads status, proposal status, and deadline from the dispute game contract |
| fault-proof/src/challenger.rs | 245 | pre-fix branch where unchallenged games could bypass the deadline-based `is_game_over` check and still be considered challengeable |

## Code Snippets

## Snippet 1

Context: `fault-proof/src/challenger.rs:245` (changes a sensitive control or state-update path)

Before
```rust
match status {
                    GameStatus::IN_PROGRESS => {
                        let is_game_over = match proposal_status {
                            ProposalStatus::Challenged => now_ts >= deadline,
                            _ => false,
                        };

                        if proposal_status == ProposalStatus::Unchallenged {
```
After
```rust
match status {
                    GameStatus::IN_PROGRESS => {
                        let is_game_over = now_ts >= deadline;

                        // Determine challenge/resolve actions based on proposal status.
                        // - Unchallenged: challenge if game is still active AND (invalid OR parent
                        //   lost)
                        // - Challenged: resolve if game is over AND parent resolved AND we
```

## Snippet 2

Context: `fault-proof/src/challenger.rs:648` (changes persisted or aggregate state handling)

Before
```rust
Ok(())
    }
}
```
After
```rust
Ok(())
    }

    // ==================== Integration Test Helpers ====================

    /// Returns a copy of a game's full internal state for testing.
    #[cfg(feature = "integration")]
    pub async fn get_game(&self, index: U256) -> Option<Game> {
```

## Snippet 3

Context: `fault-proof/src/challenger.rs:184` (changes a sensitive control or state-update path)

Before
```rust
///    - Games are evicted once finalized with no remaining credit or whenever resolves as
    ///      defender wins.
    async fn sync_state(&self) -> Result<()> {
        // 1. Load new games.
        let mut next_index = {
```
After
```rust
///    - Games are evicted once finalized with no remaining credit or whenever resolves as
    ///      defender wins.
    pub async fn sync_state(&self) -> Result<()> {
        // 1. Load new games.
        let mut next_index = {
```

# Fix Pattern

Replace a status-gated time check with a direct deadline check at the decision point, then add test-oriented access paths to verify state-sync behavior.

## How It Was Fixed

The patch changes the in-progress branch so is_game_over is always derived from now_ts >= deadline. This makes deadline expiry apply uniformly before challenge and resolve actions are selected. The separate change making sync_state public and adding integration-only getters appears to enable tests to exercise and inspect the corrected behavior.

# Why It Matters

1. It prevents the challenger from treating some expired games as still active solely because their proposal status had not advanced.

2. It reduces local state-sync inconsistencies in a protocol-facing automation component.

3. The evidence only shows corrected off-chain action selection, not a proven exploitable on-chain flaw.

# Evidence Notes

Direct evidence is limited to challenger.rs. The strongest hunk changes is_game_over from a match on proposal_status to an unconditional now_ts >= deadline within the GameStatus::IN_PROGRESS path. The surrounding context shows that value influences challenge and resolve action selection. The public sync_state change and integration-only getters are better understood as test support. Nothing in the supplied evidence proves that a post-deadline challenge would succeed on-chain, cause loss of funds, or create consensus impact. Protocol security invariant: The challenger should treat any in-progress dispute game as no longer active for challenge decisions once the live on-chain deadline has passed, regardless of proposal status. Verification notes: The patch does not prove an on-chain contract vulnerability; it shows an off-chain challenger decision bug. The patch does not prove theft, consensus failure, or a fully weaponizable exploit path. The public `sync_state` change and integration-only getters appear to support testing/inspection and are not by themselves security evidence. The evidence does not show whether incorrect post-deadline actions would succeed on-chain or merely waste attempts / desynchronize local state. Behavioral bug is directly supported by the changed condition in challenger.rs. Security impact is not established from the supplied diff excerpts. No evidence here shows contract-side validation failure or a demonstrated exploit path. Classification is therefore unclear rather than confirmed or likely security. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `deadline-enforcement`
Final impact type: `challenge-decision-errors`
Final confidence: `medium`
Final tags: `blockchain-core, fault-proof, offchain-challenger, deadline-check, state-sync`

The supplied diff supports a security-hardening interpretation, not a proven exploitable vulnerability fix. The core change corrects how the fault-proof challenger decides whether an in-progress game is already over: before, deadline expiry was only recognized for `Challenged` proposals; after, expiry is enforced uniformly with `now_ts >= deadline`. In a protocol-defense component, tightening deadline handling in challenge/resolve logic is security-relevant, because stale or out-of-window actions are risky behavior. However, the patch alone does not prove that the old behavior could be exploited on-chain, cause fund loss, or break consensus, so this should be retained only as hardening.

## Security Evidence

1. `sync_state` drives challenge/resolve decisions for dispute games in the fault-proof challenger.
2. The patch replaces a proposal-status-gated game-over check with an unconditional deadline check.
3. Pre-fix logic could treat expired `Unchallenged` games as still active during local sync.
4. The changed code sits in a protocol-defense path, not in tests or metadata only.
5. Test-support changes (`pub sync_state`, integration helpers) are consistent with regression coverage for the corrected behavior.

## Missing Evidence

1. No proof that a post-deadline challenge would actually succeed on-chain.
2. No demonstrated exploit path, adversary control, or externally triggered attack scenario.
3. No evidence of fund loss, consensus impact, or contract-side invariant violation.
4. No patch evidence showing contract validation was bypassed rather than local automation misbehaving.

## Claim Boundaries

1. Supported: the patch hardens deadline enforcement in off-chain challenger state synchronization.
2. Supported: before the fix, expired but `Unchallenged` games could be misclassified as locally challengeable.
3. Not supported: a confirmed on-chain security vulnerability was exploitable.
4. Not supported: the bug caused state corruption, theft, or consensus failure.
