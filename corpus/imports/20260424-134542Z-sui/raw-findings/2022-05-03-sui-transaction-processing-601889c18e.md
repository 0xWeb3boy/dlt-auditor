---
case_id: case_20220503_601889c18e
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2022-05-03
source_refs:
  - git:601889c18eb6175f77b9ee489d308ceaf33155dc
  - "sui_core/src/authority_client.rs:345"
  - "sui_core/src/safe_client.rs:383"
  - "sui_core/src/authority_client.rs:389"
  - "sui_core/src/authority.rs:536"
bug_class: resource-exhaustion
impact_type:
  - denial-of-service
tags:
  - infrastructure
  - transaction-processing
  - batch-streaming
  - resource-control
  - denial-of-service
  - safe-client
  - authority
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a conservative security-hardening finding for Sui authority follower batch streaming. The strongest grounded change is resource-control hardening: authority-side request bounds were added, and SafeClient now tracks streamed item count with an inline comment identifying the guard as protection against server DoS. The evidence does not prove a confirmed exploitable vulnerability, consensus flaw, authorization bypass, or serialization/state-representation bug.

## Observed Patch Facts

1. In `sui_core/src/authority_client.rs`, the patch replaces `) -> Result<BatchInfoResponseItemStream, io::Error> {` with `) -> Result<BatchInfoResponseItemStream, SuiError> {`.

2. In `sui_core/src/safe_client.rs`, the patch replaces `(0u64, None),` with `let count: u64 = 0;`.

3. In `sui_core/src/authority_client.rs`, the patch replaces `let client_ref = client.state.as_ref().try_lock().unwrap();` with `client.state.insert_genesis_object(object).await;`.

4. In `sui_core/src/authority.rs`, the patch replaces `) -> Result<(VecDeque<UpdateItem>, bool), SuiError> {` with `) -> Result<`.

## Project Context

The changed code sits primarily in `sui_core/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sui_core/src/gateway_state.rs`, `sui_core/src/authority_server.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sui_core/src/authority_server.rs`, `sui_core/src/authority_aggregator.rs`. The strongest project-level identifiers around this patch are `state`, `await`, `Box::pin`, and `Result`. Nearby tests or test-like files include `sui_core/src/unit_tests/gateway_state_tests.rs`, `sui_core/src/unit_tests/batch_tests.rs`.

## Before/After Behavior

Before the patch, the provided evidence shows AuthorityState::handle_batch_info_request rejecting end <= start but does not show a zero-length check, maximum requested-item cap, or returned computed stream range. LocalAuthorityClient built the response stream locally from returned VecDeque values. SafeClient scanned received batch_info_items while tracking sequence and last batch state, but the shown before state had no count-based bound on consumed items. After the patch, AuthorityState adds checks for request.length == 0 and request.end - request.start > MAX_ITEMS_LIMIT, LocalAuthorityClient delegates streaming to state.handle_batch_streaming(request), and SafeClient adds count tracking plus a guard against processing more than 10 * request.length items.

# Root Cause

The supported root cause is insufficient boundedness in the follower batch streaming path. The before evidence shows less complete request validation and no shown client-side cap on the number of streamed response items consumed by SafeClient. The patch hardens both producer-side request validation and consumer-side response consumption limits.

## Walkthrough

1. A follower or safe client requests batch information through BatchInfoRequest.

2. Before the patch, AuthorityState returned update items plus a subscription flag after the shown end <= start validation.

3. LocalAuthorityClient constructed a BatchInfoResponseItem stream locally from VecDeque values returned by AuthorityState.

4. The provided SafeClient before state tracked sequence and last batch state, but not a received-item count.

5. After the patch, AuthorityState rejects zero-length requests and ranges larger than MAX_ITEMS_LIMIT.

6. AuthorityState also returns computed start and end values with the subscription decision.

7. LocalAuthorityClient delegates streaming to state.handle_batch_streaming(request) and propagates SuiError.

8. SafeClient adds count state and checks whether received items exceed 10 * request.length, with the code comment describing this as server DoS protection.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sui_core/src/safe_client.rs | 383 | Client-side validation of authority batch stream responses; adds count-based bound to avoid processing excessive streamed items. |
| sui_core/src/authority.rs | 536 | Authority-side BatchInfoRequest handling; validates requested length/range and caps requested items. |
| sui_core/src/authority_client.rs | 345 | Local authority client batch stream entry point; delegates streaming to AuthorityState and returns SuiError. |
| sui_core/src/authority/authority_notifier.rs | 6 | Related follower notification state for transaction sequence watermarks and stream lifecycle. |

## Code Snippets

## Snippet 1

Context: `sui_core/src/authority_client.rs:345` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
&self,
        request: BatchInfoRequest,
    ) -> Result<BatchInfoResponseItemStream, io::Error> {
        let state = self.state.clone();

        let update_items = state.lock().await.handle_batch_info_request(request).await;

        let (items, _): (VecDeque<_>, VecDeque<_>) = update_items.into_iter().unzip();
```
After
```rust
&self,
        request: BatchInfoRequest,
    ) -> Result<BatchInfoResponseItemStream, SuiError> {
        let state = self.state.clone();

        let update_items = state.handle_batch_streaming(request).await?;
        Ok(Box::pin(update_items))
    }
