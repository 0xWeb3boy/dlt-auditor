---
case_id: case_20210713_8a576d6c5
project: snarkvm
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2021-07-13
source_refs:
  - git:8a576d6c5e369552d5c5987a9aeb3dc14cac8106
  - "gadgets/src/algorithms/signature/tests.rs:188"
  - "gadgets/src/algorithms/signature/tests.rs:23"
  - "gadgets/src/algorithms/signature/group.rs:399"
bug_class: signature-transcript-length-binding
impact_type:
  - cryptographic-integrity
tags:
  - cryptography
  - signature
  - zk-gadget
  - message-length-binding
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes the GroupEncryption gadget signature verification hash input by inserting the message byte length before the message field elements are absorbed. This supports a likely security fix for message-length binding in the in-circuit signature verifier, but the provided evidence does not demonstrate a concrete forgery, exploit path, or downstream protocol impact.

## Observed Patch Facts

1. In `gadgets/src/algorithms/signature/tests.rs`, the patch replaces `fn failed_schnorr_signature_verification_test() {` with `fn group_schnorr_signature_verification_test() {`.

2. In `gadgets/src/algorithms/signature/tests.rs`, the patch adds `bls12_377::Fr,`.

3. In `gadgets/src/algorithms/signature/group.rs`, the patch adds `hash_input.push(FpGadget::<F>::Constant(F::from(message.len() as u128)));`.

## Project Context

The changed code sits primarily in `gadgets/src/algorithms/signature`, `gadgets/src/algorithms`, which anchors the finding in the `cryptography` area of the project. Historical context from `gadgets/src/algorithms/signature/schnorr.rs`, `gadgets/src/algorithms/signature/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `gadgets/src/algorithms/encryption/tests.rs`, `gadgets/src/algorithms/merkle_tree/tests.rs`. The strongest project-level identifiers around this patch are `bls12_377::Fr`, `traits::Group`, `EdwardsAffine`, and `message`.

## Before/After Behavior

Before the patch, `gadgets/src/algorithms/signature/group.rs` appended the claimed prover commitment field elements and then the message converted into constraint field elements, with no visible message-length element in between. After the patch, the verifier pushes `FpGadget::<F>::Constant(F::from(message.len() as u128))` into `hash_input` before appending the converted message. The test file also adds GroupEncryption-specific imports and a GroupEncryption gadget signature verification test.

# Root Cause

The apparent root cause was that the gadget verifier's hash preimage did not explicitly include the original message byte length. The evidence supports this as a message-length binding issue in the gadget verifier, while the exact ambiguity condition remains inferred rather than directly shown.

## Walkthrough

1. The affected implementation is `gadgets/src/algorithms/signature/group.rs` around the construction of `hash_input` for a Poseidon sponge.

2. Before the change, the hash input included the claimed prover commitment field elements followed by `message.to_constraint_field(...)`.

3. The patch inserts `message.len()` as a constant field element before the converted message.

4. This makes the in-circuit signature challenge depend on the message byte length as well as its field-element representation.

5. `gadgets/src/algorithms/signature/tests.rs` adds imports and a GroupEncryption gadget signature verification test that exercises the affected path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| gadgets/src/algorithms/signature/group.rs | 399 | Adds message length to the in-circuit signature verification hash preimage before appending message field elements. |
| gadgets/src/algorithms/signature/tests.rs | 188 | Adds a GroupEncryption gadget signature verification regression test exercising the affected verifier path. |
| gadgets/src/algorithms/signature/tests.rs | 23 | Adds GroupEncryption and EdwardsProjective imports needed to instantiate the group signature gadget test. |

## Code Snippets

## Snippet 1

Context: `gadgets/src/algorithms/signature/tests.rs:188` (changes signature or replay validation logic)

Before
```rust
}

#[test]
fn failed_schnorr_signature_verification_test() {
```
After
```rust
}

#[test]
fn group_schnorr_signature_verification_test() {
    type GroupSignature = GroupEncryption<EdwardsProjective, EdwardsAffine>;
    type GroupSignatureGadget =
        GroupEncryptionPublicKeyRandomizationGadget<EdwardsProjective, EdwardsAffine, Fr, EdwardsBls12Gadget>;
```

## Snippet 2

Context: `gadgets/src/algorithms/signature/tests.rs:23` (changes signature or replay validation logic)

Before
```rust
};
use snarkvm_algorithms::{signature::Schnorr, traits::SignatureScheme};
use snarkvm_curves::{bls12_377::Fr, edwards_bls12::EdwardsAffine, traits::Group};
use snarkvm_r1cs::{ConstraintSystem, TestConstraintSystem};
use snarkvm_utilities::{rand::UniformRand, to_bytes_le, ToBytes};

