---
case_id: case_20241122_848921199d
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2024-11-22
source_refs:
  - git:848921199df98106bbaf82cc290e68fff5b32e31
  - "stacks-signer/src/v0/signer.rs:598"
  - "stacks-signer/src/v0/signer.rs:475"
  - "stacks-signer/src/v0/signer.rs:318"
  - "stacks-signer/src/signerdb.rs:159"
bug_class: stale-consensus-validation-race
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - validator-ops
  - consensus
  - race-condition
  - stale-state-validation
  - signer-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant race in signer block validation. The supported claim is that queued validation approval could be applied after the signer's sortition view changed, and the fix rechecks the block against the current view before local acceptance. The evidence does not establish signature forgery, private key compromise, replay, or guaranteed final on-chain invalid block acceptance.

## Observed Patch Facts

1. In `stacks-signer/src/v0/signer.rs`, the patch replaces `if let Err(e) = block_info.mark_locally_accepted(false) {` with `if let Some(block_response) = self.check_block_against_sortition_state(`.

2. In `stacks-signer/src/v0/signer.rs`, the patch replaces `let block_response = if let Some(sortition_state) = sortition_state {` with `let block_response = self.check_block_against_sortition_state(`.

3. In `stacks-signer/src/v0/signer.rs`, the patch replaces `/// Handle block proposal messages submitted to signers stackerdb` with `/// Check if block should be rejected based on sortition state`.

4. In `stacks-signer/src/signerdb.rs`, the patch replaces `impl From<BlockProposal> for BlockInfo {` with `/// The miner pubkey that proposed this block`.

## Project Context

The changed code sits primarily in `stacks-signer/src/v0`, `stacks-signer/src`, which anchors the finding in the `consensus` area of the project. Historical context from `stacks-signer/src/chainstate.rs`, `stacks-signer/src/runloop.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stacks-signer/src/chainstate.rs`, `stacks-signer/src/runloop.rs`. The strongest project-level identifiers around this patch are `block`, `sortition_state`, `block_info`, and `miner_pubkey`. Nearby tests or test-like files include `stacks-signer/src/tests/chainstate.rs`, `stacks-signer/src/tests/mod.rs`.

## Before/After Behavior

Before the patch, the provided approval path evidence shows `handle_block_validate_ok` looking up queued `BlockInfo` and proceeding toward `mark_locally_accepted(false)` without a shown fresh sortition-state recheck at that point. Proposal-time validation existed separately. After the patch, both proposal handling and queued approval handling use `check_block_against_sortition_state(...)`; during approval handling, a block that is invalid under the current sortition view is locally rejected instead of accepted. `BlockInfo` now stores `miner_pubkey` so the later recheck can use the original proposer context.

# Root Cause

A validation result queued under one sortition view could be consumed later without the supplied evidence showing that the block was revalidated against the current sortition view immediately before local acceptance. The queued record also lacked the proposer public key needed for that later binding check.

## Walkthrough

1. A block proposal is initially checked against a sortition view in the signer path.

2. The validation result can later be processed by `handle_block_validate_ok` after lookup by `signer_signature_hash`.

3. The patch adds a shared `check_block_against_sortition_state` helper for deciding whether the current sortition view rejects the block.

4. The approval path now calls that helper with `block_info.block` and `block_info.miner_pubkey` before local acceptance.

5. If the current view rejects the block, the code overrides the approval with a rejection and marks the block locally rejected.

6. `BlockInfo` now persists `miner_pubkey` so queued validation processing can repeat the check with proposer context.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stacks-signer/src/v0/signer.rs | 318 | introduces shared check_block_against_sortition_state helper for rejecting blocks invalid under the current sortition view |
| stacks-signer/src/v0/signer.rs | 469 | uses the shared sortition-state validation when initially handling a block proposal |
| stacks-signer/src/v0/signer.rs | 560 | rechecks queued validation approval against current sortition state in handle_block_validate_ok |
| stacks-signer/src/v0/signer.rs | 598 | overrides a validation approval with local rejection when the sortition state has changed and the block is no longer valid |
| stacks-signer/src/signerdb.rs | 159 | stores the proposing miner public key in BlockInfo so later validation-queue processing can revalidate proposer binding |

## Code Snippets

## Snippet 1

Context: `stacks-signer/src/v0/signer.rs:598` (changes signature or replay validation logic)

Before
```rust
}
        };
        if let Err(e) = block_info.mark_locally_accepted(false) {
            if !block_info.has_reached_consensus() {
                warn!("{self}: Failed to mark block as locally accepted: {e:?}",);
                return None;
            }
            block_info.signed_self.get_or_insert(get_epoch_time_secs());
```
After
```rust
}
        };
        if let Some(block_response) = self.check_block_against_sortition_state(
            stacks_client,
            sortition_state,
            &block_info.block,
            &block_info.miner_pubkey,
        ) {
```

## Snippet 2

Context: `stacks-signer/src/v0/signer.rs:475` (changes a sensitive control or state-update path)

