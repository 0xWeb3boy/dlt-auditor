---
case_id: case_20220715_da264c340e
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2022-07-15
source_refs:
  - git:da264c340ed6cd4695c22d04eea92dc3fc46ebe7
  - "crates/sui-core/src/safe_client.rs:440"
  - "crates/sui-core/src/safe_client.rs:418"
  - "crates/sui-types/src/messages_checkpoint.rs:120"
  - "crates/sui-types/src/messages_checkpoint.rs:506"
bug_class: checkpoint-response-verification
impact_type:
  - checkpoint-integrity
tags:
  - blockchain-core
  - checkpoint
  - response-verification
  - committee-signature
  - remote-authority
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best classified as checkpoint response verification hardening. It adds centralized `CheckpointResponse::verify(&Committee)` and calls it before request-specific validation in the safe client, and it adds a guard for missing requested detail on signed or certified past checkpoints. The evidence supports security relevance for checkpoint integrity, but not a confirmed exploitable vulnerability.

## Observed Patch Facts

1. In `crates/sui-core/src/safe_client.rs`, the patch replaces `self.verify_authenticated_checkpoint(Some(seq), past)?;` with `match past {`.

2. In `crates/sui-core/src/safe_client.rs`, the patch replaces `match req_type {` with `let detail = request.detail;`.

3. In `crates/sui-types/src/messages_checkpoint.rs`, the patch replaces `#[derive(Clone, Debug, Serialize, Deserialize)]` with `impl CheckpointResponse {`.

4. In `crates/sui-types/src/messages_checkpoint.rs`, the patch replaces `assert!(proposal.verify_with_transactions(&contents).is_err());` with `assert!(proposal.verify(&committee, Some(&contents)).is_err());`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, `crates/sui-types/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-core/src/authority.rs`, `crates/sui-types/src/messages.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/checkpoints/mod.rs`, `crates/sui-core/src/authority_active/checkpoint_driver/mod.rs`. The strongest project-level identifiers around this patch are `AuthorityCheckpointInfo::Proposal`, `proposal`, `verify`, and `current`. Nearby tests or test-like files include `crates/sui-core/src/checkpoints/tests/checkpoint_tests.rs`, `crates/sui-core/src/epoch/tests/reconfiguration_tests.rs`.

## Before/After Behavior

Before the patch, the shown `PastCheckpoint(seq)` path accepted a `Past` response after `verify_authenticated_checkpoint(Some(seq), past)` and the supplied evidence does not show a centralized response-level verification step. After the patch, `safe_client.rs` captures the request detail flag, receives the remote response, runs `resp.verify(&self.committee)?`, and then validates response shape and request consistency. For past signed or certified checkpoints, missing requested detail is rejected as Byzantine suspicion.

# Root Cause

Checkpoint response validation was split across request-specific handling and did not clearly bind all response authentication, committee verification, requested type/sequence, and optional contents/detail expectations at the response boundary.

## Walkthrough

1. A safe client sends a checkpoint request to a remote authority.

2. The remote authority returns `CheckpointResponse` with `AuthorityCheckpointInfo` and optional `CheckpointContents` detail.

3. The patch adds `CheckpointResponse::verify(&Committee)` in `messages_checkpoint.rs`.

4. The safe client now invokes that verifier immediately after receiving the response.

5. For proposal responses, verification checks the current proposal with the response detail when present and verifies the previous checkpoint without applying that detail to it.

6. For past checkpoint responses, the client still requires a `Past` response and now rejects signed or certified checkpoints that omit requested detail.

