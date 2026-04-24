---
case_id: case_20220206_db9ee35c05
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2022-02-06
source_refs:
  - git:db9ee35c05d3a5351151fb56f0d080b2ed3c46e2
  - "fastpay_core/src/authority_aggregator.rs:320"
  - "fastpay_core/src/authority/authority_store.rs:420"
  - "fastpay_core/src/authority_aggregator.rs:109"
  - "fastx_types/src/messages.rs:164"
bug_class: byzantine-authority-robustness
impact_type:
  - availability
  - sync-integrity
confidence: medium
tags:
  - blockchain-core
  - authority-aggregation
  - byzantine-fault-tolerance
  - client-authority-sync
  - availability-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The draft's staking and confirmed vulnerability framing is unsupported. The patch is best described as a FastPay client-authority synchronization robustness and API semantics change: it adds generic authority map/reduce logic, changes ObjectInfoResponse semantics, records deleted-object state in parent_sync, and avoids unconditionally expecting an optional parent_certificate in one query path. The evidence may be security relevant in a Byzantine-authority system, but it does not prove a vulnerability fix.

## Observed Patch Facts

1. In `fastpay_core/src/authority_aggregator.rs`, the patch replaces `#[cfg(test)]` with `/// This function takes an initial state, than executes an asynchronous function (FMa...`.

2. In `fastpay_core/src/authority/authority_store.rs`, the patch adds `/// Returns the last entry we have for this object in the parents_sync index used`.

3. In `fastpay_core/src/authority_aggregator.rs`, the patch replaces `if let Ok(response) = result {` with `if let Ok(ObjectInfoResponse {`.

4. In `fastx_types/src/messages.rs`, the patch replaces `/// If no parent certificate was requested this is set to None. If the` with `/// If no parent certificate was requested the latest certificate concerning`.

## Project Context

The changed code sits primarily in `fastpay_core/src`, `fastpay_core/src/authority`, `fastx_types/src`, which anchors the finding in the `staking` area of the project. Historical context from `fastpay_core/src/authority.rs`, `fastx_types/src/object.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `fastpay_core/src/authority.rs`, `fastx_types/src/error.rs`. The strongest project-level identifiers around this patch are `certificate`, `object`, `result`, and `function`. Nearby tests or test-like files include `fastpay_core/src/unit_tests/client_tests.rs`, `fastpay_core/src/unit_tests/authority_tests.rs`.

## Before/After Behavior

Before the patch, one object-info query path accepted any successful ObjectInfoResponse and then unconditionally called expect on parent_certificate before checking the certificate. After the patch, that path only proceeds when parent_certificate is Some(certificate), then checks the certificate against the committee. ObjectInfoResponse documentation changed from saying parent_certificate is None when no parent was requested to saying the latest certificate concerning the object is returned, with requested_object_reference added. AuthorityStore gained documented parent_sync lookup semantics for latest object references and deleted-object entries. AuthorityAggregator gained a generic async map/reduce helper that can continue across per-authority errors or time out adaptively.

# Root Cause

The supported root cause is brittle or incomplete client-authority synchronization semantics around optional certificates, latest object references, and deleted-object history. The evidence does not establish a concrete exploit path, state-corruption vulnerability, access-control bypass, double-spend, or consensus safety failure.

## Walkthrough

1. A client queries authorities for object information.

2. In the old query path, a successful response without parent_certificate would trigger an expect failure before any useful handling of that response shape.

3. The patched query path ignores successful responses unless they contain Some(certificate).

4. Any accepted certificate is checked against the committee, as in the previous path after the expect.

5. ObjectInfoResponse semantics are changed so a request without a specific parent can return the latest certificate concerning the object.

6. The response now includes requested_object_reference to identify the object reference created by the certificate.

7. AuthorityStore documents parent_sync latest-entry lookup behavior, including deleted-object entries using ObjectDigest::deleted() and the deleting certificate transaction digest.

8. The new authority map/reduce abstraction allows aggregation logic to consume individual authority errors and continue or time out.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| fastpay_core/src/authority_aggregator.rs | 320 | generic async map/reduce over authorities with per-authority error handling and adaptive continuation/timeout semantics |
| fastpay_core/src/authority_aggregator.rs | 109 | object-info query path now only accepts present parent certificates and checks them against the committee instead of unconditionally expecting one |
| fastpay_core/src/authority/authority_store.rs | 420 | parent_sync lookup now represents latest object reference and certificate history, including deleted-object entries |
| fastx_types/src/messages.rs | 164 | ObjectInfoResponse semantics now include latest parent certificate and requested object reference for the object |

## Code Snippets

## Snippet 1

Context: `fastpay_core/src/authority_aggregator.rs:320` (changes an authorization or privilege gate)

Before
```rust
}

    #[cfg(test)]
    async fn request_certificate(
```
After
```rust
}

    /// This function takes an initial state, than executes an asynchronous function (FMap) for each
    /// uthority, and folds the results as they become available into the state using an async function (FReduce).
    ///
    /// FMap can do io, and returns a result V. An error there may not be fatal, and could be consumed by the
    /// MReduce function to overall recover from it. This is necessary to ensure byzantine authorities cannot
    /// interupt the logic of this function.
```

## Snippet 2

Context: `fastpay_core/src/authority/authority_store.rs:420` (changes a sensitive control or state-update path)

Before
```rust
})
    }
}
```
After
```rust
})
    }

    /// Returns the last entry we have for this object in the parents_sync index used
    /// to facilitate client and authority sync. In turn the latest entry provides the
    /// latest object_reference, and also the latest tranaction that has interacted with
    /// this object.
    ///
