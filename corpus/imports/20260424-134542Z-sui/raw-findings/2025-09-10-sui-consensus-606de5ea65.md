---
case_id: case_20250910_606de5ea65
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2025-09-10
source_refs:
  - git:606de5ea650f7f02a265b98329c48f5935c35725
  - "crates/sui-core/src/consensus_handler.rs:789"
  - "crates/sui-core/src/authority_server.rs:560"
  - "crates/sui-core/src/authority_server.rs:1094"
  - "crates/sui-core/src/consensus_handler.rs:997"
bug_class: resource-exhaustion-dos-hardening
impact_type:
  - denial-of-service
  - resource-exhaustion
tags:
  - blockchain-core
  - consensus
  - dos-hardening
  - resource-control
  - rate-limiting
  - traffic-attribution
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a DoS-oriented hardening change for Sui's Mysticeti fast path transaction submission flow. The patch adds submitted-transaction accounting and client attribution so repeated submissions of the same user transaction digest can be counted after the transaction appears in consensus output and excess submissions can be fed into traffic-control spam weighting. The evidence does not prove a practical exploit or quantify resource exhaustion impact, so this should be treated as likely security hardening rather than a confirmed vulnerability fix.

## Observed Patch Facts

1. In `crates/sui-core/src/consensus_handler.rs`, the patch replaces `if parsed.rejected {` with `// Transaction has appeared in consensus output, we can increment the submission count`.

2. In `crates/sui-core/src/authority_server.rs`, the patch replaces `client_id_source: _,` with `client_id_source,`.

3. In `crates/sui-core/src/authority_server.rs`, the patch adds `None, // not tracking submitter client addr for quorum driver path`.

4. In `crates/sui-core/src/consensus_handler.rs`, the patch replaces `.submit(end_of_publish, None, &self.epoch_store, None)` with `.submit(end_of_publish, None, &self.epoch_store, None, None)`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/sui-core/src/transaction_orchestrator.rs`, `crates/sui-core/src/transaction_input_loader.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/consensus_validator.rs`, `crates/sui-core/src/consensus_adapter.rs`. The strongest project-level identifiers around this patch are `None`, `epoch_store`, `client_id_source`, and `ConsensusTransactionKind::UserTransaction`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/transaction_tests.rs`, `crates/sui-core/src/unit_tests/transaction_deny_tests.rs`.

## Before/After Behavior

Before the patch, the shown consensus handler path moved from constructing a consensus position into rejected-transaction handling without visible submitted-transaction resubmission accounting. After the patch, when Mysticeti fast path is enabled and consensus output contains a user transaction, the handler extracts the transaction digest and calls `submitted_transaction_cache.increment_submission_count(digest)`. Before the patch, the shown raw transaction submission handler ignored `client_id_source`; after the patch, it derives a submitter client address from the request using the configured source or socket address fallback. Some consensus submission call sites now pass an additional optional submitter-attribution argument, while the quorum-driver path explicitly passes `None`.

# Root Cause

The prior Mysticeti fast path submission flow lacked visible per-digest resubmission accounting and submitter attribution needed by the traffic controller to penalize excessive repeated submissions. This is missing resource-control and attribution logic, not a broken cryptographic or consensus-validity check.

## Walkthrough

1. A raw transaction submission enters `ValidatorService::handle_submit_transaction`.

2. The patched handler preserves `client_id_source` and derives a submitter client address from the request.

3. Consensus submission APIs are updated to carry optional submitter attribution; paths without attribution pass `None`.

4. When consensus output is processed, the handler gates the new accounting on `mysticeti_fastpath()`.

5. For `ConsensusTransactionKind::UserTransaction`, the handler extracts the digest and increments its submitted-transaction count.

6. The commit description states that excess resubmissions are converted into spam weight and attributed to the submitter through the traffic controller.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority/submitted_transaction_cache.rs | 1 | new cache for submitted transaction digests, retry allowance, garbage collection, and submitter attribution |
| crates/sui-core/src/consensus_handler.rs | 789 | increments submission count for MFP user transactions after they appear in consensus output and derives spam weight for excess submissions |
| crates/sui-core/src/authority_server.rs | 553 | extracts submitter client IP address from incoming raw transaction submission requests for later traffic attribution |
| crates/sui-core/src/authority_server.rs | 1063 | submits consensus transactions through quorum-driver path without submitter address tracking |
| crates/sui-core/src/consensus_adapter.rs | 34 | consensus submission path updated to carry optional submitter attribution into the submitted transaction tracking flow |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 21 | epoch-scoped storage context that owns or exposes the submitted transaction cache |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/consensus_handler.rs:789` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
index: tx_index as TransactionIndex,
                    };
                    if parsed.rejected {
                        if parsed.transaction.kind.is_user_transaction() {
```
After
```rust
index: tx_index as TransactionIndex,
                    };

                    // Transaction has appeared in consensus output, we can increment the submission count
                    // for this tx for DoS protection.
                    if self.epoch_store.protocol_config().mysticeti_fastpath() {
                        if let ConsensusTransactionKind::UserTransaction(tx) =
                            &parsed.transaction.kind
```

## Snippet 2

