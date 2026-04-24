---
case_id: case_20250206_ec85a08ef9
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2025-02-06
source_refs:
  - git:ec85a08ef93007bdd65f4b6daa2811a5275c116b
  - "bin/client/src/interop/mod.rs:82"
  - "bin/client/src/interop/transition.rs:179"
  - "crates/proof-sdk/proof-interop/src/pre_state.rs:41"
  - "bin/client/src/interop/transition.rs:118"
bug_class: state-machine-validation
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - fault-proof
  - state-transition
  - validation
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes how the interop fault-proof client handles a `SuperRoot` timestamp boundary case. It adds an explicit no-op path with an equality check on the claimed post-state, switches one derivation target from the claimed block number to the disputed block number, and removes a separate timestamp-based rejection from the final transition check. This is evidence of a correctness or invariant fix in a security-sensitive path, but the provided diff does not establish a concrete vulnerability outcome.

## Observed Patch Facts

1. In `bin/client/src/interop/mod.rs`, the patch replaces `PreState::SuperRoot(_) => {` with `PreState::SuperRoot(ref super_root) => {`.

2. In `bin/client/src/interop/transition.rs`, the patch replaces `if post_state_commitment != expected_post_state || timestamps.is_some_and(|(a, b)| a...` with `if post_state_commitment != expected_post_state {`.

3. In `crates/proof-sdk/proof-interop/src/pre_state.rs`, the patch replaces `/// Returns the active L2 chain ID of the [PreState]. This is the chain ID of the out...` with `/// Returns the timestamp of the [PreState].`.

4. In `bin/client/src/interop/transition.rs`, the patch replaces `match driver.advance_to_target(rollup_config.as_ref(), Some(claimed_l2_block_number))...` with `match driver.advance_to_target(rollup_config.as_ref(), Some(disputed_l2_block_number)...`.

## Project Context

The changed code sits primarily in `bin/client/src/interop`, `bin/client/src`, `crates/proof-sdk/proof-interop/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/proof-sdk/proof-interop/src/boot.rs`, `crates/proof-sdk/proof-interop/src/consolidation.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/proof-sdk/proof-interop/src/boot.rs`, `crates/proof-sdk/proof-interop/src/consolidation.rs`. The strongest project-level identifiers around this patch are `timestamp`, `PreState::SuperRoot`, `Self::SuperRoot`, and `boot`.

## Before/After Behavior

Before the patch, the `PreState::SuperRoot` branch always entered `sub_transition(...)`. After the patch, it first checks whether `super_root.timestamp >= boot.claimed_l2_timestamp`; if so, it accepts only when `boot.agreed_pre_state_commitment == boot.claimed_post_state`, otherwise it returns `InvalidClaim`. Separately, the transition path now advances to `disputed_l2_block_number` instead of `claimed_l2_block_number`, and the final check now rejects only on post-state commitment mismatch rather than on commitment mismatch or an extra timestamp comparison.

# Root Cause

The visible changes support a conclusion that the state machine previously handled a timestamp edge case incorrectly or incompletely: a `SuperRoot` case that should sometimes be treated as a no-op was always processed as a sub-transition, with related ambiguity in how the transition target and final validation were checked.

## Walkthrough

1. `run(...)` dispatches on `boot.agreed_pre_state` in the interop client.

2. Previously, the `PreState::SuperRoot(_)` branch always called `sub_transition(...)`.

3. The patch binds `ref super_root` and checks `super_root.timestamp >= boot.claimed_l2_timestamp`.

4. If that condition holds, the code now requires `boot.agreed_pre_state_commitment == boot.claimed_post_state` and returns success only in that case.

5. If the same condition holds but the commitments differ, the code now returns `FaultProofProgramError::InvalidClaim(...)`.

6. A `PreState::timestamp()` helper is added to expose the timestamp from either `SuperRoot` or `TransitionState`.

7. In `transition.rs`, derivation advances to `disputed_l2_block_number` instead of `claimed_l2_block_number`.

8. The final transition check now compares only the computed post-state commitment against the expected post-state commitment.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| bin/client/src/interop/mod.rs | 82 | Top-level interop STF dispatch; decides whether a SuperRoot step is a no-op and enforces claimed post-state equality in that case. |
| bin/client/src/interop/transition.rs | 118 | Advances derivation to the disputed L2 block before constructing the optimistic block used in the transition. |
| bin/client/src/interop/transition.rs | 179 | Checks that the transitioned state's commitment matches the expected post-state commitment. |
| crates/proof-sdk/proof-interop/src/pre_state.rs | 41 | Provides canonical PreState timestamp access used to determine whether the STF should transition or remain a no-op. |

## Code Snippets

## Snippet 1

Context: `bin/client/src/interop/mod.rs:82` (changes a sensitive control or state-update path)

Before
```rust
// sub-problem.
    match boot.agreed_pre_state {
        PreState::SuperRoot(_) => {
            // If the pre-state is a super root, the first sub-problem is always selected.
            sub_transition(oracle, handle_register, boot).await
        }
        PreState::TransitionState(ref transition_state) => {
            // If the pre-state is a transition state, the sub-problem is selected based on the
```
After
```rust
// sub-problem.
    match boot.agreed_pre_state {
        PreState::SuperRoot(ref super_root) => {
            // If the claimed L2 block timestamp is less than the super root timestamp, the
            // post-state muust be the agreed pre-state to accommodate trace extension.
            if super_root.timestamp >= boot.claimed_l2_timestamp {
                if boot.agreed_pre_state_commitment == boot.claimed_post_state {
                    return Ok(());
```

## Snippet 2

Context: `bin/client/src/interop/transition.rs:179` (changes a sensitive control or state-update path)