use rand::{thread_rng, Rng, SeedableRng};
use rand_chacha::ChaChaRng;
```
After
```rust
};
use snarkvm_algorithms::{signature::Schnorr, traits::SignatureScheme};
use snarkvm_curves::{
    bls12_377::Fr,
    edwards_bls12::{EdwardsAffine, EdwardsProjective},
    traits::Group,
};
use snarkvm_r1cs::{ConstraintSystem, TestConstraintSystem};
```

## Snippet 3

Context: `gadgets/src/algorithms/signature/group.rs:399` (changes a sensitive control or state-update path)

Before
```rust
.to_constraint_field(cs.ns(|| "convert claimed_prover_commitment into field elements"))?,
        );
        hash_input.extend_from_slice(&message.to_constraint_field(cs.ns(|| "convert message into field elements"))?);
```
After
```rust
.to_constraint_field(cs.ns(|| "convert claimed_prover_commitment into field elements"))?,
        );
        hash_input.push(FpGadget::<F>::Constant(F::from(message.len() as u128)));
        hash_input.extend_from_slice(&message.to_constraint_field(cs.ns(|| "convert message into field elements"))?);
```

# Fix Pattern

Bind variable-length transcript data unambiguously in cryptographic verification gadgets by including explicit length or boundary fields before hashing encoded message data.

## How It Was Fixed

The verifier hash preimage was updated to include `message.len()` as a field element before the message field elements are absorbed. A GroupEncryption gadget signature verification test was added to cover the path.

# Why It Matters

1. Signature challenge hashes should bind the exact verified message.

2. Variable-length encodings can be ambiguous without explicit length or boundary data.

3. The issue is limited by the supplied evidence to the gadget verifier path.

4. No practical forgery or transaction-level impact is shown.

# Evidence Notes

Primary evidence is the one-line implementation change in `gadgets/src/algorithms/signature/group.rs` adding `message.len()` to `hash_input`. Supporting evidence is the commit message naming GroupEncryption gadget signature verification and the added GroupEncryption-specific test. Claims about replay, state transitions, or native verifier behavior are unsupported by the provided evidence. Protocol security invariant: The in-circuit GroupEncryption/Schnorr-style signature verification challenge hash should bind the exact message being verified, including enough length or boundary information to avoid ambiguous encodings when variable-length message bytes are converted into field elements. Verification notes: No concrete exploit path is shown by the patch evidence. No evidence proves signature forgery is practical outside the gadget context. No downstream transaction or state-transition path is shown in the provided context. The patch does not show whether native non-gadget signature verification had the same issue. The precise collision or ambiguity condition caused by omitting message length is inferred from the hash-preimage change, not demonstrated directly. Do not classify this as replay based on the supplied evidence. Do not claim a concrete exploit or forgery was proven. Confidence is medium because the security relevance is strong, but the exact vulnerability condition is inferred from the fix. Helper/test changes are supporting evidence, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-transcript-length-binding`
Final impact type: `cryptographic-integrity`
Final tags: `cryptography, signature, zk-gadget, message-length-binding, security-hardening`

The supplied patch is clearly in a cryptographic signature verification gadget and adds the message byte length into the hash preimage before hashing the message field elements. That is a security-relevant tightening of transcript/message binding, supported by the commit subject and added GroupEncryption gadget verification test. However, the evidence does not prove a concrete exploit, replay path, or practical forgery, so this should be kept as security hardening rather than a confirmed security fix.

## Security Evidence

1. Commit subject explicitly says it fixes GroupEncryptionGadget signature verification.
2. Implementation change adds message.len() to the verification hash input.
3. The changed code is in a cryptographic signature gadget path.
4. A GroupEncryption gadget signature verification test was added alongside the implementation change.

## Missing Evidence

1. No demonstrated collision, ambiguity example, or forged signature is shown.
2. No downstream transaction, request, or replay path is evidenced.
3. No proof that native non-gadget verification was affected.
4. No advisory or vulnerability description is provided.

## Claim Boundaries

1. Treat as message-length binding hardening in the in-circuit GroupEncryption signature verifier.
2. Do not claim a proven replay vulnerability from the supplied evidence.
3. Do not claim a concrete exploitable forgery was demonstrated.
4. Do not generalize beyond the shown gadget verification path.
