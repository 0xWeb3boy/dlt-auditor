---
case_id: case_20260110_f40b60f3a9
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2026-01-10
source_refs:
  - git:f40b60f3a9d81bd177f1990902d41b71d5e86ffe
  - "consensus/core/src/commit_finalizer.rs:265"
  - "crates/sui-protocol-config/src/lib.rs:4450"
  - "consensus/core/src/commit_finalizer.rs:688"
  - "crates/sui-protocol-config/src/lib.rs:936"
bug_class: consensus-finalization-hardening
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - validator
  - finalization
  - garbage-collection
  - vote-accounting
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes consensus finalization logic so transactions in blocks below the leader-derived GC bound are not directly finalized based only on commit evidence. This is plausibly security-relevant consensus correctness work, but the provided evidence does not establish an exploitable vulnerability, chain divergence, invalid transaction finalization, or attacker-controlled trigger.

## Observed Patch Facts

1. In `consensus/core/src/commit_finalizer.rs`, the patch replaces `fn try_direct_finalize_commit(&mut self, index: usize) {` with `// Direct commit means every transaction in the commit can be considered to have a qu...`.

2. In `crates/sui-protocol-config/src/lib.rs`, the patch replaces `if cfg!(msim) {` with `if cfg!(msim) || in_antithesis() {`.

3. In `consensus/core/src/commit_finalizer.rs`, the patch replaces `// casted by an earlier block from the same origin.` with `// casted by an earlier block from the same origin, or the votes might not be propose...`.

4. In `crates/sui-protocol-config/src/lib.rs`, the patch adds `// If true, skip GC'ed blocks in direct finalization.`.

## Project Context

The changed code sits primarily in `consensus/core/src`, `consensus/core`, `crates/sui-protocol-config/src`, which anchors the finding in the `consensus` area of the project. Historical context from `consensus/core/src/commit_syncer.rs`, `consensus/core/src/commit.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/core/src/transaction_certifier.rs`, `consensus/core/src/dag_state.rs`. The strongest project-level identifiers around this patch are `votes`, `block`, `commit`, and `transactions`. Nearby tests or test-like files include `consensus/core/src/tests/universal_committer_tests.rs`, `consensus/core/src/tests/pipelined_committer_tests.rs`.

## Before/After Behavior

Before the patch, the supplied evidence shows direct finalization treating transactions in a commit as implicitly quorum-supported except for reject-vote handling, with no shown GC-bound exclusion. After the patch, direct finalization documents and applies a second exclusion for blocks outside the commit leader's GC bound. The indirect finalization path also skips accept-vote accumulation when votes_gced is true, reflecting that GC may have prevented votes from being proposed.

# Root Cause

The apparent root cause was an over-broad quorum inference in consensus finalization: commit evidence could be treated as sufficient for direct transaction finalization even when GC might have prevented relevant transaction votes from being carried by voting or certifying blocks.

## Walkthrough

1. A commit reaches the finalizer and transactions from committed blocks are considered for direct finalization.

2. Direct finalization relies on an inference that committed transactions have quorum-backed post-commit vote evidence.

3. The patch adds a GC-bound exception: if the containing block is outside the GC bound computed from the commit leader, that inference may not hold.

4. The code comments explain that voting and certifying blocks may not include votes for transactions below the leader's GC bound.

5. Indirect finalization vote counting is aligned by skipping accept votes when votes_gced is true.

6. Protocol configuration adds a feature flag for skipping GCed blocks in direct finalization, and simulation/antithesis settings are adjusted to exercise GC behavior more often.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/core/src/commit_finalizer.rs | 265 | Direct commit finalization now accounts for reject votes and GC-bound blocks before treating transactions as quorum-certified. |
| consensus/core/src/commit_finalizer.rs | 634 | Indirect finalization traverses child blocks and determines when pending-block transaction votes may have been omitted due to GC. |
| consensus/core/src/commit_finalizer.rs | 688 | Vote accumulation skips accept votes when the pending block's votes may have been GCed, preserving conservative finalization. |
| crates/sui-protocol-config/src/lib.rs | 936 | Adds feature flag for skipping GCed blocks in direct finalization. |
| crates/sui-protocol-config/src/lib.rs | 4450 | Adjusts simulation and antithesis GC depth to exercise the GC/finalization path more often. |

## Code Snippets

## Snippet 1

Context: `consensus/core/src/commit_finalizer.rs:265` (changes bounds, limits, or capacity handling)

Before
```rust
// Tries directly finalizing transactions in the commit.
    fn try_direct_finalize_commit(&mut self, index: usize) {
        let num_commits = self.pending_commits.len();
        let commit_state = self
            .pending_commits
            .get_mut(index)
            .unwrap_or_else(|| panic!("Commit {} does not exist. len = {}", index, num_commits,));
```
After
```rust
// Tries directly finalizing transactions in the commit.
    // Direct commit means every transaction in the commit can be considered to have a quorum of post-commit certificates,
    // unless (1) the transaction has reject votes that do not reach quorum, or
    // (2) the block containing the transaction is outside the GC bound of the commit's leader.
    // In the 2nd case, when the blocks voting and certifying this commit's leader were proposed, there is a chance
    // that some of these voting and certifying blocks do not include votes for the transactions below the leader's GC bound.
    // So conservatively, these transactions are not directly finalized. The logic here matches the GC logic in
```

## Snippet 2

Context: `crates/sui-protocol-config/src/lib.rs:4450` (changes a consensus- or validator-sensitive branch)