Context: `crates/sui-core/src/authority_server.rs:560` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
metrics,
            traffic_controller: _,
            client_id_source: _,
        } = self.clone();
        let epoch_store = state.load_epoch_store_one_call_per_task();
        if !epoch_store.protocol_config().mysticeti_fastpath() {
```
After
```rust
metrics,
            traffic_controller: _,
            client_id_source,
        } = self.clone();

        let submitter_client_addr = if let Some(client_id_source) = &client_id_source {
            self.get_client_ip_addr(&request, client_id_source)
        } else {
```

## Snippet 3

Context: `crates/sui-core/src/authority_server.rs:1094` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
epoch_store,
                    None,
                )?;
                // Do not wait for the result, because the transaction might have already executed.
```
After
```rust
epoch_store,
                    None,
                    None, // not tracking submitter client addr for quorum driver path
                )?;
                // Do not wait for the result, because the transaction might have already executed.
```

## Snippet 4

Context: `crates/sui-core/src/consensus_handler.rs:997` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
if let Err(err) =
            self.consensus_adapter
                .submit(end_of_publish, None, &self.epoch_store, None)
        {
            warn!(
```
After
```rust
if let Err(err) =
            self.consensus_adapter
                .submit(end_of_publish, None, &self.epoch_store, None, None)
        {
            warn!(
```

# Fix Pattern

Add bounded resource accounting at the point where repeated resource use becomes observable, propagate client attribution from ingress through the relevant submission path, and connect excess usage to an existing throttling mechanism.

## How It Was Fixed

The patch introduces an epoch-scoped submitted transaction cache, records submitter client address information for raw transaction submissions, extends consensus submission plumbing to carry optional attribution, and increments per-digest submission counts for Mysticeti fast path user transactions seen in consensus output. The commit description says the cache applies gas-price-based retry allowance, extra tolerance, round-based garbage collection, and traffic-controller spam weighting for excess resubmissions.

# Why It Matters

1. Repeated transaction resubmissions become visible to throttling logic.

2. Spam accounting can be tied to the submitting client where attribution is available.

3. The mitigation is scoped to Mysticeti fast path user transactions in the provided evidence.

4. The evidence does not establish impact magnitude or exploitability.

# Evidence Notes

The commit message explicitly describes DoS protection against excessive transaction resubmissions. The strongest code evidence is the new Mysticeti-gated user-transaction handling in `consensus_handler.rs` that calls `submitted_transaction_cache.increment_submission_count(digest)`, plus `authority_server.rs` changes that derive submitter client addresses from incoming requests. The provided snippets do not include the full submitted transaction cache implementation, exact allowance calculation, or the final traffic-controller tally call, so claims about those details rely mainly on the commit description. The heuristic baseline's serialization/state-representation theory is unsupported and should be discarded. Protocol security invariant: Mysticeti fast path user transaction resubmissions should be counted per transaction digest and, when they exceed the allowed retry budget, attributable to the submitting client for traffic-control throttling. The evidence supports a resource-control invariant, not a consensus-safety, signature-verification, or transaction-validity invariant. Verification notes: The patch does not prove that excessive resubmission was exploitable in a deployed configuration. The patch does not show consensus safety, transaction validity, or signature verification being fixed. The patch does not prove a remote unauthenticated attack path beyond client-attributed submission traffic. The patch does not quantify resource exhaustion impact or required submission volume. The patch does not show protection for non-Mysticeti-fastpath transaction paths. Treat as likely security hardening, not confirmed exploit remediation. Do not claim consensus safety, signature verification, or transaction validity was fixed. Do not claim protection applies to all transaction paths; the shown logic is Mysticeti fast path scoped. Quorum-driver attribution is explicitly absent in the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion-dos-hardening`
Final impact type: `denial-of-service, resource-exhaustion`
Final tags: `blockchain-core, consensus, dos-hardening, resource-control, rate-limiting, traffic-attribution, validator`

The supplied evidence supports retaining this as security hardening, not as the original serialization/state-representation finding. The commit message explicitly frames the change as DoS protection against excessive transaction resubmissions, and the code evidence shows Mysticeti fast path user transactions being counted by digest after consensus output plus client address attribution being propagated for traffic-controller spam weighting. The patch does not prove a concrete exploit, deployed impact, or consensus-safety bug, so it should not be classified as a confirmed security fix.

## Security Evidence

1. Commit subject and body explicitly describe DoS protection for MFP submitted user transactions.
2. Consensus handler adds per-user-transaction digest submission counting gated on mysticeti_fastpath().
3. Authority server now derives submitter client address from the request for attribution.
4. Consensus submission APIs gain an optional submitter-attribution parameter, with some paths explicitly passing None.
5. Commit body says excess resubmissions are converted to spam weight and integrated with traffic-controller throttling.

## Missing Evidence

1. No full cache implementation or allowance calculation is shown in the supplied snippets.
2. No traffic-controller tally call is included in the provided code evidence.
3. No exploit scenario, required volume, or resource exhaustion magnitude is demonstrated.
4. No tests proving DoS mitigation behavior are included in the supplied evidence.
5. No evidence shows this affects non-Mysticeti-fastpath paths or quorum-driver attribution.

## Claim Boundaries

1. Treat as DoS/resource-control hardening rather than a proven vulnerability fix.
2. Do not claim serialization, state representation, client-view divergence, or consensus safety was fixed.
3. Do not claim signature verification, transaction validity, or cryptographic checks were involved.
4. Claims should be scoped to Mysticeti fast path user transaction resubmission accounting.
5. Client attribution is only supported where submitter address is propagated; quorum-driver path is explicitly not tracked.
