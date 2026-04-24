---
case_id: case_20220630_992af87ebf
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
date: 2022-06-30
source_refs:
  - git:992af87ebf2f0826c6aa33fe05a7791afa092096
  - "crates/sui-core/src/authority_aggregator.rs:525"
  - "crates/sui-core/src/authority_aggregator.rs:1458"
  - "crates/sui-core/src/authority_active/gossip/node_sync.rs:364"
  - "crates/sui-types/src/error.rs:368"
bug_class: byzantine-availability-hardening
impact_type:
  - availability-degradation
  - liveness-degradation
tags:
  - blockchain-core
  - byzantine-fault-tolerance
  - gossip
  - authenticated-fetch
  - timeout-handling
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best characterized as Byzantine-availability hardening for Sui gossip node sync. It changes transaction/effects download from a direct request to the gossip peer into an AuthorityAggregator-mediated request that can accept one successful authenticated response with timeout handling. The evidence supports a liveness hardening claim, not a proven consensus-safety violation or false-data acceptance bug.

## Observed Patch Facts

1. In `crates/sui-core/src/authority_aggregator.rs`, the patch replaces `/// Return all the information in the network regarding the latest state of a specifi...` with `/// Like quorum_map_then_reduce_with_timeout, but for things that need only a single`.

2. In `crates/sui-core/src/authority_aggregator.rs`, the patch adds `pub async fn handle_transaction_and_effects_info_request(`.

3. In `crates/sui-core/src/authority_active/gossip/node_sync.rs`, the patch replaces `// TODO: Add a function to AuthorityAggregator to try multiple validators - even` with `// TODO: should we suggest that we try peer first?`.

4. In `crates/sui-types/src/error.rs`, the patch adds `#[error("Operation timed out")]`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, `crates/sui-core/src/authority_active/gossip`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/sui-core/src/authority_server.rs`, `crates/sui-core/src/authority.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/messages.rs`, `crates/sui-types/src/crypto.rs`. The strongest project-level identifiers around this patch are `object`, `cert`, `authority`, and `that`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/authority_tests.rs`, `crates/sui-core/src/unit_tests/authority_aggregator_tests.rs`.

## Before/After Behavior

Before the patch, `download_impl` cloned a client for the peer associated with the gossiped digest and requested transaction/effects info directly from that peer. The removed comment stated that the peer might be Byzantine and refuse to provide the cert and effects. After the patch, `download_impl` calls `aggregator.handle_transaction_and_effects_info_request(digests).await?`, and the new aggregator method uses `quorum_once_with_timeout`, documented for cases where only one successful response is needed and false answers are prevented by a known digest or quorum-signed object. A `TimeoutError` variant is also added for timeout handling.

# Root Cause

The prior node sync transaction/effects fetch path depended on one peer returning data. For authenticated data that other authorities could also provide, that single-peer dependency exposed the path to Byzantine withholding, timeout, or slow-response behavior.

## Walkthrough

1. Node sync enters `download_impl` with `ExecutionDigests`.

2. Before the change, the code cloned a client for the specific `peer` and requested transaction/effects info from that peer directly.

3. The removed TODO explicitly noted that the validator might be Byzantine and refuse to return the cert and effects.

4. The patch adds `AuthorityAggregator::quorum_once_with_timeout`, documented for single successful responses where Byzantine authorities can time out or slow-loris but cannot give a false answer because the digest is known or the object is quorum-signed.

5. The patch adds `AuthorityAggregator::handle_transaction_and_effects_info_request` using that helper.

6. `download_impl` now calls the aggregator method instead of directly calling the peer client.

7. `SuiError::TimeoutError` is added as part of the new timeout failure surface.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority_aggregator.rs | 525 | adds quorum_once_with_timeout helper for single authenticated successful response with timeout behavior across authorities |
| crates/sui-core/src/authority_aggregator.rs | 1458 | adds aggregator method for transaction and effects info requests using the new single-success authority query path |
| crates/sui-core/src/authority_active/gossip/node_sync.rs | 364 | changes node sync download path from querying the gossip peer directly to querying through the authority aggregator |
| crates/sui-types/src/error.rs | 368 | adds timeout error variant used by the new failure-handling path |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/authority_aggregator.rs:525` (changes bounds, limits, or capacity handling)

Before
```rust
}

    /// Return all the information in the network regarding the latest state of a specific object.
    /// For each authority queried, we obtain the latest object state along with the certificate that
```
After
```rust
}

    /// Like quorum_map_then_reduce_with_timeout, but for things that need only a single
    /// successful response, such as fetching a Transaction from some authority.
    /// This is intended for cases in which byzantine authorities can time out or slow-loris, but
    /// can't give a false answer, because e.g. the digest of the response is known, or a
    /// quorum-signed object such as a checkpoint has been requested.
    pub(crate) async fn quorum_once_with_timeout<'a, S, FMap>(
