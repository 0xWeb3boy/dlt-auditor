---
case_id: case_20200227_0ad13b212
project: zksync
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2020-02-27
source_refs:
  - git:0ad13b21280daf33fb008fdab0b323fcb86b607b
  - "core/models/src/node/tx.rs:224"
  - "core/testkit/src/zksync_account.rs:127"
  - "js/zksync.js/build/wallet.js:175"
  - "js/zksync.js/src/wallet.ts:138"
bug_class: authorization-message-domain-separation-hardening
impact_type:
  - authorization-clarity
  - signature-domain-separation
tags:
  - transaction-processing
  - change-pubkey
  - ethereum-signature
  - authorization-message
  - domain-separation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes the ChangePubKey Ethereum authorization payload from opaque raw bytes to a human-readable zkSync registration message. The evidence supports security hardening around authorization clarity and domain separation, but not a confirmed replay, forgery, or missing-validation vulnerability.

## Observed Patch Facts

1. In `core/models/src/node/tx.rs`, the patch replaces `pub fn get_eth_signed_data(nonce: Nonce, new_pubkey_hash: &PubKeyHash) -> Vec<u8> {` with `pub fn get_eth_signed_data(`.

2. In `core/testkit/src/zksync_account.rs`, the patch replaces `let sign_bytes = ChangePubKey::get_eth_signed_data(nonce, &self.pubkey_hash);` with `let sign_bytes = ChangePubKey::get_eth_signed_data(nonce, &self.pubkey_hash)`.

3. In `js/zksync.js/build/wallet.js`, the patch replaces `newPkHash = signer_1.serializeAddress(newPubKeyHash);` with `msgNonce = signer_1.serializeNonce(numNonce).toString("hex").toLowerCase();`.

4. In `js/zksync.js/src/wallet.ts`, the patch replaces `const newPkHash = serializeAddress(newPubKeyHash);` with `const msgNonce = serializeNonce(numNonce).toString("hex").toLowerCase();`.

## Project Context

The changed code sits primarily in `core/models/src/node`, `core/models/src`, `core/testkit/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/models/src/node/operations.rs`, `js/zksync.js/src/transport.ts` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/models/src/node/operations.rs`, `core/models/src/lib.rs`. The strongest project-level identifiers around this patch are `nonce`, `const`, `message`, and `Vec::with_capacity`. Nearby tests or test-like files include `js/zksync.js/tests/util.test.ts`.

## Before/After Behavior

Before the patch, ChangePubKey Ethereum signed data was constructed as raw binary `nonce || pubkey_hash` bytes in Rust and mirrored by the TypeScript wallet using `Buffer.concat([serializeNonce(numNonce), newPkHash])`. After the patch, the wallet signs a string beginning `Register ZK Sync pubkey`, containing the lowercased new pubkey hash, the nonce rendered as hex, and a trust warning. The Rust helper was changed to construct the longer message and return a `Result`. Testkit signing was updated to consume that fallible helper.

# Root Cause

The pre-patch authorization message was opaque binary data containing the nonce and pubkey hash. The supplied evidence does not show that signature verification, nonce validation, or state-transition checks were missing; the grounded issue is ambiguous or non-human-readable authorization material for a security-sensitive ChangePubKey action.

## Walkthrough

1. ChangePubKey can be authorized with an Ethereum signature over data derived from the nonce and new pubkey hash.

2. Before the patch, the Rust helper built the signed data by appending nonce bytes and `new_pubkey_hash.data`.

3. Before the patch, the TypeScript wallet built the same opaque payload with `Buffer.concat([serializeNonce(numNonce), newPkHash])`.

4. After the patch, the wallet signs a readable zkSync registration message containing the new pubkey hash and nonce.

5. After the patch, the Rust helper constructs a longer domain-specific message and returns `Result<Vec<u8>, failure::Error>`.

6. The testkit helper now expects message construction to succeed before signing.

7. No provided evidence shows a new verifier, nonce check, replay rejection path, or state-transition guard.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/models/src/node/tx.rs | 224 | Constructs the Ethereum-signed ChangePubKey authorization payload, replacing raw binary nonce/pubkey bytes with a domain-specific registration message. |
| js/zksync.js/src/wallet.ts | 138 | Builds the wallet-side message passed to ethSigner.signMessage for ChangePubKey authorization. |
| js/zksync.js/build/wallet.js | 175 | Generated JavaScript output mirroring the wallet ChangePubKey signing message change. |
| core/testkit/src/zksync_account.rs | 127 | Updates test account ChangePubKey signing to consume the new fallible message-construction API. |

## Code Snippets

## Snippet 1

Context: `core/models/src/node/tx.rs:224` (changes signature or replay validation logic)

Before
```rust
}

    pub fn get_eth_signed_data(nonce: Nonce, new_pubkey_hash: &PubKeyHash) -> Vec<u8> {
        let mut eth_signed_msg = Vec::with_capacity(24);
        eth_signed_msg.extend_from_slice(&nonce.to_be_bytes());
        eth_signed_msg.extend_from_slice(&new_pubkey_hash.data);
        eth_signed_msg
    }
