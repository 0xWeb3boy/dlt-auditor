---
case_id: case_20231129_2c5a748c5
project: reth
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-11-29
source_refs:
  - git:2c5a748c55906d38076147fc4070748cba8a0204
  - "crates/primitives/src/transaction/signature.rs:151"
  - "crates/primitives/src/transaction/signature.rs:136"
  - "crates/primitives/src/transaction/signature.rs:108"
  - "crates/primitives/src/transaction/signature.rs:313"
bug_class: signature-malleability
impact_type:
  - non-canonical-signature-acceptance
confidence: medium
tags:
  - signature
  - eip-2
  - malleability
  - transaction-validation
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence shows a security-relevant API split in transaction signature recovery: a new checked `recover_signer` explicitly rejects high-s signatures, while `recover_signer_unchecked` is documented as a compatibility path for old signatures. That supports hardening around the EIP-2 low-s invariant, but the provided excerpts do not establish that a previously reachable validation path was actually accepting forbidden signatures, so the vulnerability claim should be downgraded to unclear.

## Observed Patch Facts

1. In `crates/primitives/src/transaction/signature.rs`, the patch replaces `secp256k1::recover_signer(&sig, &hash.0).ok()` with `secp256k1::recover_signer_unchecked(&sig, &hash.0).ok()`.

2. In `crates/primitives/src/transaction/signature.rs`, the patch replaces `/// Recover signer address from message hash.` with `/// Recover signer from message hash, _without ensuring that the signature has a low 's'`.

3. In `crates/primitives/src/transaction/signature.rs`, the patch replaces `return Err(RlpError::Custom("invalid Ethereum signature (V is not 27 or 28)"))` with `return Err(RlpError::Custom("invalid Ethereum signature (V is not 27 or 28)"));`.

4. In `crates/primitives/src/transaction/signature.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `crates/primitives/src/transaction`, `crates/primitives/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/primitives/src/transaction/pooled.rs`, `crates/primitives/src/transaction/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/primitives/src/transaction/pooled.rs`, `crates/primitives/src/transaction/mod.rs`. The strongest project-level identifiers around this patch are `signature`, `hash`, `RlpError::Custom`, and `from`.

## Before/After Behavior

Before the patch, the shown recovery implementation called `secp256k1::recover_signer(&sig, &hash.0).ok()` and there was no separately named unchecked compatibility API in the supplied excerpts. After the patch, that behavior is exposed as `recover_signer_unchecked`, the checked `recover_signer` adds `if self.s > SECP256K1N_HALF { return None; }`, and a regression test asserts that a known high-s pre-Homestead transaction is rejected by the checked API.

# Root Cause

The `Signature` API did not explicitly separate EIP-2-compliant signer recovery from legacy-compatible recovery, leaving the low-s invariant implicit rather than enforced at a clearly named checked boundary.

## Walkthrough

1. The patch introduces `recover_signer_unchecked`, whose documentation says it may accept malleable or non-EIP-2-compliant signatures for compatibility with old data.

2. The unchecked helper builds the 65-byte signature and calls `secp256k1::recover_signer_unchecked(&sig, &hash.0).ok()`.

3. A separate checked `recover_signer` is added immediately after it.

4. That checked function rejects `self.s > SECP256K1N_HALF` before attempting recovery.

5. The new test `eip_2_reject_high_s_value` decodes a known pre-Homestead raw transaction and states that the checked `recover_signer` should reject it.

6. The supplied evidence does not show which caller paths use the checked versus unchecked API, so broader exploitation or reachability claims are not established here.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/primitives/src/transaction/signature.rs | 136 | Splits signer recovery into checked validation and unchecked legacy-compatibility paths |
| crates/primitives/src/transaction/signature.rs | 151 | Enforces the EIP-2 low-s guard before recovering the signer address |
| crates/stages/src/stages/sender_recovery.rs | 1 | Caller-side historical sender recovery path that likely needs unchecked recovery for pre-Homestead signatures |
| crates/primitives/src/transaction/signature.rs | 313 | Regression test proving high-s signatures are rejected by the checked recovery API |

## Code Snippets

## Snippet 1

Context: `crates/primitives/src/transaction/signature.rs:151` (changes signature or replay validation logic)

Before
```rust
// NOTE: we are removing error from underlying crypto library as it will restrain primitive
        // errors and we care only if recovery is passing or not.
        secp256k1::recover_signer(&sig, &hash.0).ok()
    }
```
After
```rust
// NOTE: we are removing error from underlying crypto library as it will restrain primitive
        // errors and we care only if recovery is passing or not.
        secp256k1::recover_signer_unchecked(&sig, &hash.0).ok()
    }

    /// Recover signer address from message hash. This ensures that the signature S value is
    /// greater than `secp256k1n / 2`, as specified in
    /// [EIP-2](https://eips.ethereum.org/EIPS/eip-2).
```

## Snippet 2

Context: `crates/primitives/src/transaction/signature.rs:136` (changes signature or replay validation logic)

Before
```rust
}

    /// Recover signer address from message hash.
    pub fn recover_signer(&self, hash: B256) -> Option<Address> {
        let mut sig: [u8; 65] = [0; 65];
```
After
```rust
}

    /// Recover signer from message hash, _without ensuring that the signature has a low `s`
    /// value_.
    ///
    /// Using this for signature validation will succeed, even if the signature is malleable or not
    /// compliant with EIP-2. This is provided for compatibility with old signatures which have
    /// large `s` values.
