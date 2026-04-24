---
case_id: case_20240521_d0ebedf217
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2024-05-21
source_refs:
  - git:d0ebedf2176c3be18f6778475f92ce9e2ee39836
  - "crates/sui-bridge/src/sui_client.rs:254"
  - "crates/sui-bridge-cli/src/main.rs:87"
  - "crates/sui-bridge/src/action_executor.rs:257"
  - "crates/sui-bridge/src/sui_client.rs:215"
bug_class: signature-threshold-api-hardening
impact_type:
  - signature-quorum-integrity
confidence: medium
tags:
  - bridge
  - signature
  - quorum
  - api-hardening
  - committee-signatures
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a cleanup or hardening of the bridge committee signature API, not a validated vulnerability fix. Callers no longer pass an explicit threshold to `request_committee_signatures`; the aggregator derives `action.approval_threshold()` internally. Existing shown callers already passed `action.approval_threshold()`, so no concrete bypass, incorrect quorum, or exploit path is established.

## Observed Patch Facts

1. In `crates/sui-bridge/src/sui_client.rs`, the patch replaces `pub async fn execute_transaction_block_with_effects(` with `pub async fn get_reference_gas_price_until_success(&self) -> u64 {`.

2. In `crates/sui-bridge-cli/src/main.rs`, the patch replaces `let threshold = sui_action.approval_threshold();` with `.request_committee_signatures(sui_action)`.

3. In `crates/sui-bridge/src/action_executor.rs`, the patch replaces `let threshold = action.approval_threshold();` with `match auth_agg.request_committee_signatures(action.clone()).await {`.

4. In `crates/sui-bridge/src/sui_client.rs`, the patch replaces `// TODO: cache this` with `pub async fn get_bridge_committee(&self) -> BridgeResult<BridgeCommittee> {`.

## Project Context

The changed code sits primarily in `crates/sui-bridge/src`, `crates/sui-bridge`, `crates/sui-bridge-cli/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/sui-bridge/src/sui_syncer.rs`, `crates/sui-bridge/src/node.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-bridge/src/client/bridge_authority_aggregator.rs`, `crates/sui-bridge/src/sui_syncer.rs`. The strongest project-level identifiers around this patch are `await`, `sui_action`, `threshold`, and `request_committee_signatures`. Nearby tests or test-like files include `crates/sui-bridge/src/e2e_tests/basic.rs`, `crates/sui-bridge/src/e2e_tests/test_utils.rs`.

## Before/After Behavior

Before the patch, the action executor and governance CLI computed `action.approval_threshold()` or `sui_action.approval_threshold()` and passed that value into `request_committee_signatures(action, threshold)`. After the patch, callers pass only the action, and `BridgeAuthorityAggregator::request_committee_signatures` derives the threshold internally. Separately, a reference-gas-price retry helper was added and a bridge-record helper was removed, but neither is tied to a demonstrated security boundary in the supplied evidence.

# Root Cause

The old API allowed internal callers to supply a threshold separately from the action. That is a potential API footgun around quorum calculation, but the supplied diff shows the changed callers were already passing the action's own threshold, so the evidence does not establish an actual root-cause vulnerability.

## Walkthrough

1. The token-transfer signing path previously computed `let threshold = action.approval_threshold()` and passed it to `auth_agg.request_committee_signatures(action.clone(), threshold)`.

2. That path now calls `auth_agg.request_committee_signatures(action.clone())`.

3. The governance CLI path previously computed `let threshold = sui_action.approval_threshold()` and passed it to `agg.request_committee_signatures(sui_action, threshold)`.

4. That path now calls `agg.request_committee_signatures(sui_action)`.

5. The traced aggregator implementation takes only `action: BridgeAction` and constructs `GetSigsState::new(action.approval_threshold(), self.committee.clone())`.

6. No evidence shows any old caller supplied a lower, stale, or mismatched threshold.

7. No replay, forgery, authorization bypass, or externally reachable exploit path is demonstrated.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-bridge/src/client/bridge_authority_aggregator.rs | 64 | committee signature aggregation now derives the approval threshold from the action internally |
| crates/sui-bridge/src/action_executor.rs | 257 | token transfer signing path requests committee signatures without passing a caller-controlled threshold |
| crates/sui-bridge-cli/src/main.rs | 87 | governance CLI path requests committee signatures through the centralized threshold API |
| crates/sui-bridge/src/sui_client.rs | 254 | adds retry-until-success helper for reference gas price; operational reliability, not a shown security invariant |

## Code Snippets

## Snippet 1

Context: `crates/sui-bridge/src/sui_client.rs:254` (changes a sensitive control or state-update path)

Before
```rust
}

    pub async fn execute_transaction_block_with_effects(
        &self,
```
After
```rust
}

    pub async fn get_reference_gas_price_until_success(&self) -> u64 {
        loop {
            let Ok(Ok(rgp)) = retry_with_max_elapsed_time!(
                self.inner.get_reference_gas_price(),
                Duration::from_secs(30)
            ) else {
```

## Snippet 2

Context: `crates/sui-bridge-cli/src/main.rs:87` (changes an authorization or privilege gate)

