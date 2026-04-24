---
case_id: case_20250718_5dce17a946
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2025-07-18
source_refs:
  - git:5dce17a94698e2f2381c810c5b43080fd0b66a02
  - "crates/sui-core/src/consensus_handler.rs:391"
  - "crates/sui-core/src/consensus_handler.rs:368"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:4383"
  - "crates/sui-protocol-config/src/lib.rs:750"
bug_class: consensus-state-commitment-gap
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - infrastructure
  - consensus
  - validator
  - state-integrity
  - state-commitment
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an `IndirectStateObserver` and conditionally folds observed indirect state into the additional consensus digest recorded in the consensus commit prologue. The supplied evidence supports a consensus/state-integrity hardening change aimed at earlier detection of validator state divergence, but it does not establish an exploitable vulnerability or concrete attacker path.

## Observed Patch Facts

1. In `crates/sui-core/src/consensus_handler.rs`, the patch replaces `#[test]` with `#[derive(Default)]`.

2. In `crates/sui-core/src/consensus_handler.rs`, the patch replaces `self.consensus_commit_prologue_v4_transaction(` with `let additional_state_digest =`.

3. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch replaces `let deferral_info = self.should_defer(` with `let tx_cost = shared_object_congestion_tracker.get_tx_cost(`.

4. In `crates/sui-protocol-config/src/lib.rs`, the patch adds `// If true, include indirect state in the additional consensus digest.`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, `crates/sui-core/src/authority`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-core/src/global_state_hasher.rs`, `crates/sui-core/src/signature_verifier.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/authority/shared_object_congestion_tracker.rs`, `crates/sui-core/src/signature_verifier.rs`. The strongest project-level identifiers around this patch are `additional_state_digest`, `commit_info`, `IndirectStateObserver`, and `state`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/transfer_to_object_tests.rs`, `crates/sui-core/src/unit_tests/transaction_tests.rs`.

## Before/After Behavior

Before the patch, the consensus commit prologue used `commit_info.additional_state_digest()` directly when additional state digest recording was enabled. The commit message states that derived or persistent state inspected during commit processing was not previously committed to and could diverge unnoticed. After the patch, an `IndirectStateObserver` accumulates serialized observed state into a hash, is threaded through consensus transaction processing, and is conditionally folded with `commit_info.additional_state_digest()` when `additional_consensus_digest_indirect_state` is enabled.

# Root Cause

A commitment-boundary gap: some derived or persistent state inspected while processing commits could influence decisions without being included in the additional consensus digest. The evidence frames this as a latent divergence detection problem, not as a proven externally exploitable flaw.

## Walkthrough

1. The commit message defines indirect state as state inspected and used for decisions while processing a commit, but not already committed as part of the commit contents.

2. `consensus_handler.rs` adds `IndirectStateObserver`, backed by `DefaultHash`, with an API that serializes observed state into the running hash.

3. `create_consensus_commit_prologue_transaction` now accepts the observer and, under `additional_consensus_digest_indirect_state`, folds the observer hash with `commit_info.additional_state_digest()`.

4. `authority_per_epoch_store.rs` passes the observer into `shared_object_congestion_tracker.get_tx_cost` before deferral-related processing.

5. `sui-protocol-config` adds a feature flag controlling whether indirect state is included in the additional consensus digest.