```

## Snippet 3

Context: `crates/primitives/src/transaction/signature.rs:108` (changes signature or replay validation logic)

Before
```rust
// non-EIP-155 legacy scheme, v = 27 for even y-parity, v = 28 for odd y-parity
            if v != 27 && v != 28 {
                return Err(RlpError::Custom("invalid Ethereum signature (V is not 27 or 28)"))
            }
            let odd_y_parity = v == 28;
```
After
```rust
// non-EIP-155 legacy scheme, v = 27 for even y-parity, v = 28 for odd y-parity
            if v != 27 && v != 28 {
                return Err(RlpError::Custom("invalid Ethereum signature (V is not 27 or 28)"));
            }
            let odd_y_parity = v == 28;
```

## Snippet 4

Context: `crates/primitives/src/transaction/signature.rs:313` (changes signature or replay validation logic)

Before
```rust
assert!(signature.size() >= 65);
    }
}
```
After
```rust
assert!(signature.size() >= 65);
    }

    #[test]
    fn eip_2_reject_high_s_value() {
        // This pre-homestead transaction has a high `s` value and should be rejected by the
        // `recover_signer` method:
        // https://etherscan.io/getRawTx?tx=0x9e6e19637bb625a8ff3d052b7c2fe57dc78c55a15d258d77c43d5a9c160b0384
```

# Fix Pattern

Split a compatibility-oriented helper from the validation-oriented API, and make the validation path enforce the protocol invariant explicitly with a local guard and regression test.

## How It Was Fixed

The fix creates two recovery entry points with distinct semantics. `recover_signer_unchecked` preserves permissive recovery for historical signatures, while the new `recover_signer` enforces the EIP-2 low-s rule by returning `None` when `s` exceeds `SECP256K1N_HALF`. A test was added to pin that checked behavior on a real high-s transaction sample.

# Why It Matters

1. It makes low-s enforcement explicit in the checked recovery API.

2. It preserves historical compatibility without silently weakening the checked path.

3. It reduces the chance that callers use a permissive recovery routine for validation by accident.

# Evidence Notes

Direct evidence is limited to `crates/primitives/src/transaction/signature.rs`: the old recovery call is moved under an unchecked helper, a new checked `recover_signer` adds an explicit high-s rejection, and a test covers rejection of a known high-s transaction. The touched file list includes `crates/stages/src/stages/sender_recovery.rs`, but no caller-side diff is provided, so any claim about how the new APIs are used outside `Signature` is inference only. The evidence supports security-relevant hardening of signature-validation semantics, but not a proven exploitable vulnerability or consensus failure. Protocol security invariant: When signer recovery is used for normal Ethereum transaction validation, the EIP-2 low-s rule must be enforced so high-s signatures are not treated as canonical; any compatibility path for historical signatures must stay explicitly separate from that checked path. Verification notes: The patch does not prove that malformed post-Homestead transactions previously reached canonical execution. The diff does not by itself demonstrate a practical remote exploit or consensus split. The exact sender-recovery caller change is inferred from the touched file set and new checked/unchecked API split, not shown line-for-line here. The evidence does not quantify which network-facing surfaces, if any, exposed the pre-fix behavior. The added test shows the checked API rejects a concrete high-s transaction. The docs on `recover_signer_unchecked` explicitly warn that it may accept malleable signatures. No provided excerpt shows a caller that was previously vulnerable or a caller switched to the new checked API. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-malleability`
Final impact type: `non-canonical-signature-acceptance`
Final confidence: `medium`
Final tags: `signature, eip-2, malleability, transaction-validation, hardening`

The patch clearly hardens a security-sensitive transaction-signature boundary by separating unchecked legacy recovery from a checked `recover_signer` path that rejects high-`s` signatures per EIP-2, and by adding a regression test for a known high-`s` transaction. That supports retaining this as a security-hardening case focused on signature malleability and canonical validation. However, the supplied evidence does not prove that a reachable network-facing validation path previously accepted invalid post-Homestead transactions or that a concrete exploit occurred, so it should not be escalated to a confirmed security-fix.

## Security Evidence

1. A new checked `recover_signer` rejects signatures where `s > SECP256K1N_HALF`.
2. The old behavior is preserved under an explicitly named `recover_signer_unchecked` compatibility API.
3. The unchecked API documentation warns it may accept malleable, non-EIP-2-compliant signatures.
4. A regression test asserts that a known high-`s` pre-Homestead transaction is rejected by the checked API.
5. The change is in transaction signature recovery, a cryptographically sensitive validation path.

## Missing Evidence

1. No caller-side diff is shown proving validation paths were switched to the checked API.
2. No evidence shows previously accepted high-`s` signatures could reach canonical processing after EIP-2 rules should apply.
3. No proof of a concrete exploit, replay, consensus failure, or externally reachable vulnerability is provided.
4. The `sender_recovery.rs` change is mentioned in metadata but not shown in the patch excerpts.

## Claim Boundaries

1. This supports security hardening of signature-validation semantics, not a proven exploitable bug fix.
2. The evidence supports concern about signature malleability and non-canonical signature acceptance only.
3. Replay, forgery, or consensus-impact claims are not established by the supplied patch alone.
4. Compatibility for historical high-`s` signatures remains intentional via the unchecked recovery helper.
