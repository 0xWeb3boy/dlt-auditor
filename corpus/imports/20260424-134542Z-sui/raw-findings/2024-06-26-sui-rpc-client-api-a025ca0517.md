---
case_id: case_20240626_a025ca0517
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: medium
source_quality: medium
date: 2024-06-26
source_refs:
  - git:a025ca0517c9dc45a38617d78f6ea1624dd9eee6
  - "crates/sui-core/src/authority_server.rs:937"
  - "crates/sui-core/src/authority_server.rs:678"
  - "crates/sui-core/src/authority_server.rs:712"
  - "crates/sui-core/src/authority_server.rs:478"
bug_class: traffic-control-accounting-gap
impact_type:
  - resource-abuse
  - resource-exhaustion
tags:
  - blockchain-core
  - traffic-controller
  - anti-abuse
  - spam-accounting
  - resource-accounting
  - validator
  - rpc
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is traffic-controller security hardening, not serialization or state-representation repair. The patch threads an explicit spam/accounting weight through authority service responses so successful gasless work can be counted by traffic-control logic.

## Observed Patch Facts

1. In `crates/sui-core/src/authority_server.rs`, the patch replaces `response: &Result<tonic::Response<T>, tonic::Status>,` with `wrapped_response: WrappedServiceResponse<T>,`.

2. In `crates/sui-core/src/authority_server.rs`, the patch replaces `.map(|v| {` with `.map(|(resp, spam_weight)| {`.

3. In `crates/sui-core/src/authority_server.rs`, the patch replaces `.map(|v| {` with `.map(|(resp, spam_weight)| {`.