```

## Snippet 2

Context: `crates/sui-core/src/authority_aggregator.rs:1458` (changes a consensus- or validator-sensitive branch)

Before
```rust
.expect("Cannot send object on channel after object fetch attempt");
    }
}
```
After
```rust
.expect("Cannot send object on channel after object fetch attempt");
    }

    pub async fn handle_transaction_and_effects_info_request(
        &self,
        digests: &ExecutionDigests,
    ) -> Result<TransactionInfoResponse, SuiError> {
        self.quorum_once_with_timeout(
```

## Snippet 3

Context: `crates/sui-core/src/authority_active/gossip/node_sync.rs:364` (changes the branch that decides whether execution stops or continues)

Before
```rust
let digest = digests.transaction;

        // TODO: Add a function to AuthorityAggregator to try multiple validators - even
        // though we are fetching the cert/effects from the same validator that sent us the tx
        // digest, and even though we know the cert is final, any given validator may be byzantine
        // and refuse to give us the cert and effects.
        let client = aggregator.clone_client(&peer);
        let resp = client
```
After
```rust
let digest = digests.transaction;

        // TODO: should we suggest that we try peer first?
        let resp = aggregator
            .handle_transaction_and_effects_info_request(digests)
            .await?;

        let cert = resp.certified_transaction.ok_or_else(|| {
```

## Snippet 4

Context: `crates/sui-types/src/error.rs:368` (changes a sensitive control or state-update path)

Before
```rust
QuorumDriverCommunicationError { error: String },

    #[error("Error executing {0}")]
    ExecutionError(String),
```
After
```rust
QuorumDriverCommunicationError { error: String },

    #[error("Operation timed out")]
    TimeoutError,

    #[error("Error executing {0}")]
    ExecutionError(String),
```

# Fix Pattern

Replace a single-authority request for authenticated data with an aggregator-mediated multi-authority query that accepts one valid successful response and applies timeout handling.

## How It Was Fixed

The patch adds a single-success authority aggregation helper, wires transaction/effects info requests through it, and updates gossip node sync download logic to use the aggregator instead of querying the original peer directly.

# Why It Matters

1. Reduces reliance on one potentially Byzantine gossip peer.

2. Improves liveness for digest-authenticated or quorum-certified data retrieval.

3. Explicitly targets timeout, withholding, or slow-response behavior.

4. Does not establish a prior false-data acceptance or consensus-divergence vulnerability.

# Evidence Notes

Primary evidence is `crates/sui-core/src/authority_active/gossip/node_sync.rs`, where a direct peer request is replaced with `aggregator.handle_transaction_and_effects_info_request(digests).await?`. Supporting evidence is `crates/sui-core/src/authority_aggregator.rs`, where `quorum_once_with_timeout` is documented for Byzantine timeout or slow-loris cases when false answers are prevented by known digests or quorum signatures, and where the transaction/effects aggregator method is added. `crates/sui-types/src/error.rs` adds `TimeoutError`. The evidence does not prove accepted forged data, state corruption, consensus divergence, or a complete fix for all object-fetch paths. Protocol security invariant: For transaction/effects data whose correctness is independently anchored by known digests or quorum certification, node sync should not depend on the single gossip peer that supplied the digest; a Byzantine authority may withhold, time out, or slow responses, but should not be able to block retrieval when another authority can provide an authenticated equivalent response. Verification notes: The patch does not prove that false transaction or effects data could previously be accepted. The patch does not prove consensus divergence or state corruption. The patch does not show a full exploit, only mitigation of single-peer withholding, timeout, or slow-response behavior. The patch does not establish that all object-fetch paths are Byzantine tolerant; the shown change targets transaction/effects info and a helper for similar authenticated fetches. Supported: single-peer transaction/effects fetch was replaced with an aggregator path. Supported: comments explicitly mention Byzantine timeout, slow-loris, and refusal concerns. Supported: the helper is scoped to data that is already digest-authenticated or quorum-signed. Not supported: consensus-safety bug, integrity bypass, or exploitability beyond liveness degradation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `byzantine-availability-hardening`
Final impact type: `availability-degradation, liveness-degradation`
Final tags: `blockchain-core, byzantine-fault-tolerance, gossip, authenticated-fetch, timeout-handling, availability`

The patch evidence supports keeping this as security hardening, not as a proven consensus-safety security fix. The changed path removes dependence on a single gossip peer for transaction/effects retrieval and adds an aggregator-based single-success fetch with timeout behavior for digest-authenticated or quorum-signed data. Comments explicitly frame the risk as Byzantine timeout, slow-loris, or refusal, which is security-relevant availability hardening in a blockchain validator context, but the patch does not prove false data acceptance, state corruption, or consensus divergence.

## Security Evidence

1. New helper is documented for cases where Byzantine authorities can time out or slow-loris but cannot provide false answers because the response is digest-authenticated or quorum-signed.
2. Node sync changes transaction/effects download from a direct peer client request to AuthorityAggregator.handle_transaction_and_effects_info_request.
3. Removed comment states the prior path depended on a validator that may be Byzantine and refuse to provide the cert and effects.
4. TimeoutError is added as part of the new timeout-aware authority aggregation path.

## Missing Evidence

1. No evidence that forged or invalid transaction/effects data could previously be accepted.
2. No evidence of consensus divergence, state corruption, or safety violation.
3. No exploit scenario or vulnerability advisory is provided.
4. No proof that the change fully covers all object-fetch or node-sync paths.

## Claim Boundaries

1. Classify as Byzantine availability/liveness hardening, not consensus-safety.
2. Impact should be limited to reducing single-peer withholding, timeout, or slow-response risk.
3. The evidence supports one-success authenticated fetch behavior only where correctness is anchored by known digests or quorum signatures.
4. Do not claim an integrity bypass, signature failure, or concrete exploitable consensus bug from this patch alone.
