---
case_id: case_20220913_0bf5cd634
project: zksync
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2022-09-13
source_refs:
  - git:0bf5cd6343852a21209c0c3a326b0c354eb95394
  - "core/lib/types/src/tx/change_pubkey.rs:409"
  - "core/lib/types/src/tx/change_pubkey.rs:335"
  - "sdk/zksync-rs/src/signer.rs:77"
  - "sdk/zksync-rs/src/signer.rs:169"
bug_class: cross-domain-signature-replay
impact_type:
  - replay
confidence: medium
tags:
  - transaction-processing
  - change-pubkey
  - signature
  - eip712
  - chain-id
  - replay-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a likely security fix for ChangePubKey Ethereum authorization domain separation. The supplied hunks show the old raw-message ECDSA signing path being deprecated for normal SDK use and a new EIP-712 path that requires chain_id, signs typed data, and verifies recovered signers from a domain-separated hash. The evidence supports cross-domain replay hardening, but not broader claims about reentrancy, front-running, denial of service, or direct fund theft.

## Observed Patch Facts

1. In `core/lib/types/src/tx/change_pubkey.rs`, the patch replaces `} else if let Some(old_eth_signature) = &self.eth_signature {` with `ChangePubKeyEthAuthData::EIP712(ChangePubKeyEIP712Data {`.

2. In `core/lib/types/src/tx/change_pubkey.rs`, the patch replaces `if let Some(ChangePubKeyEthAuthData::ECDSA(ChangePubKeyECDSAData { batch_hash, .. })) =` with `match &self.eth_auth_data {`.

3. In `sdk/zksync-rs/src/signer.rs`, the patch replaces `pub async fn sign_change_pubkey_tx(` with `#[deprecated]`.

4. In `sdk/zksync-rs/src/signer.rs`, the patch replaces `let sign_bytes = change_pubkey` with `let chain_id = chain_id.ok_or_else(|| {`.

## Project Context

The changed code sits primarily in `core/lib/types/src/tx`, `core/lib/types/src`, `sdk/zksync-rs/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sdk/zksync-rs/src/provider.rs`, `sdk/zksync-rs/src/credentials.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/zksync-rs/src/provider.rs`, `sdk/zksync-rs/src/credentials.rs`. The strongest project-level identifiers around this patch are `ChangePubKeyEthAuthData::EIP712`, `Eip712Domain::new`, `chain_id`, and `Some`. Nearby tests or test-like files include `sdk/zksync-rs/tests/unit.rs`, `core/lib/types/src/tests/hardcoded.rs`.

## Before/After Behavior

Before the patch, the shown SDK ChangePubKey path signed bytes from get_eth_signed_data() with sign_message(), and validation recovered a signer from legacy signed data. The provided before hunks do not show chain_id-bound EIP-712 domain separation for that authorization. After the patch, ChangePubKey signing requires chain_id for offchain EIP-712 auth, constructs Eip712Domain::new(chain_id), signs typed data, and validation handles ChangePubKeyEthAuthData::EIP712 by recovering the signer from the typed-data hash and comparing it to self.account. The old ECDSA signing method is retained only as a deprecated hidden compatibility API.

# Root Cause

The legacy ChangePubKey Ethereum authorization path used raw ECDSA signed bytes rather than the EIP-712 domain-separated structure shown in the patched code. Based on the provided evidence, the missing explicit chain_id domain binding is the plausible root cause of a cross-domain replay risk. The full exploit preconditions and on-chain acceptance path are not shown.

## Walkthrough

1. A ChangePubKey transaction requires Ethereum authorization to bind an account to a new zkSync public key.

2. In the old SDK path shown, the transaction authorization was produced by signing get_eth_signed_data() with sign_message().

3. The old validation evidence shows signer recovery from legacy signed data, without the EIP-712 domain construction now present in the patch.

4. The patch introduces ChangePubKeyEthAuthData::EIP712 handling in validation.

5. For EIP-712 auth, validation requires self.chain_id, builds Eip712Domain::new(chain_id), hashes typed data for the ChangePubKey transaction, recovers the signer, and accepts only the account address.

