---
case_id: case_20220729_24d683b660
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2022-07-29
source_refs:
  - git:24d683b66033127d5a53786ff9d84637ba64f931
  - "narwhal/crypto/src/secp256k1.rs:91"
  - "narwhal/crypto/src/secp256k1.rs:380"
bug_class: signature-malleability
impact_type:
  - signature-malleability
confidence: medium
tags:
  - cryptography
  - secp256k1
  - signature
  - signature-malleability
  - non-malleability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes secp256k1 recoverable signature malleability in `narwhal/crypto/src/secp256k1.rs`. The old verifier converted the recoverable signature to a standard ECDSA signature with `to_standard()` and verified that value against the public key. The new verifier recovers the public key from the provided recoverable signature and succeeds only when the recovered key bytes match the expected public key.

## Observed Patch Facts

1. In `narwhal/crypto/src/secp256k1.rs`, the patch replaces `let vrfy = Secp256k1::verification_only();` with `// If pubkey recovered from signature matches original pubkey, verifies signature.`.

2. In `narwhal/crypto/src/secp256k1.rs`, the patch adds `// Creates a 65-bytes sigature of shape [r, s, v] where v can be 0 or 1.`.

## Project Context

The changed code sits primarily in `narwhal/crypto/src`, `narwhal/crypto`, which anchors the finding in the `cryptography` area of the project. Historical context from `narwhal/crypto/src/traits.rs`, `narwhal/crypto/src/ed25519.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `narwhal/crypto/src/traits.rs`, `narwhal/crypto/src/ed25519.rs`. The strongest project-level identifiers around this patch are `signature`, `Message::from_hashed_data`, `rust_secp256k1::hashes::sha256::Hash`, and `signature::Error::new`. Nearby tests or test-like files include `narwhal/crypto/src/tests/secp256k1_tests.rs`, `narwhal/crypto/src/tests/ed25519_tests.rs`.

## Before/After Behavior

Before the patch, the verifier hashed the message, converted `signature.sig` to a standard ECDSA signature, and called `verify_ecdsa`. The patch comment states this path would verify both `[r, s, v]` and `[r, s, -v]`, so the recovery id was not uniquely enforced. After the patch, the verifier calls `signature.sig.recover(&message)` and returns success only if the recovered public key serializes to the same bytes as the expected `Secp256k1PublicKey`; recovery failure or key mismatch returns `signature::Error::new()`. The signer change shown is comment-only and does not alter signing behavior.

# Root Cause

The verifier checked the recoverable secp256k1 signature as a standard ECDSA signature by using `signature.sig.to_standard()`. That dropped the recoverable-signature distinction relevant to the recovery id, allowing recovery-id variants to pass standard ECDSA verification according to the patch comment.

## Walkthrough

1. The affected code is `impl Verifier<Secp256k1Signature> for Secp256k1PublicKey` in `narwhal/crypto/src/secp256k1.rs`.

2. The pre-patch verifier built the hashed `Message` and used `Secp256k1::verification_only()` with `verify_ecdsa`.

3. The verifier passed `signature.sig.to_standard()` to `verify_ecdsa`, checking only the standard ECDSA form.

4. The patch comment states this accepted both `[r, s, v]` and `[r, s, -v]`.

5. The new verifier calls `signature.sig.recover(&message)`.

6. Verification now succeeds only when the recovered public key bytes match `self.as_bytes()`.

7. The signer path only gained explanatory comments about the recoverable signature format and RFC6979 nonce generation.

8. No evidence was provided for transaction replay, consensus impact, private key compromise, nonce leakage, or impact to other signature schemes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| narwhal/crypto/src/secp256k1.rs | 83 | Secp256k1Signature verifier now recovers the public key from the full recoverable signature and rejects mismatched recovery ids |
| narwhal/crypto/src/secp256k1.rs | 372 | Secp256k1Signature signer path documents the 65-byte [r, s, v] signature shape; behavior appears unchanged |

## Code Snippets

## Snippet 1

Context: `narwhal/crypto/src/secp256k1.rs:91` (changes signature or replay validation logic)

Before
```rust
let message = Message::from_hashed_data::<rust_secp256k1::hashes::sha256::Hash>(msg);

        let vrfy = Secp256k1::verification_only();
        vrfy.verify_ecdsa(&message, &signature.sig.to_standard(), &self.pubkey)
            .map_err(|_e| signature::Error::new())
    }
}
```
After
```rust
let message = Message::from_hashed_data::<rust_secp256k1::hashes::sha256::Hash>(msg);

        // If pubkey recovered from signature matches original pubkey, verifies signature.
        // To ensure non-malleability, signature.verify_ecdsa() is not used since it will verify [r, s, v] and [r, s, -v].
        match signature.sig.recover(&message) {
            Ok(recovered_key) if self.as_bytes() == recovered_key.serialize().as_slice() => Ok(()),
            _ => Err(signature::Error::new()),
        }
