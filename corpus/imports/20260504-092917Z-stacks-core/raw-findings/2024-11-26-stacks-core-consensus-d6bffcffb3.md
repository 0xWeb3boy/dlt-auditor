---
case_id: case_20241126_d6bffcffb3
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2024-11-26
source_refs:
  - git:d6bffcffb35d433c1488d4aadc69c73e0b9f35a5
  - "stacks-signer/src/client/stacks_client.rs:301"
  - "stacks-signer/src/signerdb.rs:614"
  - "stacks-signer/src/v0/signer.rs:661"
  - "stacks-signer/src/signerdb.rs:1330"
bug_class: stale-state-validation
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - validator-ops
  - consensus
  - signer-state
  - stale-validation
  - block-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes signer post-validation behavior so a successful block validation response is rechecked against current signer DB state, using a new helper that selects the highest locally or globally accepted signer block. This is plausibly consensus-relevant correctness or hardening work, but the provided evidence does not prove a concrete vulnerability, exploit path, or security impact.

## Observed Patch Facts

1. In `stacks-signer/src/client/stacks_client.rs`, the patch replaces `/// Submit the block proposal to the stacks node. The block will be validated and ret...` with `#[cfg(any(test, feature = "testing"))]`.

2. In `stacks-signer/src/signerdb.rs`, the patch replaces `/// Return the last accepted block in a tenure (identified by its consensus hash).` with `/// Return the last accepted block the signer (highest stacks height). It will tie br...`.

3. In `stacks-signer/src/v0/signer.rs`, the patch replaces `if let Some(block_response) = self.check_block_against_sortition_state(` with `if let Some(block_response) = self.check_block_against_signer_db_state(&block_info.bl...`.

4. In `stacks-signer/src/signerdb.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `stacks-signer/src/client`, `stacks-signer/src`, `stacks-signer/src/v0`, which anchors the finding in the `consensus` area of the project. Historical context from `stacks-signer/src/monitor_signers.rs`, `stacks-signer/src/runloop.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stacks-signer/src/runloop.rs`, `stacks-signer/src/monitor_signers.rs`. The strongest project-level identifiers around this patch are `block`, `block_info`, `signer`, and `unwrap`. Nearby tests or test-like files include `stacks-signer/src/tests/chainstate.rs`, `stacks-signer/src/tests/mod.rs`.

## Before/After Behavior

Before the patch, the observed successful block-validation path rechecked against sortition state after BlockValidateOk. After the patch, the path checks current signer DB state via check_block_against_signer_db_state and can override the validation response by locally rejecting the block. The new get_signer_last_accepted_block helper queries accepted blocks and orders by height with deterministic tie-breaking. A test-only stall hook was added to support timing-sensitive tests.

# Root Cause

The grounded issue is that asynchronous block-validation success handling could rely on state that was no longer the most relevant local signer state by the time the response was processed. The evidence supports a stale local-state or reduced-height-check correction, not a proven cryptographic, authorization, or remotely exploitable flaw.

## Walkthrough

1. A block validation success response is handled in handle_block_validate_ok.

2. The signer looks up the corresponding block_info by signer_signature_hash.

3. The prior observed guard checked the block against changed sortition state.

4. The patched path checks the block against current signer DB state instead.

5. If signer DB state indicates the block should no longer be accepted, the handler overrides the successful validation response.

6. The block may then be marked locally rejected, unless it has already reached consensus.

7. SignerDb now has get_signer_last_accepted_block to select the highest locally or globally accepted block.

8. Added tests cover last-accepted-block selection and controlled validation timing.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stacks-signer/src/v0/signer.rs | 624 | handles successful block validation responses and revalidates the proposal against current signer DB state before accepting it |
| stacks-signer/src/v0/signer.rs | 661 | overrides a previously valid block response when signer DB state has changed |
| stacks-signer/src/signerdb.rs | 614 | queries the highest locally or globally accepted signer block for reduced height comparison |
| stacks-signer/src/client/stacks_client.rs | 301 | test-only stall hook for block validation submission timing |
| stacks-signer/src/signerdb.rs | 1330 | unit coverage for selecting the signer's last accepted block |

## Code Snippets

## Snippet 1

Context: `stacks-signer/src/client/stacks_client.rs:301` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    /// Submit the block proposal to the stacks node. The block will be validated and returned via the HTTP endpoint for Block events.
    pub fn submit_block_for_validation(&self, block: NakamotoBlock) -> Result<(), ClientError> {
        debug!("stacks_node_client: Submitting block for validation...";
            "signer_sighash" => %block.header.signer_signature_hash(),
```
After
```rust
}

    #[cfg(any(test, feature = "testing"))]
    fn test_stall_block_validation_submission() {
        use crate::v0::signer::TEST_STALL_BLOCK_VALIDATION_SUBMISSION;

        if *TEST_STALL_BLOCK_VALIDATION_SUBMISSION.lock().unwrap() == Some(true) {
            // Do an extra check just so we don't log EVERY time.
```

## Snippet 2

Context: `stacks-signer/src/signerdb.rs:614` (changes bounds, limits, or capacity handling)