Before
```rust
// Check if proposal can be rejected now if not valid against sortition view
        let block_response = if let Some(sortition_state) = sortition_state {
            match sortition_state.check_proposal(
                stacks_client,
                &mut self.signer_db,
                &block_proposal.block,
                miner_pubkey,
```
After
```rust
// Check if proposal can be rejected now if not valid against sortition view
        let block_response = self.check_block_against_sortition_state(
            stacks_client,
            sortition_state,
            &block_proposal.block,
            miner_pubkey,
        );
```

## Snippet 3

Context: `stacks-signer/src/v0/signer.rs:318` (changes a sensitive control or state-update path)

Before
```rust
}

    /// Handle block proposal messages submitted to signers stackerdb
    fn handle_block_proposal(
```
After
```rust
}

    /// Check if block should be rejected based on sortition state
    /// Will return a BlockResponse::Rejection if the block is invalid, none otherwise.
    fn check_block_against_sortition_state(
        &mut self,
        stacks_client: &StacksClient,
        sortition_state: &mut Option<SortitionsView>,
```

## Snippet 4

Context: `stacks-signer/src/signerdb.rs:159` (changes a sensitive control or state-update path)

Before
```rust
/// The block state relative to the signer's view of the stacks blockchain
    pub state: BlockState,
    /// Extra data specific to v0, v1, etc.
    pub ext: ExtraBlockInfo,
}

impl From<BlockProposal> for BlockInfo {
    fn from(value: BlockProposal) -> Self {
```
After
```rust
/// The block state relative to the signer's view of the stacks blockchain
    pub state: BlockState,
    /// The miner pubkey that proposed this block
    pub miner_pubkey: Secp256k1PublicKey,
    /// Extra data specific to v0, v1, etc.
    pub ext: ExtraBlockInfo,
}
```

# Fix Pattern

Revalidate queued consensus approval against current chain/sortition state immediately before local acceptance, and persist the metadata needed to repeat the validation later.

## How It Was Fixed

The patch introduced `check_block_against_sortition_state` in `stacks-signer/src/v0/signer.rs`, routed proposal-time validation through it, and added the same check to `handle_block_validate_ok` before local acceptance. It also added `miner_pubkey` to `BlockInfo` in `stacks-signer/src/signerdb.rs` so approval-time revalidation can use the proposer public key.

# Why It Matters

1. Prevents stale queued approval from bypassing a current sortition-view check.

2. Keeps signer local acceptance aligned with the latest signer view.

3. Preserves proposer public key context across validation queue processing.

4. Relevant to consensus-signing correctness, though final exploitability is not proven by the supplied evidence.

# Evidence Notes

Grounded evidence is limited to the provided hunks in `stacks-signer/src/v0/signer.rs` and `stacks-signer/src/signerdb.rs`. The commit subject explicitly describes a validation queue race involving sortition view changes. The code evidence supports stale-view revalidation before local acceptance. It does not prove attacker control, reliable exploitability, signature forgery, replay, private key compromise, or final chain compromise. Protocol security invariant: A signer should not locally accept or sign a Nakamoto block based only on a validation result produced under an older sortition view; approval should be rechecked against the signer's current sortition view and original proposer/miner public key context. Verification notes: The patch does not prove that an attacker could reliably trigger the race. The patch does not prove that stale approval would necessarily finalize an invalid block on chain. The patch does not show private key compromise or signature forgery. The patch does not establish a replay vulnerability beyond stale queued validation state. The evidence is limited to signer-side validation and local acceptance/rejection behavior. Downgraded confidence from high to medium because exploitability and final consensus impact are not demonstrated. Rejected the heuristic replay/signature-validation classification as unsupported. Kept security relevance because the changed path controls signer local acceptance/rejection in a consensus validation flow. Treated the new helper as support code, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `stale-consensus-validation-race`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `validator-ops, consensus, race-condition, stale-state-validation, signer-validation`

The supplied evidence supports a security-hardening classification, not a concrete security-fix. The patch rechecks queued signer validation approvals against the current sortition view before local acceptance and preserves the miner public key needed for that later check. Because this path can lead to signer acceptance and signing decisions in consensus code, the change tightens security-sensitive behavior. However, the evidence does not prove attacker control, replay, signature forgery, or final on-chain compromise, so the original replay/signature-validation framing is too strong.

## Security Evidence

1. Commit subject explicitly describes a validation queue race involving sortition view changes between submission and approval.
2. Approval handling now calls check_block_against_sortition_state before local acceptance of a queued block.
3. If the current sortition state rejects the block, the approval path overrides the response and marks the block locally rejected.
4. BlockInfo now stores miner_pubkey so queued validation can be rechecked with proposer context.
5. Nearby code shows accepted validation can produce a signed BlockResponse, making this a security-sensitive signer path.

## Missing Evidence

1. No proof that an attacker can reliably trigger or exploit the race.
2. No proof that stale local acceptance necessarily finalizes an invalid block on chain.
3. No evidence of signature forgery, private key compromise, or request replay.
4. No full test evidence or exploit scenario demonstrating concrete security impact.

## Claim Boundaries

1. Keep only as consensus signer validation hardening against stale sortition-state approvals.
2. Do not claim signature forgery, private key exposure, or replay without additional evidence.
3. Do not claim guaranteed invalid block finalization from the supplied patch alone.
4. The supported impact is reduced risk to consensus integrity, not proven chain compromise.