7. Tests were updated to verify committee-bound proposal checks, mismatched contents failure, and modified summary failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/safe_client.rs | 416 | Remote authority checkpoint response handling; now verifies signatures before validating request-specific response shape. |
| crates/sui-core/src/safe_client.rs | 440 | Past checkpoint response validation; enforces detail presence when detail was requested and the checkpoint is signed or certified. |
| crates/sui-types/src/messages_checkpoint.rs | 120 | CheckpointResponse verification; checks checkpoint/proposal authentication against the committee and binds optional detail to the current proposal. |
| crates/sui-types/src/messages_checkpoint.rs | 490 | Regression tests for signed proposal verification against committee, contents, and modified summary data. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/safe_client.rs:440` (changes a sensitive control or state-update path)

Before
```rust
CheckpointRequestType::PastCheckpoint(seq) => {
                if let AuthorityCheckpointInfo::Past(past) = &resp.info {
                    self.verify_authenticated_checkpoint(Some(seq), past)?;
                    Ok(resp)
                } else {
```
After
```rust
CheckpointRequestType::PastCheckpoint(seq) => {
                if let AuthorityCheckpointInfo::Past(past) = &resp.info {
                    match past {
                        AuthenticatedCheckpoint::Signed(_)
                        | AuthenticatedCheckpoint::Certified(_) => {
                            if detail && resp.detail.is_none() {
                                // peer has the checkpoint, but refused to give us the contents.
                                // (For AuthorityCheckpointInfo::Proposal, contents are not
```

## Snippet 2

Context: `crates/sui-core/src/safe_client.rs:418` (changes signature or replay validation logic)

Before
```rust
request: CheckpointRequest,
    ) -> Result<CheckpointResponse, SuiError> {
        let req_type = request.request_type.clone();

        let resp = self.authority_client.handle_checkpoint(request).await?;

        match req_type {
            CheckpointRequestType::LatestCheckpointProposal => {
```
After
```rust
request: CheckpointRequest,
    ) -> Result<CheckpointResponse, SuiError> {
        let detail = request.detail;
        let req_type = request.request_type.clone();

        let resp = self.authority_client.handle_checkpoint(request).await?;

        // Verify signatures
```

## Snippet 3

Context: `crates/sui-types/src/messages_checkpoint.rs:120` (changes signature or replay validation logic)

Before
```rust
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum AuthorityCheckpointInfo {
```
After
```rust
}

impl CheckpointResponse {
    pub fn verify(&self, committee: &Committee) -> SuiResult {
        match &self.info {
            AuthorityCheckpointInfo::Success => Ok(()),
            AuthorityCheckpointInfo::Proposal { current, previous } => {
                if let Some(current) = current {
```

## Snippet 4

Context: `crates/sui-types/src/messages_checkpoint.rs:506` (changes signature or replay validation logic)

Before
```rust
transactions: [ExecutionDigests::random()].into_iter().collect(),
        };
        assert!(proposal.verify_with_transactions(&contents).is_err());

        // Modify the proposal, and observe the signature fail
        proposal.summary.sequence_number = 2;
        assert!(proposal.verify().is_err());
    }
```
After
```rust
transactions: [ExecutionDigests::random()].into_iter().collect(),
        };
        assert!(proposal.verify(&committee, Some(&contents)).is_err());

        // Modify the proposal, and observe the signature fail
        proposal.summary.sequence_number = 2;
        assert!(proposal.verify(&committee, None).is_err());
    }
```

# Fix Pattern

Centralize response authentication at the remote-response trust boundary, then separately enforce request/response consistency and detail availability rules.

## How It Was Fixed

The patch introduced `CheckpointResponse::verify(&self, committee)` and called it from `safe_client.rs` before request-specific checks. It updated checkpoint/proposal verification to use the expected committee and optional contents, and added explicit rejection when a signed or certified past checkpoint response lacks requested detail.

# Why It Matters

1. Checkpoint data comes from remote authorities.

2. Committee and signature checks are integrity-critical for checkpoint synchronization.

3. Requested contents should not be silently absent when an authority claims to have an available signed or certified checkpoint.

4. The evidence does not prove fund loss, transaction forgery, durable state corruption, or consensus finality failure.

# Evidence Notes

Supported by changes in `crates/sui-core/src/safe_client.rs` around remote checkpoint handling and past-checkpoint detail checks, and by `crates/sui-types/src/messages_checkpoint.rs` adding `CheckpointResponse::verify`. The commit title and tests support verification hardening. Claims of confirmed exploitability, state corruption, or consensus compromise are not established by the provided evidence. Confidence is downgraded from high to medium because the security impact is plausible and grounded, but the vulnerability thesis is not demonstrated beyond hardening of a sensitive path. Protocol security invariant: Remote checkpoint responses should only be accepted after their signed or certified checkpoint/proposal data verifies against the expected committee, matches the requested checkpoint type and sequence, and satisfies requested contents/detail expectations when the peer claims the checkpoint is available. Verification notes: The patch does not by itself prove remote exploitability. The evidence does not show that invalid checkpoints were committed to durable state before this fix. The evidence does not establish fund loss, transaction forgery, or consensus finality failure. Some changes relax handling for unavailable proposal detail, so the fix is not a blanket tightening of all checkpoint response rules. No external exploit scenario is shown in the supplied evidence. No durable invalid checkpoint acceptance is shown. Regression tests cover signature/content mismatch behavior, not an end-to-end attack. Some behavior is relaxed for unavailable latest proposal detail, so this is not a blanket tightening of all checkpoint checks. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `checkpoint-response-verification`
Final impact type: `checkpoint-integrity`
Final tags: `blockchain-core, checkpoint, response-verification, committee-signature, remote-authority`

The supplied patch evidence supports retaining this as security hardening: checkpoint responses from remote authorities are now centrally verified against the committee before request-specific acceptance, and signed/certified past checkpoints must include requested detail. This is security-sensitive integrity behavior, but the evidence does not prove a concrete exploitable flaw, durable state corruption, or consensus compromise. The original state-corruption framing is too strong for the supplied patch alone.

## Security Evidence

1. Adds CheckpointResponse::verify(&Committee) for response-level verification of checkpoint/proposal data.
2. safe_client now calls resp.verify(&self.committee)? immediately after receiving a remote checkpoint response.
3. Proposal verification binds current proposal verification to optional detail and verifies the previous checkpoint separately.
4. Past signed or certified checkpoint responses now reject missing detail when detail was requested as ByzantineAuthoritySuspicion.
5. Tests cover committee-bound proposal verification, mismatched contents failure, and modified summary signature failure.

## Missing Evidence

1. No proof that invalid checkpoint responses were previously accepted into durable state.
2. No demonstrated exploit path, transaction forgery, fund loss, or consensus finality failure.
3. No end-to-end regression showing an attacker-controlled authority causing state corruption.
4. Commit notes include some relaxed handling, so the patch is not purely a tightening of every checkpoint rule.

## Claim Boundaries

1. Classify as checkpoint response verification hardening, not a confirmed vulnerability fix.
2. Do not claim proven state corruption or consensus compromise from the supplied evidence.
3. Do not infer fund loss or transaction forgery impact.
4. Security relevance is limited to remote checkpoint response integrity and committee/signature validation behavior.