Before
```rust
// Simtest specific overrides.
        if cfg!(msim) {
            // Trigger GC more often.
            cfg.consensus_gc_depth = Some(5);

            // Trigger checkpoint splitting more often.
```
After
```rust
// Simtest specific overrides.
        if cfg!(msim) || in_antithesis() {
            // Trigger GC more often.
            cfg.consensus_gc_depth = Some(6);

            // Trigger checkpoint splitting more often.
```

## Snippet 3

Context: `consensus/core/src/commit_finalizer.rs:688` (changes bounds, limits, or capacity handling)

Before
```rust
ignored.extend(curr_block_state.origin_descendants.iter());
                // Skip counting votes from current block if the votes on pending block could have been
                // casted by an earlier block from the same origin.
                // Note: if the current block casts reject votes on transactions in the pending block,
                // it can be assumed that accept votes are also casted to other transactions in the pending block.
                // But we choose to skip counting the accept votes in this edge case for simplicity.
                if context.protocol_config.consensus_skip_gced_accept_votes() && votes_gced {
                    let hostname = &context.committee.authority(curr_block_ref.author).hostname;
```
After
```rust
ignored.extend(curr_block_state.origin_descendants.iter());
                // Skip counting votes from current block if the votes on pending block could have been
                // casted by an earlier block from the same origin, or the votes might not be proposed due to GC.
                // Note: if the current block casts reject votes on transactions in the pending block,
                // it can be assumed that accept votes are also casted to other transactions in the pending block.
                // But we choose to skip counting the accept votes in this edge case for simplicity.
                if votes_gced {
                    let hostname = &context
```

## Snippet 4

Context: `crates/sui-protocol-config/src/lib.rs:936` (changes a consensus- or validator-sensitive branch)

Before
```rust
enable_object_funds_withdraw: bool,

    // If true, uses a new rounding mechanism for gas calculations, replacing the step-based one
    #[serde(skip_serializing_if = "is_false")]
```
After
```rust
enable_object_funds_withdraw: bool,

    // If true, skip GC'ed blocks in direct finalization.
    #[serde(skip_serializing_if = "is_false")]
    consensus_skip_gced_blocks_in_direct_finalization: bool,

    // If true, uses a new rounding mechanism for gas calculations, replacing the step-based one
    #[serde(skip_serializing_if = "is_false")]
```

# Fix Pattern

Make finalization conservative when quorum-vote inference depends on transaction votes that may have been omitted due to garbage collection.

## How It Was Fixed

The patch updates commit_finalizer logic and comments to treat GC-bound blocks as an exception to direct finalization. It also changes indirect vote counting to skip accept votes whenever votes_gced is true, and adds protocol configuration support for the direct-finalization GC check.

# Why It Matters

1. Protects a consensus finalization correctness invariant.

2. Avoids relying on implicit votes that GC may have omitted.

3. Keeps direct and indirect finalization aligned on GC-aware vote accounting.

4. Adds test/config coverage to exercise GC-sensitive finalization behavior.

# Evidence Notes

The evidence supports a consensus GC/vote-accounting fix in commit_finalizer.rs and related protocol configuration. It does not support the heuristic baseline's claims about malformed transaction decoding, panic-prone conversions, remote denial of service, or unchecked decoded values. It also does not prove a concrete security exploit or finalized invalid transaction, so the security classification should remain unclear rather than likely or confirmed. Protocol security invariant: A transaction should only be directly finalized from commit evidence when that evidence reliably implies quorum-backed transaction votes or certificates; blocks below the GC round computed from the commit leader may not have carried those votes. Verification notes: The patch does not show malformed transaction decoding or panic-on-invalid-input behavior. The evidence does not prove remote exploitability or an attacker-controlled trigger. The evidence does not prove finalized invalid transactions, only that prior direct finalization could rely on an unsafe quorum inference below the GC bound. The antithesis and snapshot changes are supporting coverage/configuration, not independent security fixes. No external exploitability evidence is provided. No test output or failing pre-patch scenario is provided. Antithesis and snapshot/config changes are supporting evidence, not independent vulnerability proof. Security corpus inclusion is not justified from the supplied evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-finalization-hardening`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, validator, finalization, garbage-collection, vote-accounting, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a proven concrete security fix. The change makes consensus transaction finalization more conservative when garbage collection may have caused transaction votes to be omitted, which tightens a security-sensitive consensus correctness invariant. However, the evidence does not prove an exploitable vulnerability, attacker-controlled trigger, finalized invalid transaction, fork, or liveness failure, so stronger security-fix claims should be avoided.

## Security Evidence

1. Direct finalization now excludes blocks outside the GC bound computed from the commit leader.
2. Patch comments state that voting or certifying blocks may not include votes for transactions below the leader's GC bound.
3. Indirect finalization vote counting is aligned to skip accept votes when votes may have been GCed.
4. A protocol feature flag is added specifically to skip GCed blocks in direct finalization.
5. The modified path is consensus finalization logic, a security-sensitive validator subsystem.

## Missing Evidence

1. No exploit scenario or attacker-controlled trigger is shown.
2. No evidence of finalized invalid transactions, chain divergence, or safety violation is provided.
3. No failing regression test or pre-patch reproduction is included in the supplied evidence.
4. No direct evidence supports the original liveness-failure impact classification.

## Claim Boundaries

1. Classify as consensus hardening around GC-aware finalization, not a confirmed vulnerability fix.
2. Do not claim malformed input handling, decoding safety, panic prevention, or remote denial of service.
3. Do not claim proven liveness impact from the supplied patch alone.
4. Do not claim exploitability beyond the conservative observation that consensus vote inference was tightened.
