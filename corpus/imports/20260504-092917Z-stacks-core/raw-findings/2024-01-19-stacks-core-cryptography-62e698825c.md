---
case_id: case_20240119_62e698825c
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2024-01-19
source_refs:
  - git:62e698825ce1487ea27ea02c62017e2afbc7b887
  - "stacks-signer/src/runloop.rs:447"
  - "stacks-signer/src/runloop.rs:346"
  - "stacks-signer/src/runloop.rs:316"
  - "stacks-signer/src/client/stackerdb.rs:105"
bug_class: signer-request-validation-hardening
impact_type:
  - invalid-signing-request-rejection
confidence: medium
tags:
  - validator-ops
  - cryptography
  - signer-protocol
  - signature-request-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to add signer-side validation and rejection reporting around block signing flow, but the provided evidence does not establish a concrete vulnerability or exploit path. The strongest grounded changes are that `SignatureShareRequest` handling now calls `validate_signature_share_request()` and drops invalid requests, and miner block proposals with invalid signature hashes now produce a `BlockRejection` with `RejectCode::InvalidSignatureHash`. This may be security relevant, but it is not enough to classify as a confirmed or likely vulnerability fix.

## Observed Patch Facts

1. In `stacks-signer/src/runloop.rs`, the patch replaces `// A coordinator could have sent a signature share request with a different message t...` with `if !self.validate_signature_share_request(request) {`.

2. In `stacks-signer/src/runloop.rs`, the patch replaces `/// Helper function to verify a chunk is a valid wsts packet.` with `/// Helper function to validate a signature share request, updating its message where...`.

3. In `stacks-signer/src/runloop.rs`, the patch replaces `//TODO: trigger the signing round here instead. Then deserialize the block and call t...` with `let Ok(hash) = block.header.signature_hash() else {`.

4. In `stacks-signer/src/client/stackerdb.rs`, the patch replaces `/// Missing expected transactions` with `/// Signers signed a block rejection`.

## Project Context

The changed code sits primarily in `stacks-signer/src`, `stacks-signer/src/client`, which anchors the finding in the `cryptography` area of the project. Historical context from `stacks-signer/src/config.rs`, `stacks-signer/src/client/stacks_client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stacks-signer/src/main.rs`, `stacks-signer/src/config.rs`. The strongest project-level identifiers around this patch are `block`, `message`, `signature`, and `with`. Nearby tests or test-like files include `stacks-signer/src/tests/mod.rs`, `stacks-signer/src/tests/config.rs`.

## Before/After Behavior

Before the patch, `verify_chunk` accepted a verified WSTS packet and for `SignatureShareRequest` only overwrote `request.message` from `self.messages.remove(&request.sign_id)` when present before returning `Some(packet)`. After the patch, it calls `validate_signature_share_request(request)` and returns `None` if that helper fails. Before the patch, miner block proposal handling deserialized a `NakamotoBlock` and submitted it for validation. After the patch, it first computes `block.header.signature_hash()`; if that fails, it broadcasts a `BlockRejection` with `RejectCode::InvalidSignatureHash` and skips further processing.

# Root Cause

The evidence supports a narrower root cause: prior handling did not show an explicit rejection path in `verify_chunk` for `SignatureShareRequest` values that fail the new signer-side validation, and invalid block signature hashes were not shown being converted into broadcast rejection messages before validation submission. It does not prove arbitrary signing, replay, consensus failure, or funds loss.

## Walkthrough

1. A miner block proposal is read from a stackerdb chunk as a `NakamotoBlock`.

2. The patched code computes the block signature hash before caching or submitting the block for validation.

3. If hash computation fails, the signer creates a `BlockRejection` with `RejectCode::InvalidSignatureHash`, sends it through stackerdb with retry, and continues to the next chunk.

4. For WSTS packets, `verify_chunk` still first verifies the packet against signing-round and coordinator keys.

5. For `Message::SignatureShareRequest`, the old code conditionally overwrote the request message from a `sign_id` lookup and then accepted the packet.

6. The patched code delegates to `validate_signature_share_request`; if it returns false, the packet is dropped.

7. The evidence shows the helper consulting cached block/vote state and documenting that it may overwrite the message with the signer's agreed value, but the full decision tree is not provided.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stacks-signer/src/runloop.rs | 346 | validates SignatureShareRequest messages against cached block/vote state and rewrites or rejects mismatched signing requests |
| stacks-signer/src/runloop.rs | 435 | filters verified WSTS packets before signer processing, now rejecting invalid signature share requests |
| stacks-signer/src/runloop.rs | 311 | handles miner block proposal chunks, computes signature hash, caches valid blocks, and broadcasts invalid-hash block rejections |
| stacks-signer/src/client/stackerdb.rs | 105 | defines block rejection reason codes used when broadcasting signer rejection results |

## Code Snippets

## Snippet 1

Context: `stacks-signer/src/runloop.rs:447` (changes signature or replay validation logic)

Before
```rust
match &mut packet.msg {
                Message::SignatureShareRequest(request) => {
                    // A coordinator could have sent a signature share request with a different message than we agreed to sign
                    // Either another message won majority or the coordinator is trying to cheat...Overwrite with our agreed upon value
                    if let Some(message) = self.messages.remove(&request.sign_id) {
                        request.message = message;
                    }
                    Some(packet)
```
After
```rust
match &mut packet.msg {
                Message::SignatureShareRequest(request) => {
                    if !self.validate_signature_share_request(request) {
                        return None;
                    }
                }
                Message::NonceRequest(request) => {
                    if !self.validate_nonce_request(request) {
```

## Snippet 2

Context: `stacks-signer/src/runloop.rs:346` (changes signature or replay validation logic)

