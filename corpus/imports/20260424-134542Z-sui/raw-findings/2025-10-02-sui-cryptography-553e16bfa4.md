---
case_id: case_20251002_553e16bfa4
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
bug_class: input-validation
confidence: medium
source_quality: medium
date: 2025-10-02
source_refs:
  - git:553e16bfa447f9f21337d0926a8ca4dc37558283
  - "crates/sui-bridge/src/server/mod.rs:162"
  - "crates/sui-bridge/src/abi.rs:204"
  - "crates/sui-bridge/src/crypto.rs:119"
  - "crates/sui-bridge/src/types.rs:384"
impact_type:
  - availability
tags:
  - bridge
  - api
  - input-validation
  - dos-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best treated as bridge node API input-validation and availability hardening. The strongest evidence is the new `validate_list_size` helper in `server/mod.rs`, whose comment explicitly says it prevents DoS during u8 conversion in encoding. The `From` to `TryFrom` conversion change for `SuiToEthBridgeAction` to `eth_sui_bridge::Message` supports that invalid bridge action/message encoding is now handled as an error. The crypto and digest updates appear to be follow-on adaptations to the new fallible encoding contract, not evidence of a standalone cryptographic flaw.

## Observed Patch Facts

1. In `crates/sui-bridge/src/server/mod.rs`, the patch replaces `async fn ping(` with `/// Validates that a comma-separated list doesn't exceed the maximum allowed size`.

2. In `crates/sui-bridge/src/abi.rs`, the patch replaces `impl From<SuiToEthBridgeAction> for eth_sui_bridge::Message {` with `impl TryFrom<SuiToEthBridgeAction> for eth_sui_bridge::Message {`.

3. In `crates/sui-bridge/src/crypto.rs`, the patch replaces `let msg_bytes = msg.to_bytes();` with `let msg_bytes = msg`.

4. In `crates/sui-bridge/src/types.rs`, the patch replaces `hasher.update(self.to_bytes());` with `hasher.update(`.

## Project Context

The changed code sits primarily in `crates/sui-bridge/src/server`, `crates/sui-bridge/src`, `crates/sui-bridge`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-bridge/src/eth_transaction_builder.rs`, `crates/sui-bridge/src/sui_transaction_builder.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-bridge/src/eth_transaction_builder.rs`, `crates/sui-bridge/src/sui_transaction_builder.rs`. The strongest project-level identifiers around this patch are `eth_sui_bridge::Message`, `Message`, `SuiToEthBridgeAction`, and `eth_sui_bridge`. Nearby tests or test-like files include `crates/sui-bridge/src/e2e_tests/basic.rs`, `crates/sui-bridge/src/e2e_tests/complex.rs`.

## Before/After Behavior

Before the patch, the provided evidence does not show a local size guard for comma-separated bridge API list input before later encoding/conversion work, and conversion from `SuiToEthBridgeAction` to `eth_sui_bridge::Message` was modeled as infallible. After the patch, oversized comma-separated lists are rejected with `BridgeError::InvalidBridgeClientRequest`, message conversion is fallible via `TryFrom`, and digest/signing callers explicitly expect byte encoding to succeed only for valid actions.

# Root Cause

The bridge request/action encoding boundary treated some inputs as insufficiently bounded or infallibly encodable. The evidence supports an input-validation/resource-exhaustion concern around oversized comma-separated lists and invalid encodings, but does not establish fund loss, signature forgery, authorization bypass, or a cryptographic primitive weakness.

## Walkthrough

1. A bridge node API path gained `validate_list_size` for comma-separated list strings.

2. The helper counts comma-separated entries and rejects counts above `MAX_LIST_SIZE`.

3. The added comment states the purpose is to prevent DoS during u8 conversion in encoding.

4. The `SuiToEthBridgeAction` to `eth_sui_bridge::Message` conversion changed from infallible `From` to fallible `TryFrom` returning `BridgeResult`.

5. Digest and signing code now call fallible `to_bytes()` and assert success for valid actions, indicating these are downstream internal paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-bridge/src/server/mod.rs | 162 | Rejects oversized comma-separated bridge API request lists before encoding/conversion work. |
| crates/sui-bridge/src/abi.rs | 204 | Changes SuiToEthBridgeAction to eth_sui_bridge::Message conversion from infallible to fallible, allowing invalid action payload encoding to return BridgeError. |
| crates/sui-bridge/src/crypto.rs | 119 | Updates bridge authority signing to handle the now-fallible BridgeAction byte encoding, with valid-action expectation at signing time. |
| crates/sui-bridge/src/types.rs | 384 | Updates BridgeAction digest computation to use the fallible byte encoding contract for valid actions. |

## Code Snippets

## Snippet 1

Context: `crates/sui-bridge/src/server/mod.rs:162` (changes a sensitive control or state-update path)

Before
```rust
}