6. The SDK signing path now requires chain_id before offchain EIP-712 signing and signs typed data with the same domain concept.

7. The previous ECDSA signing API is renamed, deprecated, and hidden, which steers normal callers away from the legacy format.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/lib/types/src/tx/change_pubkey.rs | 395 | validates ChangePubKey Ethereum auth data and recovers the signer from EIP-712 typed data bound to chain_id |
| core/lib/types/src/tx/change_pubkey.rs | 322 | builds legacy Ethereum signed data and updates batch_hash handling around the ChangePubKey auth variant |
| sdk/zksync-rs/src/signer.rs | 138 | creates ChangePubKey transactions and signs offchain auth with EIP-712 typed data, requiring chain_id |
| sdk/zksync-rs/src/signer.rs | 75 | deprecates the old ECDSA ChangePubKey signing API in favor of the EIP-712 path |

## Code Snippets

## Snippet 1

Context: `core/lib/types/src/tx/change_pubkey.rs:409` (changes a sensitive control or state-update path)

Before
```rust
create2_address == self.account
                }
            }
        } else if let Some(old_eth_signature) = &self.eth_signature {
            let recovered_address = self
                .get_old_eth_signed_data()
                .ok()
                .and_then(|msg| old_eth_signature.signature_recover_signer(&msg).ok());
```
After
```rust
create2_address == self.account
                }
                ChangePubKeyEthAuthData::EIP712(ChangePubKeyEIP712Data {
                    eth_signature, ..
                }) => {
                    if let Some(chain_id) = self.chain_id {
                        let domain = Eip712Domain::new(chain_id);
                        let data = PackedEthSignature::typed_data_to_signed_bytes(&domain, self);
```

## Snippet 2

Context: `core/lib/types/src/tx/change_pubkey.rs:335` (changes signature or replay validation logic)

Before
```rust
eth_signed_msg.extend_from_slice(&self.account_id.to_be_bytes());
        // In case this transaction is not part of a batch, we simply append zeros.
        if let Some(ChangePubKeyEthAuthData::ECDSA(ChangePubKeyECDSAData { batch_hash, .. })) =
            self.eth_auth_data
        {
            eth_signed_msg.extend_from_slice(batch_hash.as_bytes());
        } else {
            eth_signed_msg.extend_from_slice(H256::default().as_bytes());
```
After
```rust
eth_signed_msg.extend_from_slice(&self.account_id.to_be_bytes());
        // In case this transaction is not part of a batch, we simply append zeros.
        match &self.eth_auth_data {
            Some(ChangePubKeyEthAuthData::EIP712(ChangePubKeyEIP712Data {
                batch_hash, ..
            })) => {
                eth_signed_msg.extend_from_slice(batch_hash.as_bytes());
            }
```

## Snippet 3

Context: `sdk/zksync-rs/src/signer.rs:77` (changes an authorization or privilege gate)

Before
```rust
}

    pub async fn sign_change_pubkey_tx(
        &self,
```
After
```rust
}

    #[deprecated]
    #[doc(hidden)]
    /// This method required only for backward compatibility with tests.
    /// You should use `sign_change_pubkey_tx` method with EIP712 ChangePubKey for offchain signature
    pub async fn __old_sign_change_pubkey_tx_ecdsa(
        &self,
```

## Snippet 4

Context: `sdk/zksync-rs/src/signer.rs:169` (changes signature or replay validation logic)

Before
```rust
.ok_or(SignerError::MissingEthSigner)?;

            let sign_bytes = change_pubkey
                .get_eth_signed_data()
                .map_err(signing_failed_error)?;
            let eth_signature = eth_signer
                .sign_message(&sign_bytes)
                .await
```
After
```rust
.ok_or(SignerError::MissingEthSigner)?;

            let chain_id = chain_id.ok_or_else(|| {
                SignerError::CustomError("Can't sign eip712 without chain id".to_string())
            })?;
            let domain = Eip712Domain::new(chain_id);
            let eth_signature = eth_signer
                .sign_typed_data(&domain, &change_pubkey)
```

# Fix Pattern

