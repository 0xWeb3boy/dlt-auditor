---
case_id: case_20240628_4fd033f283
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2024-06-28
source_refs:
  - git:4fd033f2837fab774c512d4c2f67be4bc164d9fd
  - "stackslib/src/chainstate/nakamoto/coordinator/mod.rs:1090"
  - "stackslib/src/chainstate/nakamoto/coordinator/mod.rs:652"
  - "stackslib/src/chainstate/nakamoto/coordinator/mod.rs:874"
  - "stackslib/src/chainstate/nakamoto/coordinator/mod.rs:860"
bug_class: canonical-fork-context-reward-set-lookup
impact_type:
  - liveness
  - consensus-divergence-risk
confidence: medium
tags:
  - blockchain
  - consensus
  - canonical-fork
  - reward-set
  - liveness
  - nakamoto-coordinator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security-relevant consensus/liveness fix in the Nakamoto coordinator. The patch changes reward-cycle handling to use or justify the correct fork context for reward-set lookup, with comments explaining why the canonical tip is safe at the end of prepare phase and why local-best use is only safe for the first Nakamoto reward set. The evidence supports a canonical fork-context lookup issue, but does not prove exploitability, invalid block acceptance, or a malformed transaction panic.

## Observed Patch Facts

1. In `stackslib/src/chainstate/nakamoto/coordinator/mod.rs`, the patch replaces `let reward_cycle_info = self.get_nakamoto_reward_cycle_info(header.block_height)?;` with `// NOTE(safety): the reason it's safe to use the local best stacks tip here is`.

2. In `stackslib/src/chainstate/nakamoto/coordinator/mod.rs`, the patch replaces `// only proceed if we have processed the _anchor block_ for this reward cycle` with `// NOTE(safety): this is not guaranteed to be the canonical best Stacks tip.`.

3. In `stackslib/src/chainstate/nakamoto/coordinator/mod.rs`, the patch replaces `let stacks_epoch = self` with `let stacks_epoch = SortitionDB::get_stacks_epoch_by_epoch_id(`.

4. In `stackslib/src/chainstate/nakamoto/coordinator/mod.rs`, the patch replaces `let stacks_epoch = self` with `let stacks_epoch = SortitionDB::get_stacks_epoch_by_epoch_id(`.

## Project Context

The changed code sits primarily in `stackslib/src/chainstate/nakamoto/coordinator`, `stackslib/src/chainstate/nakamoto`, which anchors the finding in the `storage` area of the project. Historical context from `stackslib/src/chainstate/nakamoto/coordinator/tests.rs`, `stackslib/src/chainstate/nakamoto/test_signers.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stackslib/src/chainstate/nakamoto/test_signers.rs`, `stackslib/src/chainstate/nakamoto/miner.rs`. The strongest project-level identifiers around this patch are `reward`, `SortitionDB::get_stacks_epoch_by_epoch_id`, `estimator`, and `cycle`. Nearby tests or test-like files include `stackslib/src/chainstate/nakamoto/tests/node.rs`, `stackslib/src/chainstate/nakamoto/tests/mod.rs`.

## Before/After Behavior

Before the patch, the reward-cycle-start path loaded Nakamoto reward-cycle info by block height with no canonical sortition-tip basis shown in the supplied hunk. After the patch, the code derives a canonical sortition tip from coordinator state and documents why using the canonical/local-best Stacks tip is safe only under specific reward-set uniqueness conditions. The cost and fee estimator changes switch epoch lookup APIs and appear ancillary, not the core security-relevant behavior.

# Root Cause

The supported root cause is a reward-set lookup that was not clearly bound to the canonical sortition fork context at a point where coordinator behavior depends on a converged reward-set view. The evidence does not support claims about malformed transactions, panic-prone decoding, or attacker-controlled input.

## Walkthrough

1. At a Nakamoto reward-cycle boundary, the coordinator must obtain reward-cycle information before proceeding.

2. The pre-patch hunk shows lookup by block height through `get_nakamoto_reward_cycle_info(header.block_height)` without an explicit canonical sortition-tip input in the supplied evidence.

3. The patch adds canonical-tip handling and safety comments tying the lookup to the canonical MARF/fork view at the end of prepare phase.

4. A separate `can_process_nakamoto` path is annotated to clarify that local-best Stacks-tip use is safe only for the first Nakamoto reward set under epoch2 anchor selection rules.