Before
```rust
}

    /// Return the last accepted block in a tenure (identified by its consensus hash).
    pub fn get_last_accepted_block(
```
After
```rust
}

    /// Return the last accepted block the signer (highest stacks height). It will tie break a match based on which was more recently signed.
    pub fn get_signer_last_accepted_block(&self) -> Result<Option<BlockInfo>, DBError> {
        let query = "SELECT block_info FROM blocks WHERE json_extract(block_info, '$.state') IN (?1, ?2) ORDER BY stacks_height DESC, json_extract(block_info, '$.signed_group') DESC, json_extract(block_info, '$.signed_self') DESC LIMIT 1";
        let args = params![
            &BlockState::GloballyAccepted.to_string(),
            &BlockState::LocallyAccepted.to_string()
```

## Snippet 3

Context: `stacks-signer/src/v0/signer.rs:661` (changes a sensitive control or state-update path)

Before
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
After
```rust
}
        };

        if let Some(block_response) = self.check_block_against_signer_db_state(&block_info.block) {
            // The signer db state has changed. We no longer view this block as valid. Override the validation response.
            if let Err(e) = block_info.mark_locally_rejected() {
                if !block_info.has_reached_consensus() {
```

## Snippet 4

Context: `stacks-signer/src/signerdb.rs:1330` (changes persisted or aggregate state handling)

Before
```rust
assert_eq!(db.get_canonical_tip().unwrap().unwrap(), block_info_2);
    }
}
```
After
```rust
assert_eq!(db.get_canonical_tip().unwrap().unwrap(), block_info_2);
    }

    #[test]
    fn signer_last_accepted_block() {
        let db_path = tmp_db_path();
        let mut db = SignerDb::new(db_path).expect("Failed to create signer db");
```

# Fix Pattern

Revalidate asynchronous validation success results against the latest local persisted signer state before accepting them.

## How It Was Fixed

The patch added SignerDb::get_signer_last_accepted_block, changed the post-validation success handler to call check_block_against_signer_db_state, and added tests plus a cfg(test/testing) stall hook to exercise timing-sensitive behavior.

# Why It Matters

1. Block validation responses can arrive after local signer state has changed.

2. Signer decisions depend on current accepted-block state, not only earlier validation context.

3. The change may prevent stale acceptance decisions, but supplied evidence does not prove security exploitability.

4. The test-only stall hook is support code, not the root cause or production mitigation.

# Evidence Notes

Evidence is limited to selected hunks in stacks-signer/src/v0/signer.rs, stacks-signer/src/signerdb.rs, tests, and a test-only client hook. The patch touches consensus-adjacent signer logic, but there is no provided proof of attacker control, invalid block finalization, chain split, fund loss, denial of service, or other concrete security impact. Therefore the mapper's likely/security-hardening classification is stronger than the evidence supports. Protocol security invariant: A signer should not continue accepting a block-validation success result if current signer DB state now indicates that the block is stale or inconsistent with the signer's latest accepted block. The supplied evidence shows this invariant being enforced more directly, but does not establish a security vulnerability or attacker-triggered violation. Verification notes: No concrete attacker-controlled input path is proven by the supplied patch evidence. No proof is shown that invalid consensus blocks could be finalized before the patch. The test-only stall hook is not itself a production security mechanism. The patch supports stale-state or height-regression hardening, not a demonstrated cryptographic failure. The evidence does not prove chain split, fund loss, or denial of service impact. No external context or file inspection was used. The security thesis is not established by the supplied evidence alone. Classified as unclear and excluded from the security corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `stale-state-validation`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `validator-ops, consensus, signer-state, stale-validation, block-validation`

The evidence does not prove a concrete exploitable vulnerability, but it does show a consensus-adjacent signer path being tightened so a previously successful block validation response can be overridden when current signer DB state makes the block no longer valid. In a signer/validator subsystem, rechecking asynchronous validation results against latest accepted local state is security-relevant hardening rather than ordinary cleanup or maintenance.

## Security Evidence

1. Post-validation success handling now calls check_block_against_signer_db_state before accepting the result.
2. The added comment states that if signer DB state changed, the signer no longer views the block as valid and overrides the validation response.
3. The handler can mark the block locally rejected when the current signer DB state invalidates it.
4. SignerDb adds get_signer_last_accepted_block to select the highest locally or globally accepted block with deterministic tie-breaking.
5. Tests were added around last accepted block selection and timing-sensitive validation behavior.

## Missing Evidence

1. No proof that an attacker could trigger the stale validation window.
2. No demonstrated invalid block finalization, chain split, fund loss, or denial-of-service impact.
3. No advisory, vulnerability identifier, or commit message explicitly describing a security flaw.
4. The evidence does not prove a cryptographic or signature verification failure.

## Claim Boundaries

1. Treat as security hardening of consensus/signer state validation, not a confirmed exploitable security fix.
2. Do not claim state corruption was demonstrated by the patch alone.
3. Do not claim remote exploitability or attacker control from the supplied evidence.
4. The test-only stall hook is supporting regression infrastructure, not the production mitigation.
