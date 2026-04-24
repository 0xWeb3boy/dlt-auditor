---
case_id: case_20251126_3b59b5be60
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2025-11-26
source_refs:
  - git:3b59b5be6023589d039b815ab0f2f40d50faf70c
  - "consensus/core/src/commit_finalizer.rs:609"
  - "crates/sui-protocol-config/src/lib.rs:4716"
  - "crates/sui-protocol-config/src/lib.rs:2162"
  - "consensus/core/src/metrics.rs:912"
bug_class: consensus-vote-accounting-hardening
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - validator-logic
  - vote-accounting
  - garbage-collection
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is a consensus vote-accounting fix for Mysticeti fastpath finalization under garbage collection. It adds a guard that skips counting votes from a block when a same-author origin ancestor above the pending block round is missing from the retained block map and may have been GC'ed. The evidence supports a correctness issue in accept-vote aggregation, but it does not establish a vulnerability, attacker control, remote exploitability, or a demonstrated consensus safety failure.

## Observed Patch Facts

1. In `consensus/core/src/commit_finalizer.rs`, the patch replaces `// Ignore info from the block if its direct ancestor has been processed.` with `// The first ancestor of current block should have the same origin / author as the cu...`.

2. In `crates/sui-protocol-config/src/lib.rs`, the patch replaces `pub fn is_mysticeti_fpc_enabled_in_env() -> Option<bool> {` with `#[cfg(all(test, not(msim)))]`.

3. In `crates/sui-protocol-config/src/lib.rs`, the patch removes `if let Some(enabled) = is_mysticeti_fpc_enabled_in_env() {`.

4. In `consensus/core/src/metrics.rs`, the patch replaces `uptime: register_histogram_with_registry!(` with `finalizer_skipped_voting_blocks: register_int_counter_vec_with_registry!(`.

## Project Context

The changed code sits primarily in `consensus/core/src`, `consensus/core`, `crates/sui-protocol-config/src`, which anchors the finding in the `consensus` area of the project. Historical context from `consensus/core/src/block_verifier.rs`, `consensus/core/src/block_manager.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/core/src/transaction.rs`, `consensus/core/src/synchronizer.rs`. The strongest project-level identifiers around this patch are `block`, `from`, `have`, and `pending`. Nearby tests or test-like files include `consensus/core/src/tests/universal_committer_tests.rs`, `consensus/core/src/tests/randomized_tests.rs`.

## Before/After Behavior

Before the patch, the indirect finalization path traversed child blocks and skipped some origin-descendant votes, but the provided hunk does not show an explicit GC-aware check for a missing same-author origin ancestor between the pending block and current block. After the patch, the code checks the current block's first ancestor and skips counting the current block's vote when that ancestor has the same author, is at a higher round than the pending block, and is absent from `blocks_map`. A metric was added to count these skipped voting blocks.

# Root Cause

The finalizer's accept-vote aggregation relied on locally retained ancestry. If GC removed an intermediate same-author origin ancestor, the finalizer could lack evidence needed to decide whether a later same-author descendant should be treated as accepting pending transactions. The patch makes that uncertain case conservative by skipping the vote.

## Walkthrough

1. The indirect finalization path initializes accept-vote aggregators for pending transactions in a pending block.

2. It traverses child blocks from the pending block using the retained `blocks_map`.

3. The patch reads the current block's first ancestor and treats it as relevant same-origin ancestry when the author matches.

4. If that ancestor is above the pending block round but missing from `blocks_map`, the code treats the ancestry as incomplete, possibly due to GC.

5. Because the missing ancestor may have voted on the pending block and rejected pending transactions, the current block is not counted as an accept vote.

6. A new `finalizer_skipped_voting_blocks` metric records skipped blocks by authority.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/core/src/commit_finalizer.rs | 578 | Indirect finalization path that traverses child blocks and aggregates accept votes for pending transactions. |
| consensus/core/src/commit_finalizer.rs | 609 | New GC-aware ancestry check that skips counting votes when a same-author origin ancestor may have been garbage-collected. |
| consensus/core/src/metrics.rs | 906 | Metric for observing blocks skipped from voting due to uncertain immediate-descendant status. |
| crates/sui-protocol-config/src/lib.rs | 2159 | Mysticeti fastpath feature flag path; environment override removal appears ancillary to the consensus change. |

## Code Snippets

## Snippet 1

Context: `consensus/core/src/commit_finalizer.rs:609` (changes a consensus- or validator-sensitive branch)

Before
```rust
}
            let curr_block_state = blocks_map.get(&curr_block_ref).unwrap_or_else(|| panic!("Block {curr_block_ref} is either incorrectly gc'ed or failed to be recovered after crash.")).read();
            // Ignore info from the block if its direct ancestor has been processed.
            if ignored.insert(curr_block_ref) {
                // Skip collecting votes from origin descendants of current block.
                // Votes from origin descendants of current block do not count for this transactions.
                // Consider this case: block B is an origin descendant of block A (from the same authority),
                // and both blocks A and B link to another block C.
```
After
```rust
}
            let curr_block_state = blocks_map.get(&curr_block_ref).unwrap_or_else(|| panic!("Block {curr_block_ref} is either incorrectly gc'ed or failed to be recovered after crash.")).read();
            // The first ancestor of current block should have the same origin / author as the current block.
            // If it is not found in the blocks map but have round higher than the pending block, it might have
            // voted on the pending block but have been GC'ed.
            // Because the GC'ed block might have voted on the pending block and rejected some of the pending transactions,
            // we cannot assume current block is voting to accept transactions from the pending block.
            let curr_origin_ancestor_ref = curr_block_state.block.ancestors().first().unwrap();
```

