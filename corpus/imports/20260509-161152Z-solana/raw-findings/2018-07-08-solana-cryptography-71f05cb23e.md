---
case_id: case_20180708_71f05cb23e
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2018-07-08
source_refs:
  - git:71f05cb23e447dd8edb1b38c7ef0ff8463c18354
  - "src/budget.rs:102"
  - "src/budget.rs:161"
  - "src/budget.rs:119"
  - "src/budget.rs:144"
bug_class: timestamp-source-authorization
impact_type:
  - unauthorized-condition-satisfaction
confidence: medium
tags:
  - blockchain-core
  - payment-plan
  - timestamp
  - authorization
  - contract-witness
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes budget timestamp witness evaluation so future-payment conditions are checked against an explicit source public key before a locked budget can reduce to a payment. The evidence supports a contract-level authorization fix for timestamp sources, without proving a full exploit path or concrete loss.

## Observed Patch Facts

1. In `src/budget.rs`, the patch replaces `fn apply_witness(&mut self, witness: &Witness) {` with `fn apply_witness(&mut self, witness: &Witness, from: &PublicKey) {`.

2. In `src/budget.rs`, the patch replaces `let to = PublicKey::default();` with `let from = KeyPair::new().pubkey();`.

3. In `src/budget.rs`, the patch replaces `let sig = PublicKey::default();` with `let from = PublicKey::default();`.

4. In `src/budget.rs`, the patch replaces `assert!(Budget::new_future_payment(dt, 42, to).verify(42));` with `assert!(Budget::new_future_payment(dt, from, 42, to).verify(42));`.

## Project Context