Before
```rust
}

    if post_state_commitment != expected_post_state || timestamps.is_some_and(|(a, b)| a != b) {
        error!(
            target: "interop_client",
```
After
```rust
}

    if post_state_commitment != expected_post_state {
        error!(
            target: "interop_client",
```

## Snippet 3

Context: `crates/proof-sdk/proof-interop/src/pre_state.rs:41` (changes a sensitive control or state-update path)

Before
```rust
}

    /// Returns the active L2 chain ID of the [PreState]. This is the chain ID of the output root
    /// that is to be committed to in the next transition step, or `0xDEAD` if the [PreState]
    /// has already been fully saturated.
    pub fn active_l2_chain_id(&self) -> Option<u64> {
        match self {
            Self::SuperRoot(super_root) => {
```
After
```rust
}

    /// Returns the timestamp of the [PreState].
    pub const fn timestamp(&self) -> u64 {
        match self {
            Self::SuperRoot(super_root) => super_root.timestamp,
            Self::TransitionState(transition_state) => transition_state.pre_state.timestamp,
        }
```

## Snippet 4

Context: `bin/client/src/interop/transition.rs:118` (changes a sensitive control or state-update path)

Before
```rust
// Run the derivation pipeline until we are able to produce the output root of the claimed
    // L2 block.
    match driver.advance_to_target(rollup_config.as_ref(), Some(claimed_l2_block_number)).await {
        Ok((safe_head, output_root)) => {
            let optimistic_block = OptimisticBlock::new(safe_head.block_info.hash, output_root);
```
After
```rust
// Run the derivation pipeline until we are able to produce the output root of the claimed
    // L2 block.
    match driver.advance_to_target(rollup_config.as_ref(), Some(disputed_l2_block_number)).await {
        Ok((safe_head, output_root)) => {
            let optimistic_block = OptimisticBlock::new(safe_head.block_info.hash, output_root);
```

# Fix Pattern

Add an explicit guard for a state-machine edge case at the dispatch boundary, enforce exact state commitment equality for the no-op case, and align downstream transition inputs and validation with the intended disputed-step semantics.

## How It Was Fixed

The fix encodes the no-op condition directly in the `SuperRoot` branch, rejects mismatched post-state claims for that case, adds a canonical timestamp accessor on `PreState`, changes derivation to use the disputed block number, and simplifies final acceptance to the committed post-state hash comparison.

# Why It Matters

1. The modified code is in the verifier/state-transition path, so incorrect edge-case handling can affect dispute evaluation.

2. The patch makes the no-op case explicit instead of always forcing a sub-transition.

3. The post-state equality check gives a concrete rule for claims in that no-op case.

4. The evidence does not show whether the old behavior caused false acceptance, false rejection, or only trace-extension correctness issues.

# Evidence Notes

Security relevance is plausible because the patch touches fault-proof verifier logic, but the provided evidence does not prove an exploitable security bug. The commit subject and hunks support a state-machine correctness fix around no-op sub-transitions and disputed-step handling. The diff alone does not show that invalid states could previously be finalized, that an attacker could bypass verification, or that the impact exceeded correctness/liveness behavior for this edge case. Protocol security invariant: When the agreed pre-state is a `SuperRoot` whose timestamp is at or after the claimed L2 timestamp, the step should be treated as a no-op and the claimed post-state should equal the agreed pre-state commitment; otherwise the transition logic should evaluate the disputed step against the expected post-state commitment. Verification notes: The patch does not prove that an attacker could finalize an invalid state on chain. The evidence does not establish whether the pre-fix behavior caused safety failure, liveness failure, or both. No memory-safety, key-management, or cryptographic primitive break is shown by these hunks. The reachable conditions under production dispute games for the timestamp edge case are not proven by the patch alone. No tests or runtime traces are provided in the input. The reachable conditions for the timestamp edge case are not established by the diff alone. The patch supports a correctness/invariant interpretation more strongly than a confirmed vulnerability claim. Security classification should stay downgraded unless additional evidence shows invalid-claim acceptance or comparable exploitability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `state-machine-validation`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `fault-proof, state-transition, validation, consensus`

The patch changes verifier-like fault-proof state-transition logic in a security-sensitive path and adds an explicit rejection for an invalid claimed post-state in a no-op `SuperRoot` timestamp case. That is meaningful hardening of claim validation and dispute semantics. However, the diff alone does not prove that the old behavior enabled acceptance of a malicious claim or any concrete exploit, so this should be retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. The changed code is in interop fault-proof / state-transition validation logic, which is security-sensitive for dispute correctness.
2. The new `SuperRoot` branch introduces an explicit no-op condition and rejects mismatched `claimed_post_state` with `InvalidClaim`.
3. The patch aligns transition derivation with `disputed_l2_block_number`, suggesting tighter disputed-step verification semantics.
4. The final check still enforces post-state commitment equality, preserving commitment-based validation while removing a separate timestamp mismatch check.

## Missing Evidence

1. No test, trace, or commit message explains whether pre-fix behavior allowed false acceptance of invalid claims.
2. The patch does not show an attacker-controlled path from the old logic to finalized invalid state or funds loss.
3. No evidence establishes whether the issue was safety-critical versus only correctness/liveness behavior during trace extension.

## Claim Boundaries

1. Supported: this is a security-relevant hardening change in fault-proof verification logic.
2. Supported: the patch fixes a state-machine edge case around no-op sub-transitions and claimed post-state validation.
3. Not supported: a proven exploitable vulnerability or confirmed pre-fix invalid-claim acceptance.
4. Not supported: any specific impact beyond conservative consensus/dispute-integrity hardening.