Before
```rust
let sui_action = make_action(sui_chain_id, &cmd);
                println!("Action to execute on Sui: {:?}", sui_action);
                let threshold = sui_action.approval_threshold();
                let certified_action = agg
                    .request_committee_signatures(sui_action, threshold)
                    .await
                    .expect("Failed to request committee signatures");
                let bridge_arg = sui_client
```
After
```rust
let sui_action = make_action(sui_chain_id, &cmd);
                println!("Action to execute on Sui: {:?}", sui_action);
                let certified_action = agg
                    .request_committee_signatures(sui_action)
                    .await
                    .expect("Failed to request committee signatures");
                let bridge_arg = sui_bridge_client
                    .get_mutable_bridge_object_arg_must_succeed()
```

## Snippet 3

Context: `crates/sui-bridge/src/action_executor.rs:257` (changes an authorization or privilege gate)

Before
```rust
return;
        }
        let threshold = action.approval_threshold();
        match auth_agg
            .request_committee_signatures(action.clone(), threshold)
            .await
        {
            Ok(certificate) => {
```
After
```rust
return;
        }
        match auth_agg.request_committee_signatures(action.clone()).await {
            Ok(certificate) => {
                execution_queue_sender
```

## Snippet 4

Context: `crates/sui-bridge/src/sui_client.rs:215` (changes a sensitive control or state-update path)

Before
```rust
}

    // TODO: cache this
    pub async fn get_bridge_record_id(&self) -> BridgeResult<ObjectID> {
        self.inner
            .get_bridge_summary()
            .await
            .map_err(|e| BridgeError::InternalError(format!("Can't get bridge committee: {e}")))
```
After
```rust
}

    pub async fn get_bridge_committee(&self) -> BridgeResult<BridgeCommittee> {
        let bridge_summary =
```

# Fix Pattern

Centralize a security-sensitive derived parameter inside the API that consumes it, instead of requiring each caller to pass the value separately.

## How It Was Fixed

The patch removed the threshold argument from `request_committee_signatures` call sites and changed the aggregator to derive the approval threshold from the `BridgeAction` internally before collecting committee signatures.

# Why It Matters

1. Committee signature certification depends on applying the correct quorum threshold.

2. Deriving the threshold internally reduces future misuse risk.

3. The shown change is security-adjacent hardening, not proof of a prior exploitable flaw.

# Evidence Notes

Primary evidence comes from `crates/sui-bridge/src/client/bridge_authority_aggregator.rs`, `crates/sui-bridge/src/action_executor.rs`, and `crates/sui-bridge-cli/src/main.rs`. The gas-price retry helper in `sui_client.rs` appears operational. The removed bridge-record helper is not connected to a security issue by the provided evidence. The heuristic baseline's replay/signature-validation and storage claims are unsupported and should be downgraded. Protocol security invariant: Bridge actions should be certified only after collecting enough committee authority signatures for the approval threshold associated with that specific action. The patch centralizes threshold derivation inside the aggregator, but the provided evidence does not show any pre-patch caller using an incorrect threshold. Verification notes: No evidence shows any pre-patch caller supplied a lower or incorrect threshold. No replay, forgery, or signature-validation bypass is proven by the patch. No exploitability or externally reachable attack path is demonstrated. Gas price retry and removed bridge record helper changes are not shown to alter a security boundary. This should not be classified as a confirmed vulnerability fix from the provided evidence alone. Existing shown callers already used `action.approval_threshold()` before the patch. No incorrect threshold value is shown in the pre-patch code excerpts. No attack path or failed security invariant is demonstrated. Do not retain this as a confirmed vulnerability-fix corpus item based on the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-threshold-api-hardening`
Final impact type: `signature-quorum-integrity`
Final confidence: `medium`
Final tags: `bridge, signature, quorum, api-hardening, committee-signatures`

The supplied evidence does not prove a concrete exploitable vulnerability: the shown pre-patch callers already passed `action.approval_threshold()`. However, the patch does remove a security-sensitive API footgun by eliminating a separately supplied threshold from committee signature requests and deriving the quorum threshold from the action inside the aggregator. In a bridge signing path, that is credible security hardening, but not a confirmed security fix for replay, forgery, or storage behavior.

## Security Evidence

1. Committee signature certification depends on the approval threshold associated with a bridge action.
2. Call sites changed from `request_committee_signatures(action, threshold)` to `request_committee_signatures(action)`.
3. The traced aggregator implementation now derives the threshold via `action.approval_threshold()` internally.
4. The changed path is used by bridge action execution and governance CLI signing flows.

## Missing Evidence

1. No shown pre-patch caller supplied an incorrect, stale, lower, or attacker-influenced threshold.
2. No exploit path, bypass, replay, or request forgery is demonstrated by the patch evidence.
3. No test evidence shows a previously accepted invalid certificate or quorum mismatch.
4. The gas price retry and bridge committee helper changes are operational or cleanup-oriented, not independently security-relevant.

## Claim Boundaries

1. Treat this as hardening of a security-sensitive signing API, not as a proven vulnerability fix.
2. Do not classify the issue as replay, request forgery, or storage corruption from the provided evidence.
3. Do not claim external attacker control over the threshold parameter without additional evidence.
4. The corpus entry should focus on centralized quorum-threshold derivation for bridge committee signatures.