```
After
```rust
}

    pub fn get_eth_signed_data(
        nonce: Nonce,
        new_pubkey_hash: &PubKeyHash,
    ) -> Result<Vec<u8>, failure::Error> {
        const CHANGE_PUBKEY_SIGNATURE_LEN: usize = 135;
        let mut eth_signed_msg = Vec::with_capacity(CHANGE_PUBKEY_SIGNATURE_LEN);
```

## Snippet 2

Context: `core/testkit/src/zksync_account.rs:127` (changes signature or replay validation logic)

Before
```rust
None
        } else {
            let sign_bytes = ChangePubKey::get_eth_signed_data(nonce, &self.pubkey_hash);
            let eth_signature = PackedEthSignature::sign(&self.eth_private_key, &sign_bytes)
                .expect("Signature should succeed");
```
After
```rust
None
        } else {
            let sign_bytes = ChangePubKey::get_eth_signed_data(nonce, &self.pubkey_hash)
                .expect("Failed to construct change pubkey signed message.");
            let eth_signature = PackedEthSignature::sign(&self.eth_private_key, &sign_bytes)
                .expect("Signature should succeed");
```

## Snippet 3

Context: `js/zksync.js/build/wallet.js:175` (changes signature or replay validation logic)

Before
```javascript
case 2:
                        numNonce = _b.sent();
                        newPkHash = signer_1.serializeAddress(newPubKeyHash);
                        message = Buffer.concat([signer_1.serializeNonce(numNonce), newPkHash]);
                        if (!onchainAuth) return [3 /*break*/, 3];
                        _a = null;
```
After
```javascript
case 2:
                        numNonce = _b.sent();
                        msgNonce = signer_1.serializeNonce(numNonce).toString("hex").toLowerCase();
                        message = "Register ZK Sync pubkey:\n\n" + newPubKeyHash.toLowerCase() + " nonce: 0x" + msgNonce + "\n\nOnly sign this message for a trusted client!";
                        if (!onchainAuth) return [3 /*break*/, 3];
                        _a = null;
```

## Snippet 4

Context: `js/zksync.js/src/wallet.ts:138` (changes bounds, limits, or capacity handling)

Before
```ts
const numNonce = await this.getNonce(nonce);
        const newPkHash = serializeAddress(newPubKeyHash);
        const message = Buffer.concat([serializeNonce(numNonce), newPkHash]);
        const ethSignature = onchainAuth
            ? null
```
After
```ts
const numNonce = await this.getNonce(nonce);
        const msgNonce = serializeNonce(numNonce).toString("hex").toLowerCase();
        const message = `Register ZK Sync pubkey:\n\n${newPubKeyHash.toLowerCase()} nonce: 0x${msgNonce}\n\nOnly sign this message for a trusted client!`;
        const ethSignature = onchainAuth
            ? null
```

# Fix Pattern

Replace opaque binary authorization payloads with explicit domain-specific signing messages that include the operation purpose and security-relevant fields.

## How It Was Fixed

The ChangePubKey signed payload was changed from raw serialized nonce plus pubkey hash bytes to a readable registration message. Wallet code now signs text containing `Register ZK Sync pubkey`, the new pubkey hash, the nonce, and a warning. Rust model/test support was aligned with the new message construction API.

# Why It Matters

1. Improves user-visible clarity for Ethereum signatures authorizing ChangePubKey.

2. Binds the prompt to zkSync pubkey registration semantics.

3. Includes the specific pubkey hash and nonce in the signed text.

4. Supports domain separation compared with opaque raw bytes.

5. Does not prove a prior replay or forgery vulnerability.

# Evidence Notes

Evidence is limited to message-construction changes in `core/models/src/node/tx.rs`, `js/zksync.js/src/wallet.ts`, generated `js/zksync.js/build/wallet.js`, and testkit adaptation in `core/testkit/src/zksync_account.rs`. Claims about accepted forgeries, replay acceptance, missing nonce checks, or verifier changes are unsupported and should not be made. Protocol security invariant: A ChangePubKey operation authorized by an Ethereum signature should bind the user's consent to a specific zkSync pubkey registration action, including the new pubkey hash and nonce, in an unambiguous domain-specific message. Verification notes: The patch does not prove that forged ChangePubKey transactions were accepted before the change. The patch does not show a missing nonce check or replay acceptance in the state transition path. The evidence does not prove cross-protocol signature replay, only improved message specificity and readability. Generated build output should not be over-weighted beyond confirming the wallet API behavior. Confirmed by provided diff snippets only; no external inspection performed. Generated JavaScript output should be treated as corroborating the TypeScript wallet change, not independent root-cause evidence. The security classification is hardening, not a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-message-domain-separation-hardening`
Final impact type: `authorization-clarity, signature-domain-separation`
Final tags: `transaction-processing, change-pubkey, ethereum-signature, authorization-message, domain-separation, security-hardening`

The supplied patch evidence supports keeping this as security hardening: it changes the ChangePubKey Ethereum authorization payload from opaque nonce/pubkey bytes to an explicit, human-readable, operation-specific message containing the pubkey hash, nonce, and a trust warning. This tightens authorization semantics and user consent clarity, but the evidence does not prove an exploitable replay, forgery, or missing-validation bug, so the original replay/request-forgery framing should be narrowed.

## Security Evidence

1. ChangePubKey signed data changed from raw binary nonce plus pubkey hash to a domain-specific registration message.
2. Wallet-side signing now presents `Register ZK Sync pubkey` with the new pubkey hash and nonce in readable form.
3. Rust and TypeScript signing paths were aligned around the new authorization message format.
4. The added warning explicitly tells users to sign only for a trusted client.

## Missing Evidence

1. No verifier-side change is shown proving previously accepted forged signatures.
2. No nonce-validation or replay-rejection fix is shown.
3. No exploit scenario or cross-protocol replay proof is present in the supplied evidence.
4. No tests are shown demonstrating rejection of a previously accepted malicious ChangePubKey authorization.

## Claim Boundaries

1. Classify as hardening of signature authorization message semantics, not a confirmed vulnerability fix.
2. Do not claim a proven replay or request-forgery vulnerability from this patch alone.
3. Do not infer missing state-transition validation beyond the shown message-construction changes.
4. Generated JavaScript corroborates the TypeScript wallet change but is not independent security evidence.
