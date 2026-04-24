---
case_id: case_20210901_779a646e14
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2021-09-01
source_refs:
  - git:779a646e14f451b5f1d2790413501ad702a52e30
  - "fastpay_core/src/base_types.rs:269"
  - "fastpay_core/src/messages.rs:162"
  - "fastpay_core/src/messages.rs:291"
  - "fastpay/src/client.rs:146"
bug_class: signature-canonicalization-hardening
impact_type:
  - cryptographic-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - signature
  - bcs
  - canonical-serialization
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Commit 779a646e14 changes FastPay signature material from a hand-written Digestible/Sha512 path for Transfer to a Signable/BcsSignable path described as serde plus BCS canonical bytes. It also updates observed signature creation paths to sign value.transfer or certificate.value.transfer. This is security-relevant cryptographic serialization hardening, but the evidence does not prove a vulnerability fix.

## Observed Patch Facts

1. In `fastpay_core/src/base_types.rs`, the patch replaces `pub trait Digestible {` with `/// Something that we know how to hash and sign.`.

2. In `fastpay_core/src/messages.rs`, the patch replaces `impl Digestible for Transfer {` with `impl SignedTransferOrder {`.

3. In `fastpay_core/src/messages.rs`, the patch adds `impl BcsSignable for Transfer {}`.

4. In `fastpay/src/client.rs`, the patch replaces `let sig = Signature::new(&certificate.value, secx);` with `let sig = Signature::new(&certificate.value.transfer, secx);`.

## Project Context

The changed code sits primarily in `fastpay_core/src`, `fastpay/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `fastpay/src/bench.rs`, `fastpay_core/src/fastpay_smart_contract.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `fastpay/src/bench.rs`, `fastpay_core/src/fastpay_smart_contract.rs`. The strongest project-level identifiers around this patch are `Signature::new`, `digest`, `impl`, and `value`. Nearby tests or test-like files include `fastpay_core/src/unit_tests/serialize_tests.rs`, `fastpay_core/src/unit_tests/downloader_tests.rs`.

## Before/After Behavior

Before the patch, Transfer had a visible manual Digestible implementation that fed selected fields into Sha512, and at least one certificate construction path signed the enclosing order value. After the patch, Transfer is marked BcsSignable, the base signing abstraction refers to BCS canonical bytes, and observed signing paths sign the embedded Transfer payload directly.

# Root Cause

The grounded issue is a change in signature serialization and payload selection: the old code used a bespoke digest implementation for Transfer and some call sites signed wrapper values. The evidence does not prove that this caused invalid signature acceptance, signature forgery, replay, panic, or denial of service.

## Walkthrough

1. base_types.rs replaces the visible Digestible trait with Signable and BcsSignable, with comments describing serde names and BCS canonical bytes for hashing and signing.

2. messages.rs removes the visible manual Digestible implementation for Transfer that updated a Sha512 hasher field by field.

3. SignedTransferOrder::new now signs value.transfer rather than a broader wrapper object.

4. messages.rs adds impl BcsSignable for Transfer, enabling the BCS-backed signing path for Transfer.

5. client.rs benchmark certificate construction now signs certificate.value.transfer instead of certificate.value.

6. The supplied evidence places the change in FastPay transfer/order signature handling, but does not show a failing verification path or exploitable pre-patch behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| fastpay_core/src/base_types.rs | 269 | Defines the signing abstraction and replaces the prior Digestible trait with Signable/BcsSignable backed by serde and BCS canonical bytes. |
| fastpay_core/src/messages.rs | 162 | Transfer signature verification and signed transfer construction now operate on the Transfer payload being authenticated. |
| fastpay_core/src/messages.rs | 291 | Marks Transfer as BcsSignable, making it eligible for canonical BCS-based signing. |
| fastpay/src/client.rs | 146 | Benchmark certificate construction now signs certificate.value.transfer instead of the enclosing order value. |

## Code Snippets

## Snippet 1

Context: `fastpay_core/src/base_types.rs:269` (changes signature or replay validation logic)

Before
```rust
}

pub trait Digestible {
    fn digest(&self) -> [u8; 32];
}

#[cfg(test)]
impl Digestible for [u8; 5] {
```
After
```rust
}

/// Something that we know how to hash and sign.
pub trait Signable<Hasher> {
    fn write(&self, hasher: &mut Hasher);
}

/// Activate the blanket implementation of `Signable` based on serde and BCS.
```

## Snippet 2

Context: `fastpay_core/src/messages.rs:162` (changes signature or replay validation logic)