5. Estimator epoch lookup changes are present but are not supported as the security-relevant fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stackslib/src/chainstate/nakamoto/coordinator/mod.rs | 1090 | Loads Nakamoto reward-cycle info at reward-cycle start; patch changes the lookup basis toward the canonical sortition/Stacks tip context and documents why this is safe at the end of prepare phase. |
| stackslib/src/chainstate/nakamoto/coordinator/mod.rs | 652 | Determines whether Nakamoto processing can proceed by loading the first Nakamoto reward set; patch documents the narrower case where local best Stacks tip is safe because epoch2 anchor selection yields a single reward set. |
| stackslib/src/chainstate/nakamoto/coordinator/mod.rs | 860 | Updates cost estimator epoch lookup to use SortitionDB connection API; appears ancillary to coordinator state access rather than the main reward-set invariant. |
| stackslib/src/chainstate/nakamoto/coordinator/mod.rs | 874 | Updates fee estimator epoch lookup to use SortitionDB connection API; appears ancillary to coordinator state access rather than the main reward-set invariant. |

## Code Snippets

## Snippet 1

Context: `stackslib/src/chainstate/nakamoto/coordinator/mod.rs:1090` (changes a sensitive control or state-update path)

Before
```rust
// we're at the end of the prepare phase, so we'd better have obtained the reward
                // cycle info of we must block.
                let reward_cycle_info = self.get_nakamoto_reward_cycle_info(header.block_height)?;
                if let Some(rc_info) = reward_cycle_info.as_ref() {
                    // in nakamoto, if we have any reward cycle info at all, it will be known.
```
After
```rust
// we're at the end of the prepare phase, so we'd better have obtained the reward
                // cycle info of we must block.
                // NOTE(safety): the reason it's safe to use the local best stacks tip here is
                // because as long as at least 30% of the signers are honest, there's no way there
                // can be two or more distinct reward sets calculated for a reward cycle.  Due to
                // signature malleability, there can be multiple unconfirmed siblings at a given
                // height H, but at height H+1, exactly one of those siblings will be canonical,
                // and will remain canonical with respect to its tenure's Bitcoin fork forever.
```

## Snippet 2

Context: `stackslib/src/chainstate/nakamoto/coordinator/mod.rs:652` (changes a sensitive control or state-update path)

Before
```rust
.expect("FATAL: epoch3 block height has no reward cycle");

        // only proceed if we have processed the _anchor block_ for this reward cycle
        let Some((rc_info, _)) = load_nakamoto_reward_set(
            self.burnchain
```
After
```rust
.expect("FATAL: epoch3 block height has no reward cycle");

        // NOTE(safety): this is not guaranteed to be the canonical best Stacks tip.
        // However, it's safe to use here because we're only interested in loading up the first
        // Nakamoto reward set, which uses the epoch2 anchor block selection algorithm.  There will
        // only be one such reward set in epoch2 rules, since it's tied to a specific block-commit
        // (note that this is not true for reward sets generated in Nakamoto prepare phases).
        let (local_best_stacks_ch, local_best_stacks_bhh) =
```

## Snippet 3

Context: `stackslib/src/chainstate/nakamoto/coordinator/mod.rs:874` (changes a consensus- or validator-sensitive branch)

Before
```rust
// update fee estimator
            if let Some(ref mut estimator) = self.fee_estimator {
                let stacks_epoch = self
                    .sortition_db
                    .index_conn()
                    .get_stacks_epoch_by_epoch_id(&block_receipt.evaluated_epoch)
                    .expect("Could not find a stacks epoch.");
                if let Err(e) = estimator.notify_block(&block_receipt, &stacks_epoch.block_limit) {
```
After
```rust
// update fee estimator
            if let Some(ref mut estimator) = self.fee_estimator {
                let stacks_epoch = SortitionDB::get_stacks_epoch_by_epoch_id(
                    self.sortition_db.conn(),
                    &block_receipt.evaluated_epoch,
                )?
                .expect("Could not find a stacks epoch.");
                if let Err(e) = estimator.notify_block(&block_receipt, &stacks_epoch.block_limit) {
```

## Snippet 4

Context: `stackslib/src/chainstate/nakamoto/coordinator/mod.rs:860` (changes a consensus- or validator-sensitive branch)

