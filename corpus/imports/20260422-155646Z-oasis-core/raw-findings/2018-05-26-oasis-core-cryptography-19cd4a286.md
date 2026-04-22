---
case_id: case_20180526_19cd4a286
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2018-05-26
source_refs:
  - git:19cd4a286faebbbc8ca7d96004f4528339ffe47f
  - "contract/trusted/src/dispatcher.rs:150"
  - "common/src/signature.rs:231"
  - "contract/trusted/src/dispatcher.rs:235"
  - "registry/dummy/src/entity.rs:92"
bug_class: signed-message-validation-consistency
impact_type:
  - request-integrity
confidence: medium
tags:
  - cryptography
  - signature
  - signed-messages
  - serialization
  - fail-closed
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch clearly tightens signed-message handling, but the provided evidence does not establish a concrete vulnerability. It shows a move toward keeping serialized signed data in the wrapper, reusing the verified call object during dispatch, and failing closed on one registry payload read.

## Observed Patch Facts

1. In `contract/trusted/src/dispatcher.rs`, the patch replaces `// Decode request method.` with `match serde_cbor::from_slice::<SignedContractCall<Generic>>(call) {`.

2. In `common/src/signature.rs`, the patch replaces `let signature = Signature::sign(signer, context, &serde_cbor::to_vec(&value).unwrap());` with `let untrusted_raw_value = serde_cbor::to_vec(&value).unwrap();`.

3. In `contract/trusted/src/dispatcher.rs`, the patch replaces `let result_decoded: ContractOutput<u32> = serde_cbor::from_slice(&result).unwrap();` with `let result_decoded: ContractOutput<Complex> = serde_cbor::from_slice(&result).unwrap();`.

4. In `registry/dummy/src/entity.rs`, the patch replaces `if entity.signature.public_key != entity.get_value_unsafe().id {` with `if entity.signature.public_key != entity.get_value_unsafe()?.id {`.

## Project Context

The changed code sits primarily in `contract/trusted/src`, `contract/trusted`, `common/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `common/src/uint.rs`, `common/src/bytes.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `common/src/uint.rs`, `common/src/bytes.rs`. The strongest project-level identifiers around this patch are `serde_cbor::from_slice`, `serde_cbor::to_vec`, `signature`, and `serde_cbor`. Nearby tests or test-like files include `registry/dummy/tests/entity.rs`, `registry/dummy/tests/contract.rs`.

## Before/After Behavior

Before the patch, the dispatcher verified a signed call and extracted only `call.method`, while `Signed<T>::sign` stored a typed value plus signature. After the patch, the dispatcher keeps the verified call object, looks up the method from `verified.get_call().method`, and passes that verified object into the handler; `Signed<T>` stores `untrusted_raw_value` plus `signature`, and `open` becomes a borrowing method. A registry entity check also changes from a direct unsafe payload read to a fallible `?` form.

# Root Cause

The code previously did not consistently carry one verified signed representation through later processing. The patch indicates that signed payload handling relied on extracted or reconstructed values in some paths instead of preserving and reusing the verified wrapper end to end.

## Walkthrough

1. `contract/trusted/src/dispatcher.rs` changes from extracting only `call.method` after `open()` to keeping `verified`, using `verified.get_call().method`, and dispatching with `method_dispatch.dispatch(verified)`.

2. `common/src/signature.rs` changes `Signed<T>::sign` to materialize `untrusted_raw_value`, sign that byte vector, and store it alongside `signature` instead of storing a typed `value` field directly.

3. The `open` API changes from consuming `self` to borrowing `&self`, consistent with the wrapper retaining internal payload state.

4. `registry/dummy/src/entity.rs` changes `entity.get_value_unsafe().id` to `entity.get_value_unsafe()?.id`, so extraction failure now aborts the identity check path.

5. The updated dispatcher test now decodes `ContractOutput<Complex>`, which supports that more of the verified call payload is carried through dispatch.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| contract/trusted/src/dispatcher.rs | 150 | trusted contract entrypoint now verifies the signed call and dispatches using the verified request rather than splitting routing from later handling |
| common/src/signature.rs | 229 | generic signed-wrapper logic now binds signatures to stored raw CBOR bytes and opens from that authenticated raw payload |
| registry/dummy/src/entity.rs | 90 | registry entity registration treats access to unsigned payload contents as fallible before checking signer-public-key to entity-id binding |

## Code Snippets

## Snippet 1

Context: `contract/trusted/src/dispatcher.rs:150` (changes signature or replay validation logic)

Before
```rust
/// Dispatches a raw contract invocation request.
    pub fn dispatch(&self, call: &Vec<u8>) -> Vec<u8> {
        // Decode request method.
        let method = match serde_cbor::from_slice::<SignedContractCall<Generic>>(call) {
            Ok(signed) => {
                // Verify signature and then get the method.
                match signed.open() {
                    Ok(call) => call.method,
```
After
```rust
/// Dispatches a raw contract invocation request.
    pub fn dispatch(&self, call: &Vec<u8>) -> Vec<u8> {
        match serde_cbor::from_slice::<SignedContractCall<Generic>>(call) {
            Ok(signed) => {
                // Verify signature and then get the method.
                match signed.open() {
                    Ok(verified) => match self.methods.get(&verified.get_call().method) {
                        Some(method_dispatch) => method_dispatch.dispatch(verified),
```