## Snippet 2

Context: `crates/sui-protocol-config/src/lib.rs:4716` (changes a consensus- or validator-sensitive branch)

Before
```rust
}};
}

pub fn is_mysticeti_fpc_enabled_in_env() -> Option<bool> {
    if let Ok(v) = std::env::var("CONSENSUS") {
        if v == "mysticeti_fpc" {
            return Some(true);
        } else if v == "mysticeti" {
```
After
```rust
}};
}
#[cfg(all(test, not(msim)))]
mod test {
```

## Snippet 3

Context: `crates/sui-protocol-config/src/lib.rs:2162` (changes a sensitive control or state-update path)

Before
```rust
pub fn mysticeti_fastpath(&self) -> bool {
        if let Some(enabled) = is_mysticeti_fpc_enabled_in_env() {
            return enabled;
        }
        self.feature_flags.mysticeti_fastpath
    }
```
After
```rust
pub fn mysticeti_fastpath(&self) -> bool {
        self.feature_flags.mysticeti_fastpath
    }
```

## Snippet 4

Context: `consensus/core/src/metrics.rs:912` (changes a consensus- or validator-sensitive branch)

Before
```rust
registry
            ).unwrap(),
            uptime: register_histogram_with_registry!(
                "uptime",
```
After
```rust
registry
            ).unwrap(),
            finalizer_skipped_voting_blocks: register_int_counter_vec_with_registry!(
                "finalizer_skipped_voting_blocks",
                "Number of blocks skipped from voting due to potentially not being an immediate descendant.",
                &["authority"],
                registry
            ).unwrap(),
```

# Fix Pattern

Add a conservative GC-aware vote-accounting guard before aggregating accept votes when retained ancestry is incomplete.

## How It Was Fixed

`consensus/core/src/commit_finalizer.rs` now computes a `skip_votes` condition based on same-author ancestry, pending-block round, and absence of the ancestor from `blocks_map`. When the condition holds, the finalizer avoids counting the current block as an accept vote. `consensus/core/src/metrics.rs` adds observability for skipped voting blocks. The protocol-config environment override removal is ancillary and does not establish the root cause.

# Why It Matters

1. Prevents incomplete GC-pruned ancestry from being treated as proof of acceptance.

2. Makes vote aggregation conservative when an intermediate same-author vote may be missing.

3. Adds metrics for observing the new skip path.

4. The provided evidence does not prove a security vulnerability.

# Evidence Notes

Supported by the new comments and `skip_votes` logic in `consensus/core/src/commit_finalizer.rs` and the new metric in `consensus/core/src/metrics.rs`. The malformed-transaction, panic, and denial-of-service narrative from the heuristic baseline is unsupported by the supplied evidence. The evidence also does not show attacker-controlled GC behavior, a concrete exploit path, or a proven consensus safety violation. Protocol security invariant: The finalizer should only count a block as an accept vote for pending transactions when retained ancestry is sufficient to support that inference; garbage collection should not cause missing intermediate same-author ancestry to be interpreted as acceptance. Verification notes: The patch does not show malformed transaction decoding or panic-on-invalid-input behavior. The patch does not prove remote exploitability or an attacker-controlled GC schedule. The patch does not prove consensus safety violation by itself, only an overcounting condition that could affect finalization decisions. The protocol-config changes alone are not enough to classify this as a security fix. Commit message describes a fix and test for counting votes with GC. Primary code evidence is limited to vote accounting in the commit finalizer. Metric addition supports observability, not root cause. Protocol-config changes appear ancillary from the provided evidence. Security relevance is plausible because this is consensus logic, but vulnerability status is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-vote-accounting-hardening`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, validator-logic, vote-accounting, garbage-collection, security-hardening`

The evidence supports retaining this as security hardening, not a confirmed vulnerability fix. The patch changes consensus finalization vote accounting to avoid treating a descendant block as an accept vote when a same-author ancestor above the pending block may have been garbage-collected and may have rejected pending transactions. That is a conservative tightening in security-sensitive validator consensus logic, but the supplied evidence does not prove attacker control, exploitability, or an actual consensus safety violation.

## Security Evidence

1. Consensus commit finalizer now skips votes when retained ancestry is incomplete due to possible GC.
2. Patch comment explicitly says the GC'ed block may have rejected pending transactions, so the current block cannot be assumed to accept them.
3. The changed logic affects accept-vote aggregation for pending transactions in validator consensus finalization.
4. A metric was added to observe blocks skipped by the new conservative vote-accounting path.

## Missing Evidence

1. No proof that an attacker can cause or influence the GC state needed to trigger the issue.
2. No demonstrated exploit, consensus fork, invalid finalization, or safety failure is shown.
3. No security advisory, CVE, or explicit vulnerability language is provided.
4. Protocol-config and metrics changes are ancillary and do not independently establish security impact.

## Claim Boundaries

1. Classify as hardening of consensus vote accounting, not a confirmed exploitable security fix.
2. Do not claim remote exploitability or attacker-controlled GC from the supplied evidence.
3. Do not claim a concrete liveness or safety failure beyond possible incorrect accept-vote aggregation.
4. Do not rely on the ancillary feature-flag cleanup as security evidence.