```

## Snippet 3

Context: `fastpay_core/src/authority_aggregator.rs:109` (changes the branch that decides whether execution stops or continues)

Before
```rust
for client in self.authority_clients.iter_mut() {
            let result = client.handle_object_info_request(request.clone()).await;
            if let Ok(response) = result {
                let certificate = response
                    .parent_certificate
                    .expect("Unable to get certificate");
                if certificate.check(&self.committee).is_ok() {
                    // BUG (https://github.com/MystenLabs/fastnft/issues/290): Orders do not have a sequence number any more, objects do.
```
After
```rust
for client in self.authority_clients.iter_mut() {
            let result = client.handle_object_info_request(request.clone()).await;
            if let Ok(ObjectInfoResponse {
                parent_certificate: Some(certificate),
                ..
            }) = result
            {
                if certificate.check(&self.committee).is_ok() {
```

## Snippet 4

Context: `fastx_types/src/messages.rs:164` (changes a sensitive control or state-update path)

Before
```rust
pub struct ObjectInfoResponse {
    /// The certificate that created or mutated the object at a given version.
    /// If no parent certificate was requested this is set to None. If the
    /// parent was requested and not found a error (ParentNotfound or
    /// CertificateNotfound) will be returned.
    pub parent_certificate: Option<CertifiedOrder>,

    /// The object and its current lock. If the object does not exist
```
After
```rust
pub struct ObjectInfoResponse {
    /// The certificate that created or mutated the object at a given version.
    /// If no parent certificate was requested the latest certificate concerning
    /// this object is sent. If the parent was requested and not found a error
    /// (ParentNotfound or CertificateNotfound) will be returned.
    pub parent_certificate: Option<CertifiedOrder>,
    /// The full reference created by the above certificate
    pub requested_object_reference: Option<ObjectRef>,
```

# Fix Pattern

Make synchronization semantics explicit and tolerate incomplete or failing per-authority responses instead of assuming every successful response has the same optional fields populated.

## How It Was Fixed

The patch updates ObjectInfoResponse semantics and fields, documents parent_sync latest-entry behavior for live and deleted objects, changes the object-info query path to pattern-match only responses with a parent certificate, and adds a generic map/reduce helper for querying authorities with reducer-controlled continuation and timeout behavior.

# Why It Matters

1. Improves robustness of object synchronization against incomplete authority responses.

2. Makes deleted-object history visible in the same sync index used for latest object state.

3. Reduces reliance on panicking or aborting when an optional certificate is absent.

4. May matter in a Byzantine-authority model, but exploitability is not shown.

# Evidence Notes

Supported evidence comes from fastpay_core/src/authority_aggregator.rs around the object-info query and new map/reduce comments, fastpay_core/src/authority/authority_store.rs parent_sync comments, and fastx_types/src/messages.rs ObjectInfoResponse comments and requested_object_reference addition. The evidence does not support the heuristic baseline's staking subsystem, state-corruption bug class, or high confidence. It also does not support keeping this as a confirmed security fix in a vulnerability corpus. Protocol security invariant: Clients synchronizing object state from authorities should be able to recover certified latest object history, including deleted-object state, without a single malformed, incomplete, or failing authority response aborting progress. The supplied evidence shows changes in this direction, but does not establish that the previous behavior violated a security invariant in an exploitable way. Verification notes: No exploitability is proven by the provided patch evidence. No direct access-control bypass is shown. No asset theft, double-spend, or consensus safety violation is demonstrated. Some changes are API and synchronization semantics rather than a narrowly identified bug fix. The heuristic baseline's staking subsystem label is not supported by the provided file paths or traced context. No direct exploit scenario is provided. No test evidence in the supplied input demonstrates a prevented attack. No asset theft, double-spend, authorization bypass, or consensus break is demonstrated. The Byzantine-authority comment supports possible security relevance, but not a validated vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `byzantine-authority-robustness`
Final impact type: `availability, sync-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, authority-aggregation, byzantine-fault-tolerance, client-authority-sync, availability-hardening`

The evidence does not support a confirmed vulnerability, staking subsystem, or state-corruption claim. However, the patch explicitly frames the new authority map/reduce behavior as needed so Byzantine authorities cannot interrupt client logic, and it changes object-info handling to tolerate missing parent certificates instead of panicking. In a blockchain authority/client synchronization path, that is enough to retain as security hardening, not a concrete security fix.

## Security Evidence

1. New authority aggregation helper is documented as allowing per-authority errors to be consumed so Byzantine authorities cannot interrupt the logic.
2. Object-info query path no longer unwraps parent_certificate with expect; it only proceeds when a checked certificate is present.
3. ObjectInfoResponse and parent_sync semantics are expanded to expose latest object references and deleted-object certificate history for synchronization.

## Missing Evidence

1. No exploit scenario, attack test, advisory, or demonstrated asset/state compromise is provided.
2. No evidence shows a consensus safety break, double-spend, authorization bypass, or concrete state-corruption vulnerability.
3. The patch includes broad robustness and API semantics work, so not all changes are security-specific.

## Claim Boundaries

1. Classify as security-hardening for adversarial authority tolerance, not as a proven security-fix.
2. Do not retain the original staking label; changed files point to FastPay authority/client synchronization.
3. Do not claim state corruption or state-integrity impact beyond conservative sync-integrity hardening.