## Snippet 2

Context: `common/src/signature.rs:231` (changes signature or replay validation logic)

Before
```rust
T: Serialize,
    {
        let signature = Signature::sign(signer, context, &serde_cbor::to_vec(&value).unwrap());

        Self { value, signature }
    }

    /// Verify signature and return signed value.
```
After
```rust
T: Serialize,
    {
        let untrusted_raw_value = serde_cbor::to_vec(&value).unwrap();
        let signature = Signature::sign(signer, context, &untrusted_raw_value);

        Self {
            untrusted_raw_value,
            value: PhantomData,
```

## Snippet 3

Context: `contract/trusted/src/dispatcher.rs:235` (changes the branch that decides whether execution stops or continues)

Before
```rust
// Decode result.
        let result_decoded: ContractOutput<u32> = serde_cbor::from_slice(&result).unwrap();

        assert_eq!(result_decoded, ContractOutput::Success(42u32));
    }
}
```
After
```rust
// Decode result.
        let result_decoded: ContractOutput<Complex> = serde_cbor::from_slice(&result).unwrap();

        assert_eq!(
            result_decoded,
            ContractOutput::Success(Complex {
                text: "hello".to_owned(),
```

## Snippet 4

Context: `registry/dummy/src/entity.rs:92` (changes signature or replay validation logic)

Before
```rust
let entity_subscribers = self.entity_subscribers.clone();
        Box::new(future::lazy(move || {
            if entity.signature.public_key != entity.get_value_unsafe().id {
                return Err(Error::new("Wrong signature."));
            }
```
After
```rust
let entity_subscribers = self.entity_subscribers.clone();
        Box::new(future::lazy(move || {
            if entity.signature.public_key != entity.get_value_unsafe()?.id {
                return Err(Error::new("Wrong signature."));
            }
```

# Fix Pattern

Preserve the verified signed object through dispatch, retain serialized payload state inside the signed wrapper, and convert unchecked payload access into fail-closed handling.

## How It Was Fixed

The fix restructures signed-message handling so the signed wrapper stores serialized payload bytes, the dispatcher uses the verified call object for both method lookup and execution, and one registry identity check now treats payload extraction as fallible.

# Why It Matters

1. It reduces the chance that routing and execution observe different views of a signed request.

2. It makes malformed signed payload handling fail closed in at least one identity-binding path.

3. It strengthens consistency in a sensitive signed-message code path without proving a specific exploit.

# Evidence Notes

The strongest evidence is in `contract/trusted/src/dispatcher.rs` and `common/src/signature.rs`, with a smaller supporting change in `registry/dummy/src/entity.rs`. The snippets support signed-message hardening, but they do not show the full old/new `open` implementation, the deserialization behavior of `Signed<T>`, or a demonstrated forgery, replay, or authorization-bypass scenario. Protocol security invariant: Signed requests should be verified once and then routed and executed using that same verified representation, and failures while extracting signed contents should abort processing. Verification notes: The patch does not prove a working signature forgery against deployed code. It is not shown whether the underlying issue required CBOR malleability, ignored fields, or another deserialize/reserialize mismatch. The evidence does not establish a replay bug or nonce-handling failure. The commit does not show broader authorization bypass beyond signed-message verification consistency. The provided evidence does not prove that the old code accepted attacker-controlled invalid signatures. The snippets do not establish a replay issue or nonce-handling flaw. The exact deserialize/reserialize mismatch, if any, is not shown. The test change supports behavior change but does not by itself validate a security exploit or security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signed-message-validation-consistency`
Final impact type: `request-integrity`
Final confidence: `medium`
Final tags: `cryptography, signature, signed-messages, serialization, fail-closed`

The patch is in a security-sensitive path and clearly tightens how signed messages are represented, verified, and dispatched. It preserves the signed raw bytes inside the wrapper, reuses the verified call object for both method lookup and execution, and makes one signed-entity extraction path fail closed. That supports retaining this as security hardening, but the evidence does not prove a concrete exploitable forgery, replay, or authorization-bypass bug in the old code.

## Security Evidence

1. Signed data handling changes from storing a typed value to storing serialized raw bytes that are directly signed.
2. Dispatcher now routes and executes using the same verified call object instead of splitting out only the method name.
3. A signed-entity identity check changes from unchecked payload access to a fallible path using `?`, which is fail-closed behavior.
4. The touched code is explicitly in signature verification and trusted contract dispatch paths.

## Missing Evidence

1. The old and new `open` implementations are not shown, so the exact verification/deserialization flaw is not proven.
2. No patch evidence shows that invalid signatures were previously accepted in practice.
3. No nonce, sequence, or duplicate-message handling is shown, so replay should not be claimed.
4. No exploit, regression test, or advisory demonstrates a concrete security impact beyond hardening.

## Claim Boundaries

1. This supports signed-message validation hardening, not a proven exploitable vulnerability.
2. Do not label this as a confirmed replay fix from the provided patch alone.
3. Do not claim request forgery or authorization bypass without stronger evidence.
4. The strongest justified claim is improved consistency and fail-closed behavior in signature-sensitive code.
