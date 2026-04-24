---
case_id: case_20220720_ede61fb385
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2022-07-20
source_refs:
  - git:ede61fb385d933e5e7eb11562efbac7393ffce6f
  - "crates/sui-core/src/epoch/reconfiguration.rs:64"
  - "crates/sui-core/src/epoch/reconfiguration.rs:47"
  - "crates/sui-core/src/authority.rs:1113"
  - "crates/sui-core/src/authority/authority_store.rs:1452"
bug_class: authenticated-epoch-storage-hardening
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - infrastructure
  - consensus
  - validator
  - epoch
  - committee
  - signature
  - checkpoint
  - authenticated-storage
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to add an authenticated/signed epoch storage path and adjust epoch reconfiguration bookkeeping, but the evidence does not establish a vulnerability. The strongest grounded change is replacing local new-epoch metadata insertion with a `sign_new_epoch` flow that receives the current epoch, next committee, authority identity, signer, and last checkpoint. That is security-relevant code, but no exploit path, attacker control, or concrete invariant failure is shown.

## Observed Patch Facts

1. In `crates/sui-core/src/epoch/reconfiguration.rs`, the patch replaces `let epoch = self.state.committee.load().epoch();` with `let epoch = self.state.committee.load().epoch;`.

2. In `crates/sui-core/src/epoch/reconfiguration.rs`, the patch replaces `self.state.halted.store(true, Ordering::SeqCst);` with `self.state.halt_validator();`.

3. In `crates/sui-core/src/authority.rs`, the patch replaces `pub(crate) fn insert_new_epoch_info(&self, new_committee: &Committee) -> SuiResult {` with `pub(crate) fn sign_new_epoch_and_update_committee(`.

4. In `crates/sui-core/src/authority/authority_store.rs`, the patch adds `// Epoch related functions`.

## Project Context

The changed code sits primarily in `crates/sui-core/src/epoch`, `crates/sui-core/src`, `crates/sui-core`, which anchors the finding in the `storage` area of the project. Historical context from `crates/sui-core/src/gateway_state.rs`, `crates/sui-core/src/authority_client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/gateway_state.rs`, `crates/sui-core/src/authority_client.rs`. The strongest project-level identifiers around this patch are `epoch`, `state`, `Ordering::SeqCst`, and `committee`. Nearby tests or test-like files include `crates/sui-core/src/epoch/tests/reconfiguration_tests.rs`, `crates/sui-core/src/unit_tests/batch_tests.rs`.

## Before/After Behavior

Before the patch, `AuthorityState` had an `insert_new_epoch_info(&Committee)` path that checked epoch ordering and inserted `EpochInfoLocals` with `validator_halted: true`. After the patch, the authority path calls `sign_new_epoch_and_update_committee`, which delegates to `database.sign_new_epoch` with epoch, next committee, authority identity, signer, and last checkpoint. Reconfiguration code also uses `halt_validator()` and carries checkpoint completion context when finishing an epoch change.

# Root Cause

Not established. The draft infers that prior epoch transition metadata was insufficiently authenticated, but the supplied evidence does not prove that this caused an exploitable or externally triggerable state transition flaw.

## Walkthrough

1. Epoch reconfiguration checks checkpoint readiness before starting an epoch change.

2. The patch replaces direct halted-flag mutation with `halt_validator()`, which may be cleanup or centralization.

3. The finish path now derives a `last_checkpoint` from checkpoint state before completing the transition.

4. The authority-level API changes from inserting new epoch info to signing the new epoch and updating the committee.

5. The new store path accepts signing material and checkpoint context, suggesting authenticated persistence of epoch information.