Before
```rust
// update cost estimator
            if let Some(ref mut estimator) = self.cost_estimator {
                let stacks_epoch = self
                    .sortition_db
                    .index_conn()
                    .get_stacks_epoch_by_epoch_id(&block_receipt.evaluated_epoch)
                    .expect("Could not find a stacks epoch.");
                estimator.notify_block(
```
After
```rust
// update cost estimator
            if let Some(ref mut estimator) = self.cost_estimator {
                let stacks_epoch = SortitionDB::get_stacks_epoch_by_epoch_id(
                    self.sortition_db.conn(),
                    &block_receipt.evaluated_epoch,
                )?
                .expect("Could not find a stacks epoch.");
                estimator.notify_block(
```

# Fix Pattern

Bind consensus-adjacent state lookups to the canonical fork context, and narrowly document any remaining local-best lookups only where protocol rules guarantee a unique result.

## How It Was Fixed

The patch changes the coordinator reward-set lookup path to use the canonical sortition-tip context memoized by the coordinator/sortition DB and adds safety notes explaining the prepare-phase and first-reward-set cases. Ancillary estimator code was updated to use `SortitionDB::get_stacks_epoch_by_epoch_id(self.sortition_db.conn(), ...)?`.

# Why It Matters

1. Reward-set lookup affects Nakamoto coordinator progress.

2. Wrong fork context can plausibly cause nodes to observe missing or divergent reward-set state.

3. The supported impact is consensus/liveness risk, not confirmed remote exploitability.

4. The evidence excludes the draft baseline's malformed-transaction panic theory.

# Evidence Notes

Evidence is limited to commit `4fd033f2837fab774c512d4c2f67be4bc164d9fd` and hunks in `stackslib/src/chainstate/nakamoto/coordinator/mod.rs`. The commit subject directly describes querying the reward set through the MARF using the canonical fork memoized in the sortition DB. The changed comments discuss canonical siblings, prepare-phase timing, signature malleability, and reward-set uniqueness. The supplied evidence does not show tests, a concrete exploit path, direct safety failure, or security relevance for fee/cost estimator changes. Protocol security invariant: At Nakamoto reward-cycle boundaries, coordinator reward-set lookups should be made from the Stacks state associated with the canonical sortition fork, so honest nodes use the same reward-set view despite temporary unconfirmed siblings. Verification notes: No proof that an attacker can force two valid reward sets for the same reward cycle. No proof of direct chain-safety failure such as accepting invalid blocks. No proof of a malformed transaction panic or decoded-input crash despite the heuristic baseline suggesting that shape. No proof that fee or cost estimator changes are security-relevant. Impact is best characterized as consensus/liveness risk from wrong fork-context state lookup, not confirmed remote exploitability. No command execution or file inspection was performed. Full after-code for the reward-set call is not included in the supplied evidence. No proof is supplied that an attacker can trigger divergent reward sets. No proof is supplied that invalid blocks could be accepted. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `canonical-fork-context-reward-set-lookup`
Final impact type: `liveness, consensus-divergence-risk`
Final confidence: `medium`
Final tags: `blockchain, consensus, canonical-fork, reward-set, liveness, nakamoto-coordinator`

The supplied evidence supports a security-hardening classification, not a confirmed security-fix. The commit and patch focus on querying Nakamoto reward-set state from the canonical fork/MARF context and narrowly documenting when local-best Stacks tip use is safe. In a blockchain coordinator, that is security-sensitive consensus/liveness behavior, but the evidence does not prove an exploitable bug, invalid block acceptance, or attacker-triggered chain split.

## Security Evidence

1. Commit subject explicitly says reward-set lookup must be queried from the canonical fork memoized in the sortition DB.
2. Patch comments discuss canonical siblings, prepare-phase timing, signature malleability, and reward-set uniqueness assumptions.
3. Changed code sits in Nakamoto coordinator reward-cycle processing, a consensus/liveness-sensitive path.
4. The patch narrows and documents safe use of non-canonical/local-best Stacks tip state.

## Missing Evidence

1. No test or reproduction showing nodes diverging or blocking before the fix.
2. No proof that an attacker can force multiple valid reward sets for a reward cycle.
3. No evidence of invalid block acceptance, remote crash, or direct fund loss.
4. Fee and cost estimator API changes are not shown to be security-relevant.

## Claim Boundaries

1. Treat as consensus/liveness hardening around canonical fork-context lookup.
2. Do not claim confirmed exploitability from the supplied patch alone.
3. Do not claim malformed transaction handling, decoding panic, or input-validation vulnerability.
4. Do not treat ancillary estimator lookup changes as the core security issue.