Before
```rust
}

impl Digestible for Transfer {
    fn digest(self: &Transfer) -> [u8; 32] {
        let mut h: Sha512 = Sha512::new();
        let mut hash: [u8; 64] = [0u8; 64];
        let mut digest: [u8; 32] = [0u8; 32];
```
After
```rust
}

impl SignedTransferOrder {
    /// Use signing key to create a signed object.
    pub fn new(value: TransferOrder, authority: AuthorityName, secret: &SecretKey) -> Self {
        let signature = Signature::new(&value.transfer, secret);
        Self {
            value,
```

## Snippet 3

Context: `fastpay_core/src/messages.rs:291` (changes a sensitive control or state-update path)

Before
```rust
}
}
```
After
```rust
}
}

impl BcsSignable for Transfer {}
```

## Snippet 4

Context: `fastpay/src/client.rs:146` (changes signature or replay validation logic)

Before
```rust
for i in 0..committee.quorum_threshold() {
            let (pubx, secx) = keys.get(i).unwrap();
            let sig = Signature::new(&certificate.value, secx);
            certificate.signatures.push((*pubx, sig));
        }
```
After
```rust
for i in 0..committee.quorum_threshold() {
            let (pubx, secx) = keys.get(i).unwrap();
            let sig = Signature::new(&certificate.value.transfer, secx);
            certificate.signatures.push((*pubx, sig));
        }
```

# Fix Pattern

Replace ad hoc signature digest construction with a canonical serialization-backed signing interface and align signature creation call sites on the intended Transfer payload.

## How It Was Fixed

The patch introduces Signable/BcsSignable, registers Transfer as BcsSignable, removes the visible manual Transfer digest implementation, and updates observed signing call sites to pass the embedded Transfer payload to Signature::new.

# Why It Matters

1. Canonical bytes reduce ambiguity in signed data.

2. Signing the intended payload helps keep clients and validators aligned on what is authenticated.

3. The evidence supports hardening, not a confirmed vulnerability remediation.

# Evidence Notes

Primary evidence comes from fastpay_core/src/base_types.rs, fastpay_core/src/messages.rs, and fastpay/src/client.rs. The mapper correctly rejects the heuristic panic/liveness narrative. No supplied snippet proves invalid signatures were accepted, no exploit path is shown, and the client benchmark change may be compatibility support rather than production vulnerability remediation. Protocol security invariant: FastPay signatures should authenticate the intended Transfer payload using a deterministic byte representation shared by signing and verification. The patch changes the signing abstraction toward BCS-backed bytes and updates observed signing call sites to sign the embedded Transfer, but the provided evidence does not establish that the prior behavior allowed forgery, replay, invalid signature acceptance, or consensus divergence. Verification notes: No evidence proves that invalid signatures were accepted before the patch. No evidence proves a remote exploit, denial of service, or consensus failure. No evidence supports the heuristic claim about panic-prone conversion or malformed decoded values. No evidence shows whether the old manual digest was non-canonical in a practically exploitable way. Benchmark/client changes may be compatibility updates rather than production vulnerability fixes. No evidence of a concrete signature bypass was provided. No evidence of replay, consensus failure, or denial of service was provided. No evidence supports classifying this as a liveness failure. Keep out of the security-fix corpus because the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-canonicalization-hardening`
Final impact type: `cryptographic-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, signature, bcs, canonical-serialization, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The commit moves signature material from a bespoke Digestible/Sha512 implementation toward BCS-backed canonical serialization and aligns signing call sites to the Transfer payload that verification checks. That is a clear tightening of cryptographic signing behavior, but the evidence does not prove prior forgery, replay, invalid signature acceptance, consensus failure, or liveness impact.

## Security Evidence

1. Commit subject is explicitly about signature handling: "Use BCS for signature".
2. base_types.rs introduces Signable/BcsSignable and comments that BCS generates canonical bytes suitable for hashing and signing.
3. messages.rs removes the visible manual Digestible implementation for Transfer and adds impl BcsSignable for Transfer.
4. SignedTransferOrder::new signs value.transfer, matching the shown check_signature behavior against self.transfer.
5. client.rs benchmark certificate construction changes signatures from certificate.value to certificate.value.transfer.

## Missing Evidence

1. No failing verification path or exploit scenario is shown.
2. No evidence shows that the old manual digest was ambiguous or practically bypassable.
3. No evidence shows invalid signatures were accepted before the patch.
4. No evidence supports the original liveness-failure impact claim.
5. No production validator or consensus failure is demonstrated.

## Claim Boundaries

1. Classify as canonical-signature serialization hardening only.
2. Do not claim a concrete signature forgery, replay vulnerability, or authentication bypass.
3. Do not claim liveness or denial-of-service impact from the supplied evidence.
4. Client benchmark changes should be treated as supporting alignment evidence, not proof of a production vulnerability.