4. In `crates/sui-core/src/authority_server.rs`, the patch replaces `return Ok(Some(vec![HandleCertificateResponseV3 {` with `return Ok((`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `crates/sui-core/src/consensus_throughput_calculator.rs`, `crates/sui-core/src/authority_client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/consensus_throughput_calculator.rs`, `crates/sui-core/src/authority_client.rs`. The strongest project-level identifiers around this patch are `tonic::Response::new`, `tonic`, `None`, and `tonic::Response`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/consensus_tests.rs`, `crates/sui-core/src/unit_tests/transfer_to_object_tests.rs`.

## Before/After Behavior

Before the patch, the shown response handling accepted a plain RPC result and derived only an optional error from success or failure status. Certificate handlers built tonic responses from returned payloads, and the already-executed certificate path returned only response data. After the patch, these paths use wrapped responses or tuples carrying both the response payload and a Weight, and handle_traffic_resp extracts the spam_weight for traffic-controller accounting while preserving normal RPC success/error behavior.

# Root Cause

The traffic-controller boundary did not receive an explicit weight from successful gasless business-logic paths. In particular, certificate handling paths that could return already-computed effects without VM execution returned response data without carrying the accounting signal now needed to classify that work as spam-relevant.

## Walkthrough

1. A validator handles certificate requests through the authority service.

2. The request enters certificate handling after transaction validity checks.

3. If the certificate was already executed, the handler can read and return existing signed effects rather than invoking VM execution.

4. Before the patch, the supplied snippets show this successful path returning only payload data up to the RPC response builder.

5. The patch changes certificate handling to return a payload plus Weight.

6. The v2 and v3 certificate response builders preserve the returned spam_weight while constructing tonic responses.

7. handle_traffic_resp now unwraps WrappedServiceResponse into error information, spam_weight, and the final RPC result for traffic-controller accounting.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority_server.rs | 936 | unwraps `WrappedServiceResponse` into response, error, and explicit spam weight for traffic-controller accounting |
| crates/sui-core/src/authority_server.rs | 660 | propagates spam weight from certificate handling through handle_certificate_v2 response construction |
| crates/sui-core/src/authority_server.rs | 694 | propagates spam weight from certificate handling through handle_certificate_v3 response construction |
| crates/sui-core/src/authority_server.rs | 425 | business-logic path for certificate handling, including already-executed certificate fast path that returns effects without VM execution |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/authority_server.rs:937` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
&self,
        client: Option<IpAddr>,
        response: &Result<tonic::Response<T>, tonic::Status>,
    ) {
        let error: Option<SuiError> = if let Err(status) = response {
            Some(SuiError::from(status.clone()))
        } else {
            None
```
After
```rust
&self,
        client: Option<IpAddr>,
        wrapped_response: WrappedServiceResponse<T>,
    ) -> Result<tonic::Response<T>, tonic::Status> {
        let (error, spam_weight, unwrapped_response) = match wrapped_response {
            Ok((result, spam_weight)) => (None, spam_weight.clone(), Ok(result)),
            Err(status) => (
                Some(SuiError::from(status.clone())),
```

## Snippet 2

Context: `crates/sui-core/src/authority_server.rs:678` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
.instrument(span)
        .await
        .map(|v| {
            tonic::Response::new(
                v.expect("handle_certificate should not return none with wait_for_effects=true")
                    .remove(0)
                    .into(),
            )
```
After
```rust
.instrument(span)
        .await
        .map(|(resp, spam_weight)| {
            (
                tonic::Response::new(
                    resp.expect(
                        "handle_certificate should not return none with wait_for_effects=true",
                    )
```

## Snippet 3

Context: `crates/sui-core/src/authority_server.rs:712` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
.instrument(span)
        .await
        .map(|v| {
            tonic::Response::new(
                v.expect("handle_certificate should not return none with wait_for_effects=true")
                    .remove(0),
            )
        })
```
After
```rust
.instrument(span)
        .await
        .map(|(resp, spam_weight)| {
            (
                tonic::Response::new(
                    resp.expect(
                        "handle_certificate should not return none with wait_for_effects=true",
                    )
```

## Snippet 4

Context: `crates/sui-core/src/authority_server.rs:478` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
};

                return Ok(Some(vec![HandleCertificateResponseV3 {
                    effects: signed_effects.into_inner(),
                    events,
                    input_objects: None,
                    output_objects: None,
                    auxiliary_data: None,
```
After
```rust
};

                return Ok((
                    Some(vec![HandleCertificateResponseV3 {
                        effects: signed_effects.into_inner(),
                        events,
                        input_objects: None,
                        output_objects: None,
```

# Fix Pattern

Propagate explicit resource-abuse accounting metadata from business logic to the traffic-controller boundary instead of inferring spam solely from RPC success or error status.

## How It Was Fixed

Authority service response types and mappings were changed to carry `(response, spam_weight)` values. `handle_traffic_resp` now matches `WrappedServiceResponse<T>`, extracts `spam_weight` on success, uses zero weight on error in the shown code, and returns the unwrapped tonic result. Certificate handlers and the already-executed certificate path were updated to preserve this tuple shape.

# Why It Matters

1. Gasless requests can still consume node resources.

2. Successful requests need accounting, not only failed ones.

3. Already-executed certificate submissions can avoid VM execution but still cause read/response work.

4. The evidence supports anti-abuse accounting hardening, not consensus failure, authorization bypass, or state corruption.

# Evidence Notes

Direct support comes from the supplied `authority_server.rs` snippets around `handle_traffic_resp`, `handle_certificate_v2_impl`, `handle_certificate_v3_impl`, and `handle_certificates`, plus commit metadata stating the PR redefines spam for traffic controller as request types that do not consume gas. The heuristic baseline's RPC serialization/state-representation theory is unsupported and should be discarded. The evidence does not prove exploitability, economic loss, consensus failure, or incorrect transaction execution. Protocol security invariant: Traffic-control accounting should classify successful requests that consume validator or node resources without consuming gas, so gasless read/API paths and already-executed certificate submissions remain visible to throttling or spam policy. Verification notes: The patch does not prove a remotely exploitable denial-of-service condition by itself. The patch does not show incorrect transaction execution, consensus safety failure, or state corruption. The patch does not show authentication or authorization bypass. The evidence does not prove economic loss; it only shows corrected classification/accounting for gasless resource use. The heuristic baseline's RPC serialization framing is not supported by the commit description and should not drive classification. Reviewed only the provided snippets and metadata. No external repository or command output was used. Security classification is downgraded from confirmed to likely because exploitability is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `traffic-control-accounting-gap`
Final impact type: `resource-abuse, resource-exhaustion`
Final tags: `blockchain-core, traffic-controller, anti-abuse, spam-accounting, resource-accounting, validator, rpc`

The supplied evidence supports retaining this as security hardening for anti-abuse accounting. The commit description explicitly frames the change as redefining spam for gasless request types, and the patch threads explicit spam weights through successful authority service responses so traffic-control logic can account for requests that consume node resources without consuming gas. The evidence does not support the original serialization/state-consistency framing or prove a concrete exploitable denial-of-service bug, so the corpus metadata should be narrowed.

## Security Evidence

1. Commit states traffic controller spam classification is being changed for request types that do not consume gas.
2. Authority service responses now carry a spam_weight alongside successful RPC response payloads.
3. handle_traffic_resp extracts spam_weight for traffic-controller accounting instead of deriving only error information from the RPC result.
4. Already-executed certificate handling now returns response data together with a Weight, covering a gasless read-and-return path.

## Missing Evidence

1. No proof that the previous behavior enabled a practical remote denial-of-service attack.
2. No demonstrated bypass threshold, attacker workflow, or resource exhaustion measurement is provided.
3. No evidence of consensus failure, state corruption, authorization bypass, or client-view divergence.
4. Only selected snippets are supplied, so the full traffic-controller policy effect is inferred from metadata and changed types.

## Claim Boundaries

1. Classify as anti-abuse traffic-control hardening, not a confirmed vulnerability fix.
2. Do not claim serialization, canonical state representation, or state consistency repair.
3. Do not claim economic loss, consensus compromise, or incorrect transaction execution.
4. Supported claim is limited to improved accounting/classification of successful gasless validator/RPC work.