Before
```rust
}

    /// Helper function to verify a chunk is a valid wsts packet.
    /// Note if the chunk is a NonceRequest for a block proposal, we will sign the block hash with an optional byte indicating a vote no if appropriate.
    fn verify_chunk(
        &mut self,
```
After
```rust
}

    /// Helper function to validate a signature share request, updating its message where appropriate.
    /// If the request is for a block it has already agreed to sign, it will overwrite the message with the agreed upon value
    /// Returns whether the request is valid or not.
    fn validate_signature_share_request(&self, request: &mut SignatureShareRequest) -> bool {
        // A coordinator could have sent a signature share request with a different message than we agreed to sign
        match self
```

## Snippet 3

Context: `stacks-signer/src/runloop.rs:316` (changes signature or replay validation logic)

Before
```rust
continue;
            };
            //TODO: trigger the signing round here instead. Then deserialize the block and call the validation as you validate its contents
            // https://github.com/stacks-network/stacks-core/issues/3930
            // Received a block proposal from the miner. Submit it for verification.
            self.stacks_client
                .submit_block_for_validation(block)
```
After
```rust
continue;
            };
            let Ok(hash) = block.header.signature_hash() else {
                warn!("Received a block proposal with an invalid signature hash. Broadcasting a block rejection...");
                let block_rejection = BlockRejection::new(block, RejectCode::InvalidSignatureHash);
                    // Submit signature result to miners to observe
                    if let Err(e) = self
                    .stackerdb
```

## Snippet 4

Context: `stacks-signer/src/client/stackerdb.rs:105` (changes an authorization or privilege gate)

Before
```rust
/// RPC endpoint Validation failed
    ValidationFailed(ValidateRejectCode),
    /// Missing expected transactions
    MissingTransactions(Vec<Txid>),
}
```
After
```rust
/// RPC endpoint Validation failed
    ValidationFailed(ValidateRejectCode),
    /// Signers signed a block rejection
    SignedRejection,
    /// Invalid signature hash
    InvalidSignatureHash,
}
```

# Fix Pattern

Add explicit validation before accepting signer protocol requests, and add structured rejection reporting for invalid block proposal signature hashes.

## How It Was Fixed

`SignatureShareRequest` handling was factored into `validate_signature_share_request`, and `verify_chunk` now rejects the packet when that helper returns false. Miner block proposal handling now checks `block.header.signature_hash()` before caching or validation submission, and broadcasts a `BlockRejection` using the new `RejectCode::InvalidSignatureHash` when the hash is invalid. `RejectCode::SignedRejection` was also added, but the provided evidence does not show its complete use.

# Why It Matters

1. Prevents at least some invalid signature-share requests from continuing through signer processing.

2. Makes invalid block signature hashes observable through structured rejection messages.

3. May improve signer protocol robustness and diagnostics.

4. Does not, on the supplied evidence, establish an exploitable security flaw.

# Evidence Notes

Evidence is limited to excerpts from `stacks-signer/src/runloop.rs` and `stacks-signer/src/client/stackerdb.rs`. The comments mention a coordinator possibly sending a different message than agreed, which is security-relevant, but the full validation logic and tests are not shown. The commit subject emphasizes broadcasting block submissions in failure and success cases, which also supports a liveness or observability interpretation. Claims of replay protection, arbitrary signing prevention, consensus violation, or funds impact are unsupported. Protocol security invariant: A signer should only continue processing WSTS signature-share requests that pass signer-side validation against its known block or vote state, and block proposals whose signature hash cannot be computed should be rejected rather than cached or submitted as valid candidates. Verification notes: The patch does not prove that an attacker could force signers to sign an arbitrary block. The patch does not prove a replay attack; nonce handling is only partially visible in the provided evidence. The patch does not prove consensus violation or funds loss. The patch may also serve liveness/observability by broadcasting rejection outcomes, not only security enforcement. The provided evidence does not show the full validate_signature_share_request decision tree. No full `validate_signature_share_request` implementation was provided. No exploit scenario or failing pre-patch test was provided. No evidence was provided that old behavior led to consensus failure or unauthorized signatures. Treat as possibly security-relevant hardening, not a validated vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signer-request-validation-hardening`
Final impact type: `invalid-signing-request-rejection`
Final confidence: `medium`
Final tags: `validator-ops, cryptography, signer-protocol, signature-request-validation, security-hardening`

The patch evidence does not prove a concrete exploitable vulnerability, but it does show a clear tightening in a security-sensitive signer protocol path: verified WSTS SignatureShareRequest packets are now passed through explicit signer-side validation and dropped on failure, with comments describing a coordinator sending a different message than the signer agreed to sign. The invalid block signature hash rejection path is weaker evidence by itself and could be observability or liveness work, but the signature-share validation change supports retaining this as security hardening rather than a confirmed security fix.

## Security Evidence

1. SignatureShareRequest handling now calls validate_signature_share_request and returns None when validation fails.
2. The new helper is documented as validating signer requests against already-agreed block/vote state and overwriting only where appropriate.
3. Patch comments explicitly describe a coordinator possibly sending a different message than agreed or trying to cheat.
4. The code path is in signer/WSTS packet processing after packet verification, making it security-sensitive.

## Missing Evidence

1. No full validate_signature_share_request decision tree is provided.
2. No exploit scenario, advisory, CVE, or failing pre-patch regression test is shown.
3. No evidence proves arbitrary signing, replay, consensus failure, or funds impact.
4. The commit subject emphasizes broadcast behavior, which may indicate product reliability or observability work.

## Claim Boundaries

1. Classify as security hardening, not a confirmed vulnerability fix.
2. Do not claim proven replay prevention from the supplied evidence.
3. Do not claim unauthorized block signing was possible before the patch.
4. Treat invalid signature hash broadcasting as supporting context, not the primary security basis.