```

## Snippet 2

Context: `sui_core/src/safe_client.rs:383` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
let client = self.clone();
        let address = self.address;
        let stream = Box::pin(batch_info_items.scan(
            (0u64, None),
            move |(seq, txs_and_last_batch), batch_info_item| {
                let req_clone = request.clone();
                let client = client.clone();
```
After
```rust
let client = self.clone();
        let address = self.address;
        let count: u64 = 0;
        let stream = Box::pin(batch_info_items.scan(
            (0u64, None, count),
            move |(seq, txs_and_last_batch, count), batch_info_item| {
                let req_clone = request.clone();
                let client = client.clone();
```

## Snippet 3

Context: `sui_core/src/authority_client.rs:389` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
) -> Self {
        let client = Self::new(committee, address, secret).await;
        {
            let client_ref = client.state.as_ref().try_lock().unwrap();
            for object in objects {
                client_ref.insert_genesis_object(object).await;
            }
        }
```
After
```rust
) -> Self {
        let client = Self::new(committee, address, secret).await;

        for object in objects {
            client.state.insert_genesis_object(object).await;
        }

        client
```

## Snippet 4

Context: `sui_core/src/authority.rs:536` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
&self,
        request: BatchInfoRequest,
    ) -> Result<(VecDeque<UpdateItem>, bool), SuiError> {
        // Ensure the range contains some elements and end > start
        if request.end <= request.start {
            return Err(SuiError::InvalidSequenceRangeError);
        };
```
After
```rust
&self,
        request: BatchInfoRequest,
    ) -> Result<
        (
            VecDeque<UpdateItem>,
            // Should subscribe, computer start, computed end
            (bool, TxSequenceNumber, TxSequenceNumber),
        ),
```

# Fix Pattern

Add layered resource bounds to a streaming protocol: validate request ranges at the authority side, centralize stream range computation, and add a client-side consumption limit for overlong responses.

## How It Was Fixed

The patch moved local stream construction into AuthorityState, changed the local client path to return SuiError, added AuthorityState validation for zero-length and oversized batch ranges, and added SafeClient item-count tracking with an overlong-response guard. The genesis object insertion change appears to be cleanup or test support, not the root cause.

# Why It Matters

1. Limits work caused by malformed or excessive batch stream requests.

2. Reduces risk that a safe client processes an overlong authority response indefinitely or excessively.

3. Improves resource-control hardening in a protocol-facing streaming path.

4. Does not establish a cryptographic, authorization, or consensus-safety vulnerability.

# Evidence Notes

Grounded evidence comes from sui_core/src/safe_client.rs adding count tracking and a comment saying the guard protects against server DoS; sui_core/src/authority.rs adding request.length == 0 and request.end - request.start > MAX_ITEMS_LIMIT checks; and sui_core/src/authority_client.rs delegating to state.handle_batch_streaming(request). The heuristic claim about canonical serialization or state representation is unsupported by the provided diff and should be discarded. Remote exploitability and production impact are not proven. Protocol security invariant: Follower and safe-client batch streaming should remain bounded by the requested BatchInfoRequest window: authorities should reject empty or excessive ranges, and safe clients should stop consuming responses that exceed a reasonable multiple of the requested length. Verification notes: The patch does not prove remote exploitability against a production validator. The patch does not show a cryptographic signature, authorization, or consensus safety invariant being fixed. The genesis object insertion change appears to be state API cleanup/test support, not a security fix by itself. The gossip additions and follow-latest behavior may be protocol-relevant, but the provided evidence only concretely supports bounded streaming/resource-control hardening. The evidence does not support the heuristic claim of canonical serialization/state representation as the main bug shape. Classified as security hardening, not a confirmed security fix. Kept confidence at medium because the DoS intent is directly commented but exploitability is not demonstrated. Ignored gossip additions and genesis object insertion as unsupported root-cause evidence. No claim is made about signatures, authorization, consensus safety, or serialization correctness. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion`
Final impact type: `denial-of-service`
Final tags: `infrastructure, transaction-processing, batch-streaming, resource-control, denial-of-service, safe-client, authority`

The supplied patch evidence supports retaining this as security hardening, not a confirmed security fix. The strongest evidence is the SafeClient item-count guard with an inline comment saying it protects against server DoS, plus authority-side validation rejecting zero-length and oversized batch ranges. The evidence does not support the original serialization/state-representation framing or broader consensus, signature, or database claims.

## Security Evidence

1. SafeClient adds streamed item count tracking in the batch stream path.
2. SafeClient adds a guard for responses exceeding 10 * request.length, with a comment identifying server DoS protection.
3. Authority batch request handling adds validation for request.length == 0.
4. Authority batch request handling adds a MAX_ITEMS_LIMIT range cap.
5. Changes affect protocol-facing batch/follower streaming code paths.

## Missing Evidence

1. No demonstrated exploit or concrete production incident is shown.
2. No proof that an attacker could trigger the path remotely in a deployed configuration is supplied.
3. No evidence of consensus safety failure, signature bypass, authorization issue, or serialization bug is present.
4. No full before/after error behavior is provided for all streaming edge cases.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Limit the bug class to resource exhaustion or boundedness in batch streaming.
3. Do not claim consensus, signature, database, or canonical serialization impact from this evidence.
4. Do not claim confirmed exploitability or production compromise.
