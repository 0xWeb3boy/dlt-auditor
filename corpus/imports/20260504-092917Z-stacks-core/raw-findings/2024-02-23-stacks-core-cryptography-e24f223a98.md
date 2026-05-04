---
case_id: case_20240223_e24f223a98
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2024-02-23
source_refs:
  - git:e24f223a9815ccf5a23c3ca0653b3949aa9831ea
  - "stacks-signer/src/signer.rs:1163"
  - "stacks-signer/src/signer.rs:529"
  - "stacks-signer/src/signer.rs:1127"
  - "stackslib/src/chainstate/nakamoto/mod.rs:343"
bug_class: signer-vote-message-validation
impact_type:
  - signer-vote-integrity
  - consensus-adjacent-integrity
confidence: medium
tags:
  - validator-ops
  - cryptography
  - consensus
  - signature
  - message-validation
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch replaces an implicit signer vote encoding based on raw 32-byte hashes, 33-byte hash-plus-marker messages, and first-32-byte slicing with an explicit serialized `NakamotoBlockVote` containing `signer_signature_hash` and `rejected`. This is plausibly security-relevant because it touches signer vote validation and signature result handling, but the supplied evidence does not establish an exploitable vulnerability, consensus break, signature forgery, or threshold-signature bypass.

## Observed Patch Facts

1. In `stacks-signer/src/signer.rs`, the patch replaces `let block = read_next::<NakamotoBlock, _>(&mut &message[..]).ok().unwrap_or({` with `// We do not sign across blocks, but across their hashes. however, the first sign req...`.

2. In `stacks-signer/src/signer.rs`, the patch replaces `let message_len = request.message.len();` with `let Some(block_vote): Option<NakamotoBlockVote> = read_next(&mut &request.message[..]...`.

3. In `stacks-signer/src/signer.rs`, the patch replaces `let Some(aggregate_public_key) = &self.coordinator.get_aggregate_public_key() else {` with `let message = self.coordinator.get_message();`.

4. In `stackslib/src/chainstate/nakamoto/mod.rs`, the patch replaces `pub struct NakamotoBlock {` with `/// A vote across the signer set for a block`.

## Project Context

The changed code sits primarily in `stacks-signer/src`, `stackslib/src/chainstate/nakamoto`, `stackslib/src/chainstate`, which anchors the finding in the `cryptography` area of the project. Historical context from `stacks-signer/src/coordinator.rs`, `stackslib/src/chainstate/nakamoto/tenure.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stackslib/src/chainstate/nakamoto/tenure.rs`, `stackslib/src/chainstate/nakamoto/signer_set.rs`. The strongest project-level identifiers around this patch are `message`, `block`, `hash`, and `signature`. Nearby tests or test-like files include `stackslib/src/chainstate/stacks/tests/block_construction.rs`, `stackslib/src/chainstate/nakamoto/tests/mod.rs`.

## Before/After Behavior

Before the patch, signer vote handling inferred message meaning from byte length and marker conventions: 32-byte messages were treated as block hashes, 33-byte messages ending in `b'n'` represented a rejection variant, and result/error paths recovered a hash by slicing the first 32 bytes from longer messages. After the patch, signer request validation, signature processing, and signing-error processing deserialize `NakamotoBlockVote`; non-block-vote streams are rejected or ignored in the shown paths, with a full-block first-sign-request case still handled separately.

# Root Cause

The previous implementation used an implicit and overloaded byte-level encoding for signer votes. The provided evidence supports a correctness and robustness issue in message interpretation, but not a demonstrated security root cause.

## Walkthrough

1. `validate_signature_share_request` previously accepted messages that matched expected raw byte lengths and marker conventions.

2. `process_signature` and `process_sign_error` previously derived the relevant block hash from coordinator messages by taking the first 32 bytes when needed.

3. The patch introduces `NakamotoBlockVote` with `signer_signature_hash` and `rejected` fields.

4. `validate_signature_share_request` now attempts to deserialize the request message as `NakamotoBlockVote` and rejects unknown streams.