```

## Snippet 2

Context: `narwhal/crypto/src/secp256k1.rs:380` (changes a sensitive control or state-update path)

Before
```rust
let message = Message::from_hashed_data::<rust_secp256k1::hashes::sha256::Hash>(msg);

        Ok(Secp256k1Signature {
            sig: secp.sign_ecdsa_recoverable(&message, &self.secret.privkey),
```
After
```rust
let message = Message::from_hashed_data::<rust_secp256k1::hashes::sha256::Hash>(msg);

        // Creates a 65-bytes sigature of shape [r, s, v] where v can be 0 or 1.
        // Pseudo-random deterministic nonce generation is used according to RFC6979.
        Ok(Secp256k1Signature {
            sig: secp.sign_ecdsa_recoverable(&message, &self.secret.privkey),
```

# Fix Pattern

Verify recoverable signatures by recovering the public key from the exact recoverable signature and message, then comparing that recovered key to the expected public key. Do not reduce the signature to a standard ECDSA form when recovery metadata is part of the accepted signature representation.

## How It Was Fixed

The patch removed `Secp256k1::verification_only()` and `verify_ecdsa(&message, &signature.sig.to_standard(), &self.pubkey)` from the secp256k1 verifier. It replaced them with `signature.sig.recover(&message)` and an exact byte comparison between the recovered public key and the expected public key. Failures and mismatches return `signature::Error::new()`.

# Why It Matters

1. The previous verifier did not enforce the recovery id in the recoverable signature representation.

2. The new verifier enforces non-malleability for this secp256k1 recoverable signature path.

3. The evidence supports a signature-malleability fix, not broader replay or consensus claims.

4. The provided evidence does not show other signature schemes were affected.

# Evidence Notes

The strongest evidence is the verifier diff in `narwhal/crypto/src/secp256k1.rs`, where standard ECDSA verification over `signature.sig.to_standard()` was replaced with recover-and-compare logic. The in-code comment explicitly gives the non-malleability reason and states `verify_ecdsa()` would verify both recovery-id variants. The signer snippet only adds comments and should be treated as support/context, not as a behavioral fix. Related files show crypto subsystem context but do not expand the affected scope beyond secp256k1 recoverable signature verification. Protocol security invariant: Recoverable secp256k1 signature verification must bind the full recoverable signature, including the recovery id, to the expected public key. Verification should not accept an alternate recovery-id form merely because the standard ECDSA portion verifies. Verification notes: The patch does not show a concrete transaction replay or consensus exploit path. The evidence does not prove private key compromise or nonce leakage. The patch only demonstrates malleability handling for the secp256k1 recoverable signature verifier, not other signature schemes. The signing implementation appears unchanged aside from explanatory comments. Classification is limited to secp256k1 recoverable signature malleability. No concrete exploit path is established beyond acceptance of alternate recovery-id forms. No evidence supports replay, consensus, nonce leakage, or private key compromise claims. No evidence shows functional changes in the signer path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-malleability`
Final impact type: `signature-malleability`
Final confidence: `medium`
Final tags: `cryptography, secp256k1, signature, signature-malleability, non-malleability`

The patch clearly tightens secp256k1 recoverable-signature verification by replacing standard ECDSA verification, which ignores the recovery id, with recover-and-compare logic that binds the full recoverable signature to the expected public key. That supports a security-hardening classification for signature non-malleability. The evidence does not prove a concrete replay, request forgery, consensus, or exploitable protocol impact, so the original security-fix and replay framing is too strong.

## Security Evidence

1. Verifier stopped using signature.sig.to_standard() with verify_ecdsa().
2. New verifier recovers the public key from the provided recoverable signature and message.
3. Verification now succeeds only when the recovered public key bytes match the expected public key.
4. Patch comment explicitly says the change is to ensure non-malleability and avoid accepting both recovery-id variants.

## Missing Evidence

1. No demonstrated transaction replay or request-forgery path.
2. No evidence that accepted alternate recovery ids crossed a trust boundary in an exploitable way.
3. No consensus, authentication bypass, or asset-impact evidence is shown.
4. Signer change is comment-only and does not alter behavior.

## Claim Boundaries

1. Validated scope is limited to secp256k1 recoverable-signature verification.
2. The evidence supports non-malleability hardening, not private key compromise or nonce leakage.
3. Do not generalize the issue to other signature schemes.
4. Do not claim request forgery or replay without additional protocol evidence.
