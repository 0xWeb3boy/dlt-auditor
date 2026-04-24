---
case_id: case_20220125_f95e29b749
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2022-01-25
source_refs:
  - git:f95e29b749961d4c9a58863ad0aa4bacbee9b846
  - "fastx_types/src/messages.rs:91"
  - "fastx_types/src/messages.rs:242"
  - "fastx_types/src/messages.rs:79"
  - "fastx_types/src/messages.rs:127"
bug_class: unsafe-certificate-comparison-semantics
impact_type:
  - protocol-integrity
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - certificate-comparison
  - signature-semantics
  - api-hardening
  - compile-time-guard
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch removes generic equality and hashing support from CertifiedOrder and from structs that embed it, because comparing or hashing certificates by their concrete signature sets can encode misleading certificate identity semantics. The supplied evidence supports security-relevant API hardening, but it does not show a concrete vulnerable caller, exploit path, or demonstrated runtime security failure.

## Observed Patch Facts

1. In `fastx_types/src/messages.rs`, the patch replaces `#[derive(Eq, PartialEq, Clone, Debug, Serialize, Deserialize)]` with `// Note: if you meet an error due to this line it may be because you need an Eq imple...`.

2. In `fastx_types/src/messages.rs`, the patch replaces `impl Hash for CertifiedOrder {` with `impl Order {`.

3. In `fastx_types/src/messages.rs`, the patch replaces `#[derive(Eq, Clone, Debug, Serialize, Deserialize)]` with `///`.

4. In `fastx_types/src/messages.rs`, the patch replaces `#[derive(Debug, PartialEq, Eq, Hash, Clone, Serialize, Deserialize)]` with `#[derive(Debug, Clone, Serialize, Deserialize)]`.

## Project Context

The changed code sits primarily in `fastx_types/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `fastx_types/src/serialize.rs`, `fastx_types/src/object.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `fastx_types/src/object.rs`, `fastx_types/src/error.rs`. The strongest project-level identifiers around this patch are `derive`, `Clone`, `Debug`, and `Serialize`. Nearby tests or test-like files include `fastx_types/src/unit_tests/serialize_tests.rs`, `fastx_types/src/unit_tests/base_types_tests.rs`.

## Before/After Behavior

Before the patch, CertifiedOrder derived Eq and had explicit Hash and PartialEq implementations; the removed Hash implementation included the order, signature count, and signer names. Certificate-bearing structs such as ConfirmationOrder and ObjectInfoResponse also derived equality or hashing traits. After the patch, CertifiedOrder only derives Clone, Debug, Serialize, and Deserialize, and the dependent structs no longer expose equality or hash derives that would transitively depend on CertifiedOrder.

# Root Cause

The code exposed generic Eq/Hash behavior for a certificate type whose structural signature-set fields do not necessarily match the protocol-level identity of a certified order. The evidence does not establish that this API surface was actually misused in a vulnerable path.

## Walkthrough

1. CertifiedOrder represents an order plus a vector of quorum signatures.

2. The patch documents that the signature set is not necessarily unique: more than one valid certificate may exist for the same transaction.

3. Before the change, CertifiedOrder supported Eq, PartialEq, and Hash semantics that could account for concrete signature-set details.

4. Types containing CertifiedOrder also derived equality or hashing traits before the patch.

5. The patch removes those trait implementations and derives, forcing future code to handle certificate comparison deliberately.

6. The added comments warn that valid certificates with distinct signatures may be equivalent, while unchecked certificates with different signer sets should not be blindly treated as equivalent.

7. No supplied evidence shows an existing unsafe deduplication, map lookup, consensus failure, double-spend, or privilege impact.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| fastx_types/src/messages.rs | 79 | Defines CertifiedOrder as an order plus quorum signatures and removes Eq-derived semantics from the certificate type. |
| fastx_types/src/messages.rs | 85 | Documents the certificate identity invariant and adds compile-time pressure against implementing Hash or Eq incorrectly. |
| fastx_types/src/messages.rs | 91 | Removes equality derivation from ConfirmationOrder because it embeds CertifiedOrder. |
| fastx_types/src/messages.rs | 127 | Removes PartialEq/Eq/Hash derivation from ObjectInfoResponse because it can carry a CertifiedOrder. |
| fastx_types/src/messages.rs | 242 | Deletes the prior CertifiedOrder Hash and PartialEq implementations that incorporated signature-set details. |

## Code Snippets

## Snippet 1

Context: `fastx_types/src/messages.rs:91` (changes signature or replay validation logic)

Before
```rust
}

#[derive(Eq, PartialEq, Clone, Debug, Serialize, Deserialize)]
pub struct ConfirmationOrder {
    pub certificate: CertifiedOrder,
```
After
```rust
}

// Note: if you meet an error due to this line it may be because you need an Eq implementation for `CertifiedOrder`,
// or one of the structs that include it, i.e. `ConfirmationOrder`, `OrderInforResponse` or `ObjectInforResponse`.
//
// Please note that any such implementation must be agnostic to the exact set of signatures in the certificate, as
// clients are allowed to equivocate on the exact nature of valid certificates they send to the system. This assertion
// is a simple tool to make sure certifcates are accounted for correctly - should you remove it, you're on your own to
```