6. The evidence does not show theft, signature bypass, unauthorized execution, or a concrete adversarial trigger.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/consensus_handler.rs | 331 | builds consensus commit prologue and folds observed indirect state into additional_state_digest when the protocol flag is enabled |
| crates/sui-core/src/consensus_handler.rs | 391 | defines IndirectStateObserver that serializes observed state into a running hash |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 4340 | passes the indirect state observer through consensus user transaction processing before deferral decisions |
| crates/sui-core/src/authority/shared_object_congestion_tracker.rs | 1 | traced path for congestion-control state consulted while computing transaction cost |
| crates/sui-protocol-config/src/lib.rs | 750 | adds protocol feature flag controlling inclusion of indirect state in the additional consensus digest |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/consensus_handler.rs:391` (changes signature or replay validation logic)

Before
```rust
}

    #[test]
    fn test_additional_consensus_state() {
```
After
```rust
}

    #[derive(Default)]
    pub struct IndirectStateObserver {
        hash: DefaultHash,
    }

    impl IndirectStateObserver {
```

## Snippet 2

Context: `crates/sui-core/src/consensus_handler.rs:368` (changes a sensitive control or state-update path)

Before
```rust
if protocol_config.record_additional_state_digest_in_prologue() {
                self.consensus_commit_prologue_v4_transaction(
                    epoch,
                    version_assignments.unwrap(),
                    commit_info.additional_state_digest(),
                )
            } else if let Some(version_assignments) = version_assignments {
```
After
```rust
if protocol_config.record_additional_state_digest_in_prologue() {
                let additional_state_digest =
                    if protocol_config.additional_consensus_digest_indirect_state() {
                        let d1 = commit_info.additional_state_digest();
                        indirect_state_observer.fold_with(d1)
                    } else {
                        commit_info.additional_state_digest()
```

## Snippet 3

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:4383` (changes a sensitive control or state-update path)

Before
```rust
}

        let deferral_info = self.should_defer(
            execution_time_estimator,
            &transaction,
            commit_info,
            dkg_failed,
```
After
```rust
}

        let tx_cost = shared_object_congestion_tracker.get_tx_cost(
            execution_time_estimator,
            &transaction,
            indirect_state_observer,
        );
```

## Snippet 4

Context: `crates/sui-protocol-config/src/lib.rs:750` (changes a sensitive control or state-update path)

Before
```rust
#[serde(skip_serializing_if = "is_false")]
    allow_private_accumulator_entrypoints: bool,
}
```
After
```rust
#[serde(skip_serializing_if = "is_false")]
    allow_private_accumulator_entrypoints: bool,

    // If true, include indirect state in the additional consensus digest.
    #[serde(skip_serializing_if = "is_false")]
    additional_consensus_digest_indirect_state: bool,
}
```

# Fix Pattern

Thread an explicit observer through commit-processing paths that inspect derived state, hash the observed state deterministically, and include that hash in the consensus/prologue digest behind a protocol feature flag.

## How It Was Fixed

The patch defines `IndirectStateObserver`, passes it through relevant consensus transaction-processing code, and changes consensus commit prologue creation so the observer hash can be folded into the recorded additional state digest when the new protocol flag is enabled.

# Why It Matters

1. Consensus divergence is security-relevant in principle.

2. Earlier detection of divergent validator state can reduce delayed fork risk.

3. The supplied evidence supports hardening and diagnosability, not a confirmed vulnerability fix.

4. Runtime behavior depends on the new protocol flag being enabled.

# Evidence Notes

Grounded evidence comes from `consensus_handler.rs` adding `IndirectStateObserver` and folding it into `additional_state_digest`, `authority_per_epoch_store.rs` forwarding the observer into transaction-cost calculation, and `sui-protocol-config` adding `additional_consensus_digest_indirect_state`. Claims about cryptographic weaknesses, external exploitability, or complete coverage of all indirect state sources are unsupported. The shared-object congestion tracker is implicated by the call path, but the provided excerpts do not fully show what state it observes internally. Protocol security invariant: Consensus commit processing should be deterministic across validators, and state inspected while making commit-processing decisions should be represented in the committed digest surface so validator divergence is detected promptly. Verification notes: No concrete external attacker path is shown by the patch. No theft, unauthorized transaction execution, or signature bypass is demonstrated. No cryptographic primitive weakness is shown despite digest-related code changes. The evidence supports consensus divergence detection hardening, not a proven exploitable consensus break. The patch does not prove that every possible indirect state source is now covered. Runtime impact depends on the added protocol flag being enabled. No external attacker path is demonstrated. No cryptographic primitive weakness is shown. No concrete exploit scenario is established. The change is best treated as consensus integrity hardening with unclear vulnerability status. Keep out of the security corpus under the provided strict rules. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-state-commitment-gap`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `infrastructure, consensus, validator, state-integrity, state-commitment, hardening`

The supplied evidence supports retaining this as security hardening, not as a concrete security fix. The patch makes consensus commit processing commit to additional indirect state that can affect decisions, and the commit message explicitly frames the prior behavior as allowing validator state divergence to remain hidden until a later fork. That is security-sensitive consensus integrity hardening, but the evidence does not prove an exploitable attacker path, cryptographic break, signature issue, or specific vulnerability trigger.

## Security Evidence

1. Adds an IndirectStateObserver that serializes observed indirect state into a running hash.
2. Conditionally folds the indirect-state hash into the additional consensus digest recorded in the consensus commit prologue.
3. Threads the observer into consensus transaction processing around shared-object congestion transaction-cost decisions.
4. Adds a protocol feature flag described as including indirect state in the additional consensus digest.
5. Commit message states that uncommitted derived state could diverge unnoticed and cause delayed forks.

## Missing Evidence

1. No concrete external attacker path is shown.
2. No proof of unauthorized execution, theft, signature bypass, or cryptographic primitive weakness is provided.
3. No specific prior production incident or exploit scenario is included in the supplied evidence.
4. The excerpts do not fully show every indirect state source or prove complete coverage.

## Claim Boundaries

1. Classify as consensus/state-integrity hardening only.
2. Do not claim a confirmed exploitable vulnerability.
3. Do not describe this as a signature, RPC, snapshot, or cryptographic primitive fix.
4. Runtime effect depends on the added protocol flag being enabled.