5. `process_signature` now requires a block-vote message before proceeding with signature result handling and removes tracked state by `block_vote.signer_signature_hash`.

6. `process_sign_error` still supports the first sign request as a full block, then parses later messages as `NakamotoBlockVote` instead of slicing arbitrary message bytes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stacks-signer/src/signer.rs | 529 | validates inbound signature share requests and now rejects non-NakamotoBlockVote message streams |
| stacks-signer/src/signer.rs | 1127 | processes completed signatures and maps the signed vote back to the tracked block hash |
| stacks-signer/src/signer.rs | 1163 | processes signing errors and recovers the associated block via block vote parsing |
| stackslib/src/chainstate/nakamoto/mod.rs | 343 | defines the serialized NakamotoBlockVote carrying signer_signature_hash and rejection state |

## Code Snippets

## Snippet 1

Context: `stacks-signer/src/signer.rs:1163` (changes a sensitive control or state-update path)

Before
```rust
fn process_sign_error(&mut self, e: &SignError) {
        let message = self.coordinator.get_message();
        let block = read_next::<NakamotoBlock, _>(&mut &message[..]).ok().unwrap_or({
                // This is not a block so maybe its across its hash
                // This jankiness is because a coordinator could have signed a rejection we need to find the underlying block hash
                let signer_signature_hash_bytes = if message.len() > 32 {
                    &message[..32]
                } else {
```
After
```rust
fn process_sign_error(&mut self, e: &SignError) {
        let message = self.coordinator.get_message();
        // We do not sign across blocks, but across their hashes. however, the first sign request is always across the block
        // so we must handle this case first

        let block: NakamotoBlock = read_next(&mut &message[..]).ok().unwrap_or({
            // This is not a block so maybe its across its hash
            let Some(block_vote): Option<NakamotoBlockVote> = read_next(&mut &message[..]).ok() else {
```

## Snippet 2

Context: `stacks-signer/src/signer.rs:529` (changes signature or replay validation logic)

Before
```rust
/// Returns whether the request is valid or not.
    fn validate_signature_share_request(&self, request: &mut SignatureShareRequest) -> bool {
        let message_len = request.message.len();
        // Note that the message must always be either 32 bytes (the block hash) or 33 bytes (block hash + b'n')
        let hash_bytes = if message_len == 33 && request.message[32] == b'n' {
            // Pop off the 'n' byte from the block hash
            &request.message[..32]
        } else if message_len == 32 {
```
After
```rust
/// Returns whether the request is valid or not.
    fn validate_signature_share_request(&self, request: &mut SignatureShareRequest) -> bool {
        let Some(block_vote): Option<NakamotoBlockVote> = read_next(&mut &request.message[..]).ok()
        else {
            // We currently reject anything that is not a block vote
            debug!(
                "Signer #{}: Received a signature share request for an unknown message stream. Reject it.",
                self.signer_id
```

## Snippet 3

Context: `stacks-signer/src/signer.rs:1127` (changes signature or replay validation logic)

Before
```rust
fn process_signature(&mut self, signature: &Signature) {
        // Deserialize the signature result and broadcast an appropriate Reject or Approval message to stackerdb
        let Some(aggregate_public_key) = &self.coordinator.get_aggregate_public_key() else {
            debug!(
                "Signer #{}: No aggregate public key set. Cannot validate signature...",
                self.signer_id
            );
            return;
```
After
```rust
fn process_signature(&mut self, signature: &Signature) {
        // Deserialize the signature result and broadcast an appropriate Reject or Approval message to stackerdb
        let message = self.coordinator.get_message();
        let Some(block_vote): Option<NakamotoBlockVote> = read_next(&mut &message[..]).ok() else {
            debug!(
                "Signer #{}: Received a signature result for a non-block. Nothing to broadcast.",
                self.signer_id
            );
```

## Snippet 4