## Snippet 2

Context: `fastx_types/src/messages.rs:242` (changes signature or replay validation logic)

Before
```rust
}

impl Hash for CertifiedOrder {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.order.hash(state);
        self.signatures.len().hash(state);
        for (name, _) in self.signatures.iter() {
            name.hash(state);
```
After
```rust
}

impl Order {
    pub fn new(kind: OrderKind, secret: &KeyPair) -> Self {
```

## Snippet 3

Context: `fastx_types/src/messages.rs:79` (changes a sensitive control or state-update path)

Before
```rust
/// An order signed by a quorum of authorities
#[derive(Eq, Clone, Debug, Serialize, Deserialize)]
pub struct CertifiedOrder {
    pub order: Order,
```
After
```rust
/// An order signed by a quorum of authorities
///
/// Note: the signature set of this data structure is not necessarily unique in the system,
/// i.e. there can be several valid certificates per transaction.
///
/// As a consequence, we check this struct does not implement Hash or Eq, see the note below.
///
```

## Snippet 4

Context: `fastx_types/src/messages.rs:127` (changes a sensitive control or state-update path)

Before
```rust
}

#[derive(Debug, PartialEq, Eq, Hash, Clone, Serialize, Deserialize)]
pub struct ObjectInfoResponse {
    pub requested_certificate: Option<CertifiedOrder>,
```
After
```rust
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObjectInfoResponse {
    pub requested_certificate: Option<CertifiedOrder>,
```

# Fix Pattern

Remove misleading generic equality and hashing implementations from certificate-bearing types when structural fields do not safely represent protocol identity.

## How It Was Fixed

The patch removes Eq derivation from CertifiedOrder, deletes its explicit Hash and PartialEq implementations, and removes PartialEq/Eq/Hash derives from containing response/order structs. It adds comments documenting the intended certificate comparison invariant and warning future implementers to account for validation state.

# Why It Matters

1. Reduces risk of accidental signature-set-based certificate identity checks.

2. Makes future comparison or deduplication code fail at compile time unless deliberately implemented.

3. Preserves an important distinction between validated and unchecked certificates.

4. Does not by itself prove a concrete vulnerability was fixed.

# Evidence Notes

Grounded evidence is limited to fastx_types/src/messages.rs changes: CertifiedOrder stops deriving Eq, its Hash and PartialEq implementations are deleted, and ConfirmationOrder/ObjectInfoResponse stop deriving comparison or hash traits. The commit message and comments explain the intended invariant. The evidence does not include a vulnerable caller or runtime behavior demonstrating exploitation. Protocol security invariant: A CertifiedOrder's concrete signature set is not a unique certificate identity: multiple distinct quorum signature sets can certify the same order, and comparison semantics depend on whether certificates have already been validated. Verification notes: No concrete vulnerable caller is shown using CertifiedOrder equality or hashing unsafely. No exploitability, privilege escalation, double-spend, or consensus failure is proven by the patch alone. The change is compile-time API hardening rather than a runtime validation check. The patch does not implement a correct signature-agnostic Eq; it prevents accidental use until validation-state distinctions exist. No concrete exploit path is shown in the provided input. No vulnerable use of dedup, HashMap, HashSet, or equality comparison is identified. Treat as possible security-relevant hardening, not a confirmed security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unsafe-certificate-comparison-semantics`
Final impact type: `protocol-integrity, state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, certificate-comparison, signature-semantics, api-hardening, compile-time-guard`

The supplied evidence supports retaining this as security hardening, not a confirmed security fix. The patch removes Eq/Hash/PartialEq behavior from CertifiedOrder and dependent types, and the added comments explain that valid certificates may differ by signature set while representing the same certified order, with different semantics before validation. That is a security-sensitive invariant in certificate/order handling, but the evidence does not show an actual vulnerable caller or exploit path.

## Security Evidence

1. CertifiedOrder represents an order signed by a quorum of authorities and carries a signature vector.
2. The patch removes Eq/Hash/PartialEq behavior that previously encoded concrete signature-set details into identity semantics.
3. Added comments state that multiple valid certificates can exist for the same transaction and that clients may equivocate on exact signature sets.
4. The change forces future certificate comparison or hashing decisions to be deliberate rather than silently inherited through generic traits.
5. Containing types such as ConfirmationOrder and ObjectInfoResponse also stop deriving equality or hashing traits that would depend on CertifiedOrder.

## Missing Evidence

1. No concrete caller is shown misusing CertifiedOrder equality, hashing, deduplication, HashMap, or HashSet behavior.
2. No demonstrated exploit, consensus failure, double spend, replay issue, or state corruption path is provided.
3. No runtime validation change is shown; the patch is primarily API restriction and compile-time pressure.
4. No test evidence in the supplied input proves a previously failing security scenario.

## Claim Boundaries

1. Classify as security hardening rather than a confirmed vulnerability fix.
2. Do not claim proven state corruption or exploitable transaction-processing failure from this evidence alone.
3. Do not claim the patch implements correct certificate equality; it removes unsafe generic equality and hashing semantics.
4. The supported security claim is limited to preventing accidental misuse of certificate identity semantics around signature sets.