async fn ping(
    State((_handler, _metrics, metadata)): State<(
```
After
```rust
}

/// Validates that a comma-separated list doesn't exceed the maximum allowed size
/// to prevent DoS attacks during u8 conversion in encoding
fn validate_list_size(list_str: &str, field_name: &str) -> Result<(), BridgeError> {
    let count = list_str.split(',').count();
    if count > MAX_LIST_SIZE {
        return Err(BridgeError::InvalidBridgeClientRequest(format!(
```

## Snippet 2

Context: `crates/sui-bridge/src/abi.rs:204` (changes persisted or aggregate state handling)

Before
```rust
////////////////////////////////////////////////////////////////////////

impl From<SuiToEthBridgeAction> for eth_sui_bridge::Message {
    fn from(action: SuiToEthBridgeAction) -> Self {
        eth_sui_bridge::Message {
            message_type: BridgeActionType::TokenTransfer as u8,
            version: TOKEN_TRANSFER_MESSAGE_VERSION,
            nonce: action.sui_bridge_event.nonce,
```
After
```rust
////////////////////////////////////////////////////////////////////////

impl TryFrom<SuiToEthBridgeAction> for eth_sui_bridge::Message {
    type Error = BridgeError;

    fn try_from(action: SuiToEthBridgeAction) -> BridgeResult<Self> {
        Ok(eth_sui_bridge::Message {
            message_type: BridgeActionType::TokenTransfer as u8,
```

## Snippet 3

Context: `crates/sui-bridge/src/crypto.rs:119` (changes the branch that decides whether execution stops or continues)

Before
```rust
impl BridgeAuthoritySignInfo {
    pub fn new(msg: &BridgeAction, secret: &BridgeAuthorityKeyPair) -> Self {
        let msg_bytes = msg.to_bytes();
        Self {
            authority_pub_key: secret.public().clone(),
```
After
```rust
impl BridgeAuthoritySignInfo {
    pub fn new(msg: &BridgeAction, secret: &BridgeAuthorityKeyPair) -> Self {
        let msg_bytes = msg
            .to_bytes()
            .expect("Message encoding should not fail for valid actions");
        Self {
            authority_pub_key: secret.public().clone(),
```

## Snippet 4

Context: `crates/sui-bridge/src/types.rs:384` (changes the branch that decides whether execution stops or continues)

Before
```rust
pub fn digest(&self) -> BridgeActionDigest {
        let mut hasher = Keccak256::default();
        hasher.update(self.to_bytes());
        BridgeActionDigest::new(hasher.finalize().into())
    }
```
After
```rust
pub fn digest(&self) -> BridgeActionDigest {
        let mut hasher = Keccak256::default();
        hasher.update(
            self.to_bytes()
                .expect("Message encoding should not fail for valid actions"),
        );
        BridgeActionDigest::new(hasher.finalize().into())
    }
```

# Fix Pattern

Add explicit bounds checks at the bridge API input boundary and propagate encoding failures through fallible conversion APIs.

## How It Was Fixed

The server code added a list-size validator that returns `InvalidBridgeClientRequest` when a comma-separated list exceeds `MAX_LIST_SIZE`. ABI conversion was changed to return `BridgeResult` via `TryFrom`. Internal digest and signing callers were adjusted to the fallible byte-encoding API with an expectation that validated actions encode successfully.

# Why It Matters

1. Reduces risk of oversized bridge API inputs causing excessive or invalid encoding work.

2. Allows invalid bridge action/message encodings to fail cleanly.

3. Keeps signing and digesting paths behind a valid-encoding assumption.

4. Does not prove remote exploitability or asset compromise from the supplied evidence.

# Evidence Notes

Grounded evidence comes from `server/mod.rs` line 162, where the added comment explicitly references preventing DoS attacks during u8 conversion in encoding; `abi.rs` line 204, where conversion changes from `From` to `TryFrom`; and the follow-on `to_bytes().expect(...)` changes in `crypto.rs` and `types.rs`. The exact endpoint, attacker model, and concrete pre-patch failure mode are not shown. Protocol security invariant: Bridge node API request-derived list inputs should be bounded before encoding/conversion work, and bridge action/message conversion should be able to reject invalid encodings instead of treating them as infallible. Verification notes: Remote exploitability is not proven by the provided patch evidence. No signature forgery, committee compromise, or authorization bypass is shown. No direct fund-loss or bridge message replay impact is demonstrated. The exact invalid request endpoint and pre-patch failure mode are not fully shown. Crypto changes appear secondary to validation/encoding behavior, not a cryptographic primitive flaw. Classified as likely security hardening, not a confirmed vulnerability fix. Subsystem downgraded away from cryptography because crypto changes appear secondary. No claim of signature forgery, committee compromise, authorization bypass, replay, or fund loss is supported. Keep in security corpus due to explicit DoS-prevention comment and runtime input guard. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `availability`
Final tags: `bridge, api, input-validation, dos-hardening`

The supplied patch evidence supports retaining this as security hardening, not a confirmed vulnerability fix. The strongest evidence is the added bridge API list-size validator with an explicit comment that it prevents DoS during u8 conversion in encoding, plus fallible message conversion for invalid bridge actions. The evidence does not prove exploitability, asset compromise, or a cryptographic flaw, so the corpus entry should be scoped to availability/input-validation hardening.

## Security Evidence

1. Added validate_list_size rejects comma-separated bridge API lists larger than MAX_LIST_SIZE.
2. Code comment explicitly states the guard is intended to prevent DoS attacks during u8 conversion in encoding.
3. SuiToEthBridgeAction conversion changed from infallible From to fallible TryFrom returning BridgeResult.
4. Invalid oversized input now returns InvalidBridgeClientRequest instead of proceeding into encoding/conversion.

## Missing Evidence

1. No exact endpoint or externally reachable request path is shown.
2. No concrete pre-patch crash, panic, resource exhaustion trace, or exploit demonstration is provided.
3. No evidence of signature forgery, authorization bypass, replay, fund loss, or committee compromise.
4. Crypto and digest changes appear to adapt to fallible encoding rather than fix a cryptographic weakness.

## Claim Boundaries

1. Classify as bridge API input-validation and DoS hardening only.
2. Do not claim a confirmed exploitable vulnerability from the supplied evidence.
3. Do not classify the primary issue as cryptography despite touched crypto-related files.
4. Do not claim financial loss or bridge message integrity compromise.