The changed code sits primarily in `src`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/transaction.rs`, `src/payment_plan.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/transaction.rs`, `src/thin_client.rs`. The strongest project-level identifiers around this patch are `Budget`, `from`, `Budget::Or`, and `cond`.

## Before/After Behavior

Before the patch, `Budget::apply_witness` accepted only a `Witness` and reduced `Budget::After` or `Budget::Or` when `cond.is_satisfied(witness)` returned true. The old future-payment test showed `Budget::new_future_payment(dt, 42, to)` reducing after `Witness::Timestamp(dt)` with no source key passed into the decision. After the patch, `apply_witness` accepts `(&Witness, &PublicKey)`, forwards the key to `cond.is_satisfied(witness, from)`, and future-payment construction includes the trusted `from` key. Tests now cover authorized timestamp use and an unauthorized timestamp source case.

# Root Cause

The budget condition evaluation did not receive the public key associated with the witness source, so timestamp satisfaction could be based on the timestamp witness value alone rather than on whether the timestamp came from a contract-approved authority.

## Walkthrough

1. A budget can reduce to a payment when an `After` or `Or` condition is satisfied by a witness.

2. Before the fix, `apply_witness` evaluated conditions using only `cond.is_satisfied(witness)`.

3. For timestamp-based future payments, the shown test demonstrates that a timestamp witness alone could trigger reduction to `Budget::Pay`.

4. The patch changes `apply_witness` to also receive a `PublicKey` source and pass it into every condition satisfaction check.

5. Future-payment creation now records a trusted source key, allowing the contract condition to decide whether to trust a timestamp from that key.

6. The added unauthorized future-payment test supports the intended behavior that timestamps from non-whitelisted keys are rejected.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/budget.rs | 102 | Budget::apply_witness now passes the verified source public key into condition satisfaction before reducing a budget to a payment. |
| src/budget.rs | 119 | Condition signature/timestamp satisfaction tests reflect source-key based authorization rather than trusting witness payload alone. |
| src/budget.rs | 161 | Future-payment tests show authorized timestamp witnesses reduce the budget and unauthorized timestamp sources are rejected. |
| src/payment_plan.rs | 1 | Witness timestamp events are the payment-plan inputs used by the interpreter to reduce contracts into executable payments. |
| src/transaction.rs | 1 | Transactions carry signatures and public keys used to associate a witness with a verified sender/source before contract evaluation. |

## Code Snippets

## Snippet 1

Context: `src/budget.rs:102` (changes a sensitive control or state-update path)

Before
```rust
/// Apply a witness to the budget to see if the budget can be reduced.
    /// If so, modify the budget in-place.
    fn apply_witness(&mut self, witness: &Witness) {
        let new_payment = match self {
            Budget::After(cond, payment) if cond.is_satisfied(witness) => Some(payment),
            Budget::Or((cond, payment), _) if cond.is_satisfied(witness) => Some(payment),
            Budget::Or(_, (cond, payment)) if cond.is_satisfied(witness) => Some(payment),
            _ => None,
```
After
```rust
/// Apply a witness to the budget to see if the budget can be reduced.
    /// If so, modify the budget in-place.
    fn apply_witness(&mut self, witness: &Witness, from: &PublicKey) {
        let new_payment = match self {
            Budget::After(cond, payment) if cond.is_satisfied(witness, from) => Some(payment),
            Budget::Or((cond, payment), _) if cond.is_satisfied(witness, from) => Some(payment),
            Budget::Or(_, (cond, payment)) if cond.is_satisfied(witness, from) => Some(payment),
            _ => None,
```

## Snippet 2

Context: `src/budget.rs:161` (changes the branch that decides whether execution stops or continues)

Before
```rust
fn test_future_payment() {
        let dt = Utc.ymd(2014, 11, 14).and_hms(8, 9, 10);
        let to = PublicKey::default();

        let mut budget = Budget::new_future_payment(dt, 42, to);
        budget.apply_witness(&Witness::Timestamp(dt));
        assert_eq!(budget, Budget::new_payment(42, to));
    }
```
After
```rust
fn test_future_payment() {
        let dt = Utc.ymd(2014, 11, 14).and_hms(8, 9, 10);
        let from = KeyPair::new().pubkey();
        let to = KeyPair::new().pubkey();

        let mut budget = Budget::new_future_payment(dt, from, 42, to);
        budget.apply_witness(&Witness::Timestamp(dt), &from);
        assert_eq!(budget, Budget::new_payment(42, to));
```

## Snippet 3

Context: `src/budget.rs:119` (changes signature or replay validation logic)

Before
```rust
mod tests {
    use super::*;

    #[test]
    fn test_signature_satisfied() {
        let sig = PublicKey::default();
        assert!(Condition::Signature(sig).is_satisfied(&Witness::Signature(sig)));
    }
```
After
```rust
mod tests {
    use super::*;
    use signature::{KeyPair, KeyPairUtil};

    #[test]
    fn test_signature_satisfied() {
        let from = PublicKey::default();
        assert!(Condition::Signature(from).is_satisfied(&Witness::Signature, &from));
```

## Snippet 4

Context: `src/budget.rs:144` (changes signature or replay validation logic)

Before
```rust
assert!(Budget::new_payment(42, to).verify(42));
        assert!(Budget::new_authorized_payment(from, 42, to).verify(42));
        assert!(Budget::new_future_payment(dt, 42, to).verify(42));
        assert!(Budget::new_cancelable_future_payment(dt, from, 42, to).verify(42));
    }
```
After
```rust
assert!(Budget::new_payment(42, to).verify(42));
        assert!(Budget::new_authorized_payment(from, 42, to).verify(42));
        assert!(Budget::new_future_payment(dt, from, 42, to).verify(42));
        assert!(Budget::new_cancelable_future_payment(dt, from, 42, to).verify(42));
    }
```

# Fix Pattern

Propagate source identity into condition evaluation and require timestamp witnesses to match the authority encoded in the budget condition before performing the state transition.

## How It Was Fixed

The patch threads a `PublicKey` parameter through budget witness application and condition satisfaction. Future-payment constructors and tests were updated to include the trusted timestamp source, and a regression test was added for unauthorized timestamp sources. Signature witness tests were also adjusted to compare against the externally supplied source key rather than a key embedded in the witness payload.

# Why It Matters

1. Prevents budget contracts from trusting network-provided timestamps by default.

2. Keeps timestamp authority selection inside the contract condition.

3. Makes payment release depend on both witness content and source identity.

4. Adds regression coverage for unauthorized timestamp sources.

# Evidence Notes

Primary evidence comes from `src/budget.rs`: `apply_witness` now takes `from: &PublicKey`, calls `cond.is_satisfied(witness, from)`, future-payment tests now include a `from` key, and an unauthorized future-payment test was added. The commit message explicitly states contracts should not trust the network for timestamps and should decide whether to trust the timestamp source. The provided evidence does not establish remote exploitability, broken signature verification, or specific economic impact. Protocol security invariant: Budget contracts that reduce locked payments based on timestamp witnesses must not treat network-provided time as inherently trusted; timestamp satisfaction must depend on the witness value and the public key source the contract is willing to trust. Verification notes: The patch does not by itself prove remote exploitability or a complete attack path. The evidence does not show signature verification was broken; it shows the verified key was not passed into the contract decision. The economic impact or ability to steal funds is not established from the provided patch alone. This is not a serialization, migration, or test-only cleanup; runtime authorization behavior changes are shown. Runtime authorization behavior changed, not just tests or cleanup. The vulnerability thesis is limited to timestamp-source authorization for budget reduction. No full attack path or loss scenario is proven by the provided evidence. Helper or related files are supporting context, not shown as the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `timestamp-source-authorization`
Final impact type: `unauthorized-condition-satisfaction`
Final confidence: `medium`
Final tags: `blockchain-core, payment-plan, timestamp, authorization, contract-witness`

The supplied evidence supports keeping this as security hardening, but the phase-3 finding is stronger than the patch alone proves. The commit and tests show budget contracts stopped accepting timestamp witnesses based only on the timestamp value and began checking the witness source public key against the contract-approved key. That is security-sensitive authorization behavior for payment-plan reduction, but the evidence does not establish a concrete exploit path, loss scenario, or broken cryptographic verification, so security-fix/high confidence is too strong.

## Security Evidence

1. Commit message says contracts should not trust the network for timestamps.
2. Budget::apply_witness now receives a source PublicKey and passes it into condition checks.
3. Future-payment construction now records a trusted source key.
4. Tests include an unauthorized future-payment case requiring timestamps to come from a whitelisted public key.
5. Payment-plan context says witnesses reduce contracts into executable payments.

## Missing Evidence

1. No issue text for #405 is provided.
2. No concrete attacker flow is shown.
3. No evidence of actual fund theft, premature payment execution in production, or network exploitability is provided.
4. No full before/after implementation of Condition::is_satisfied is included.
5. No proof that signature verification itself was broken.

## Claim Boundaries

1. Validated only as timestamp-source authorization hardening for budget witness evaluation.
2. Do not claim a proven cryptographic signature bypass.
3. Do not claim confirmed economic loss or fund theft.
4. Do not claim remote exploitability from the patch alone.
5. The strongest supported impact is unauthorized satisfaction of a timestamp-based contract condition.