Move replay-sensitive authorization from raw-message ECDSA signing to EIP-712 typed-data signing and verification with an explicit chain_id domain requirement.

## How It Was Fixed

The patch added EIP-712 ChangePubKey auth validation, required chain_id in the SDK signing path, constructed Eip712Domain::new(chain_id), used sign_typed_data for new offchain authorization, recovered signers from the typed-data hash during validation, and deprecated the old ECDSA ChangePubKey signing method.

# Why It Matters

1. ChangePubKey authorization affects which key can control a zkSync account.

2. Signatures for account-control changes need clear domain separation.

3. Binding authorization to chain_id reduces replay risk across networks or domains.

4. The provided evidence supports this replay-hardening claim, not the unrelated hardening themes in the broad commit message.

# Evidence Notes

Primary support comes from core/lib/types/src/tx/change_pubkey.rs, where EIP-712 auth validation is added using Eip712Domain::new(chain_id), typed_data_to_signed_bytes(), and signer recovery from the typed-data hash. SDK support comes from sdk/zksync-rs/src/signer.rs, where sign_change_pubkey_tx now requires chain_id for EIP-712 signing and uses sign_typed_data. The commit message explicitly mentions cross-domain attack protection, but the supplied code excerpts do not show the full protocol acceptance path or a concrete exploit reproduction. Protocol security invariant: A ChangePubKey Ethereum authorization should be bound to the intended zkSync transaction and network domain, including chain_id, so a signature from another domain or signing scheme is not accepted as authorization for the account public-key change. Verification notes: The patch evidence does not prove private key compromise or direct fund theft. The provided hunks do not establish a node crash or malformed-input liveness bug. The evidence does not show the full on-chain enforcement path for ChangePubKey authorization. The broad commit mentions reentrancy, front-running, and proveBlocks hardening, but the supplied traced hunks substantiate only the ChangePubKey domain-separation issue. The exact exploit preconditions for cross-domain replay are not fully shown by the patch context. Downgraded confidence from high to medium because the full on-chain or server-side acceptance path is not provided. Rejected the heuristic liveness-failure and panic claims; the supplied hunks do not support node crash behavior. Rejected reentrancy, front-running, and proveBlocks claims for this finding because the selected evidence is limited to ChangePubKey authorization. Kept in the security corpus because the code and commit text align on replay-sensitive domain separation for account authorization. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cross-domain-signature-replay`
Final impact type: `replay`
Final confidence: `medium`
Final tags: `transaction-processing, change-pubkey, signature, eip712, chain-id, replay-hardening`

The supplied evidence supports retaining this as security-relevant, but more conservatively as replay hardening rather than a proven concrete security fix. The patch moves ChangePubKey Ethereum authorization toward EIP-712 typed-data signing and verification with an explicit chain_id domain, and the commit message names cross-domain attack protection. However, the excerpts do not prove an exploitable replay path, on-chain acceptance path, or actual account compromise, and the original liveness-failure classification is not supported.

## Security Evidence

1. ChangePubKey EIP-712 validation constructs Eip712Domain::new(chain_id) before recovering the signer from typed data.
2. SDK signing now requires chain_id before EIP-712 ChangePubKey signing and uses sign_typed_data instead of raw sign_message bytes.
3. The old ECDSA ChangePubKey signing method is deprecated and hidden for compatibility use.
4. The commit metadata explicitly references cross-domain attack protection.

## Missing Evidence

1. No full exploit scenario or proof that legacy signatures were accepted across domains is shown.
2. No on-chain or server-side acceptance path proving concrete unauthorized key change is included.
3. No regression test demonstrating rejected cross-domain replay is supplied in the evidence.
4. The broad commit also mentions reentrancy, front-running, and griefing, but the provided hunks only substantiate ChangePubKey signature-domain changes.

## Claim Boundaries

1. Do not classify this as a liveness failure; the supplied hunks do not show crash, halt, or availability impact.
2. Do not claim direct fund theft or account takeover from the provided evidence alone.
3. Do not attribute this finding to reentrancy, front-running, proveBlocks, or griefing protections.
4. Supported claim is limited to ChangePubKey authorization replay/domain-separation hardening.