Context: `stackslib/src/chainstate/nakamoto/mod.rs:343` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct NakamotoBlock {
```
After
```rust
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
/// A vote across the signer set for a block
pub struct NakamotoBlockVote {
    pub signer_signature_hash: Sha512Trunc256Sum,
    pub rejected: bool,
}
```

# Fix Pattern

Replace ad hoc byte interpretation with a typed serialized vote object and require affected signer paths to parse that object before acting on vote state.

## How It Was Fixed

The patch adds `NakamotoBlockVote` in `stackslib/src/chainstate/nakamoto/mod.rs` and updates signer request validation, signature result processing, and signing-error processing in `stacks-signer/src/signer.rs` to deserialize that type. The observed changes remove length-based vote validation, trailing `b'n'` rejection-marker handling, and first-32-byte hash slicing from those signer vote paths.

# Why It Matters

1. Reduces ambiguity in signer vote message handling.

2. Binds the target signer signature hash and rejection flag in one structured message.

3. Rejects or ignores unknown message streams in the shown signer paths.

4. Touches consensus-adjacent signer coordination code.

5. Does not, by itself, prove a security vulnerability.

# Evidence Notes

Evidence is limited to the supplied hunks from commit `e24f223a98` dated 2024-02-23. The strongest support is in `stacks-signer/src/signer.rs:529`, `stacks-signer/src/signer.rs:1127`, `stacks-signer/src/signer.rs:1163`, and `stackslib/src/chainstate/nakamoto/mod.rs:343`. The evidence supports a structured-message refactor or hardening of signer vote handling. It does not show attacker control, exploitability, signature bypass, aggregate-key validation consequences, or consensus divergence. Protocol security invariant: Signer vote messages should be parsed according to a well-defined format before signer request, result, or error handling acts on the target block hash or rejection state. Verification notes: No exploitability is proven from the patch alone. No evidence shows forged signatures or threshold signature bypass. No evidence shows a remote attacker can force consensus divergence. No evidence shows the old raw hash format was accepted outside this signer coordination path. The aggregate public key validation impact cannot be fully assessed from the provided hunks. No exploit path is demonstrated in the provided evidence. No remote attacker capability is established. No threshold-signature bypass is shown. No consensus failure scenario is shown. Treat as security-relevant unclear rather than a confirmed or likely vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signer-vote-message-validation`
Final impact type: `signer-vote-integrity, consensus-adjacent-integrity`
Final confidence: `medium`
Final tags: `validator-ops, cryptography, consensus, signature, message-validation, hardening`

The supplied patch evidence supports retaining this as security hardening, not as a proven vulnerability fix. The change replaces ad hoc byte-length and marker-based signer vote interpretation with a typed serialized NakamotoBlockVote and rejects or ignores unknown message streams in signer vote request, result, and error paths. That clearly tightens behavior in a cryptographic, consensus-adjacent signer path, but the evidence does not prove exploitability, attacker control, signature forgery, or consensus divergence.

## Security Evidence

1. validate_signature_share_request now deserializes NakamotoBlockVote and rejects unknown message streams instead of accepting raw 32-byte or 33-byte conventions.
2. process_signature now requires a parsed NakamotoBlockVote before acting on the signature result and block tracking state.
3. process_sign_error no longer slices arbitrary first-32-byte hashes from non-block messages and instead parses a block vote after the full-block special case.
4. NakamotoBlockVote explicitly binds signer_signature_hash with the rejected flag in a structured serialized type.
5. The touched code is signer coordination logic involving signatures and consensus-adjacent block votes.

## Missing Evidence

1. No demonstrated exploit path or attacker-controlled message source is shown.
2. No evidence shows signature forgery, threshold-signature bypass, or unauthorized approval/rejection.
3. No concrete consensus divergence or state corruption scenario is proven.
4. No security advisory, CVE, or commit message explicitly describing a vulnerability is provided.
5. No test evidence in the supplied input proves a security regression case.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim confirmed exploitability or a concrete vulnerability.
3. Do not claim database-related impact from the supplied evidence.
4. Limit impact to signer vote/message integrity in a consensus-adjacent path.
5. Original state-corruption framing is too strong for the provided patch evidence.