6. The missing piece is evidence that the old insertion path was reachable by an attacker or could cause an invalid committee transition.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/epoch/reconfiguration.rs | 37 | starts epoch change, checks checkpoint readiness, halts validator before draining pending batches |
| crates/sui-core/src/epoch/reconfiguration.rs | 64 | finishes epoch change using the last checkpoint and updated committee state |
| crates/sui-core/src/authority.rs | 1113 | replaces direct epoch-info insertion with signing of the new epoch and committee update |
| crates/sui-core/src/authority/authority_store.rs | 1452 | adds persistent store path for signed/authenticated new epoch data |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/epoch/reconfiguration.rs:64` (changes a consensus- or validator-sensitive branch)

Before
```rust
/// a validator that belongs to the committee of the next epoch.
    pub async fn finish_epoch_change(&self) -> SuiResult {
        let epoch = self.state.committee.load().epoch();
        info!(epoch=?epoch, "Finishing epoch change");
        assert!(
            self.state.halted.load(Ordering::SeqCst),
            "finish_epoch_change called when validator is not halted",
        );
```
After
```rust
/// a validator that belongs to the committee of the next epoch.
    pub async fn finish_epoch_change(&self) -> SuiResult {
        let epoch = self.state.committee.load().epoch;
        info!(?epoch, "Finishing epoch change");
        let last_checkpoint = if let Some(checkpoints) = &self.state.checkpoints {
            let mut checkpoints = checkpoints.lock();
            assert!(
```

## Snippet 2

Context: `crates/sui-core/src/epoch/reconfiguration.rs:47` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

        self.state.halted.store(true, Ordering::SeqCst);
        info!(epoch=?epoch, "Validator halted for epoch change");
        while !self.state.batch_notifier.ticket_drained() {
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
        info!(epoch=?epoch, "Epoch change started");
```
After
```rust
}

        self.state.halt_validator();
        info!(?epoch, "Validator halted for epoch change");
        // TODO: The following doesn't work: we also need to make sure that the transactions
        // all have been included in a batch (and hence will be included in the next checkpoint
        // proposal).
        // TODO: Use a conditional variable pattern instead of while + sleep.
```

## Snippet 3

Context: `crates/sui-core/src/authority.rs:1113` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    pub(crate) fn insert_new_epoch_info(&self, new_committee: &Committee) -> SuiResult {
        let current_epoch_info = self.database.get_last_epoch_info()?;
        fp_ensure!(
            current_epoch_info.committee.epoch <= new_committee.epoch,
            SuiError::InconsistentEpochState {
                error: "Trying to insert an old epoch entry".to_owned()
```
After
```rust
}

    pub(crate) fn sign_new_epoch_and_update_committee(
        &self,
        next_epoch_committee: Committee,
        last_checkpoint: CheckpointSequenceNumber,
    ) -> SuiResult {
        self.database.sign_new_epoch(
```

## Snippet 4

Context: `crates/sui-core/src/authority/authority_store.rs:1452` (changes signature or replay validation logic)

Before
```rust
Ok(result)
    }
}
```
After
```rust
Ok(result)
    }

    // Epoch related functions

    /// This function should be called at the end of the epoch identified by `epoch`,
    /// and after this call, we expect that the node's committee has changed
    /// to `next_epoch_committee`.
```

# Fix Pattern

Replace plain local epoch metadata insertion with a signed/authenticated epoch persistence API, while threading checkpoint context through the transition path.

## How It Was Fixed

The patch introduces `sign_new_epoch_and_update_committee` and `database.sign_new_epoch`, passing the current epoch, next committee, authority name, signer, and last checkpoint. It also centralizes validator halt handling through `halt_validator()`.

# Why It Matters

1. Epoch and committee state are consensus-sensitive.

2. Signed epoch records can strengthen transition integrity.

3. The patch may be security hardening.

4. The evidence does not show attacker control or concrete exploitability.

5. This should not be treated as a confirmed vulnerability fix.

# Evidence Notes

Grounded evidence supports an authenticated epoch storage refactor/hardening: `authority.rs` replaces `insert_new_epoch_info` with `sign_new_epoch_and_update_committee`, and `authority_store.rs` adds `sign_new_epoch`. Supporting reconfiguration changes involve checkpoint readiness, last checkpoint context, and validator halt handling. Unsupported claims include state corruption, exploitable missing authentication, remote forgery, asset impact, or privilege escalation. Protocol security invariant: Epoch and committee transitions should be authenticated and tied to the correct checkpoint/epoch context, but the provided evidence does not establish that the previous code violated this invariant in an attacker-relevant way. Verification notes: No direct remote exploit path is shown by the provided patch evidence. No proof is shown that an attacker could forge or inject a committee change before this patch. No asset theft, transaction forgery, or privilege escalation impact is established. The halt_validator change may be correctness-related, but the security-relevant part is the authenticated epoch storage path. The evidence supports likely security hardening, not a confirmed vulnerability advisory. No direct exploit path is provided. No attacker-controlled input path is shown. No proof is shown that a malicious or stale committee could be inserted before the patch. No regression test evidence is quoted showing the prior behavior failed a security invariant. Classify as unclear security relevance, not a security corpus entry. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authenticated-epoch-storage-hardening`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `infrastructure, consensus, validator, epoch, committee, signature, checkpoint, authenticated-storage`

The supplied evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The patch moves epoch transition persistence from a plain local insertion path to a signed/authenticated epoch flow that includes authority identity, signing material, next committee, current epoch, and last checkpoint context in a validator/committee transition path. However, the evidence does not prove that the old path was attacker-reachable or exploitable.

## Security Evidence

1. Commit subject explicitly says "Add authenticated epoch".
2. AuthorityState replaces insert_new_epoch_info with sign_new_epoch_and_update_committee.
3. New store path signs new epoch data using authority identity and signer material.
4. Epoch transition logic threads last_checkpoint into the committee update flow.
5. Changes affect validator epoch reconfiguration and committee state, which are consensus-sensitive.

## Missing Evidence

1. No direct exploit path is shown.
2. No attacker-controlled input path to the old insertion behavior is shown.
3. No proof that a stale, forged, or malicious committee could previously be persisted.
4. No regression test excerpt demonstrates prior acceptance of unauthenticated epoch state.
5. No advisory or vulnerability statement is provided.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Do not claim remote exploitation, privilege escalation, asset theft, or transaction forgery.
3. Do not claim proven state corruption from the supplied patch alone.
4. The supported claim is authenticated epoch/committee transition persistence hardening.
