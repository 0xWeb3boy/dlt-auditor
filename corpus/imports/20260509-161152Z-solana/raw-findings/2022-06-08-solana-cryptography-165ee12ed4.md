---
case_id: case_20220608_165ee12ed4
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2022-06-08
source_refs:
  - git:165ee12ed46fca585925cd1e61939c3bf12cf868
  - "sdk/src/nonce_account.rs:25"
  - "send-transaction-service/src/send_transaction_service.rs:238"
  - "runtime/src/nonce_keyed_account.rs:1107"
  - "sdk/src/nonce_account.rs:60"
bug_class: nonce-authority-validation
impact_type:
  - unauthorized-transaction-acceptance
  - replay-risk
confidence: medium
tags:
  - blockchain-core
  - durable-nonce
  - authorization
  - signature-validation
  - replay-sensitive
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The commit message states that durable nonce transactions not signed by the nonce authority are rejected. The shown code evidence supports part of that fix: nonce account verification now returns Option<Data> instead of a boolean, preserving initialized nonce account state for downstream validation. The exact authority-signature rejection branch is not present in the provided snippets, so this should be treated as a likely security fix rather than a fully demonstrated vulnerability/exploit.

## Observed Patch Facts

1. In `sdk/src/nonce_account.rs`, the patch replaces `pub fn verify_nonce_account(acc: &AccountSharedData, hash: &Hash) -> bool {` with `pub fn verify_nonce_account(acc: &AccountSharedData, hash: &Hash) -> Option<Data> {`.

2. In `send-transaction-service/src/send_transaction_service.rs`, the patch replaces `if !nonce_account::verify_nonce_account(&nonce_account, &durable_nonce)` with `if nonce_account::verify_nonce_account(&nonce_account, &durable_nonce).is_none()`.

3. In `runtime/src/nonce_keyed_account.rs`, the patch replaces `assert!(!verify_nonce_account(` with `assert!(`.

4. In `sdk/src/nonce_account.rs`, the patch replaces `assert!(!verify_nonce_account(&account, &Hash::default()));` with `assert!(verify_nonce_account(&account, &Hash::default()).is_none());`.

## Project Context

The changed code sits primarily in `sdk/src`, `send-transaction-service/src`, `runtime/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/bank.rs`, `runtime/src/accounts.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `runtime/src/accounts.rs`. The strongest project-level identifiers around this patch are `Hash::default`, `nonce_account`, `verify_nonce_account`, and `Hash`.

## Before/After Behavior

Before the patch, verify_nonce_account(acc, hash) returned a boolean indicating whether the account was system-owned, initialized, and matched the supplied blockhash. After the patch, it returns Some(Data) only for that successful case and None for failed cases. The send transaction service was updated from boolean negation to is_none() for durable nonce expiry handling, and tests were updated to expect None for invalid nonce account verification.

# Root Cause

The supported root cause is that nonce verification collapsed successful validation to a boolean, so nonce account state such as authority data was not carried across this verification boundary. The provided snippets do not directly prove that callers accepted unauthorized durable nonce transactions, but the commit message identifies missing nonce-authority signing as the rejected case.

## Walkthrough

1. A durable nonce transaction includes durable nonce information identifying a nonce account and nonce hash.

2. The send transaction service loads the nonce account and checks it against the durable nonce hash.

3. Before the patch, verify_nonce_account returned only true or false for owner/state/hash validation.

4. After the patch, verify_nonce_account returns the initialized nonce Data on a successful match.

5. Existing expiry logic now checks for None instead of negating a boolean.

6. This change is consistent with allowing later validation to inspect nonce account state, including authority information.

7. The supplied evidence does not include the downstream signer-authority check itself.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/src/nonce_account.rs | 25 | Nonce account verification now returns initialized nonce Data on hash match instead of only a boolean, enabling callers to inspect authority/state. |
| send-transaction-service/src/send_transaction_service.rs | 238 | Durable nonce transaction retention/expiry logic adapts to Option-returning nonce verification. |
| runtime/src/nonce_keyed_account.rs | 1107 | Runtime nonce verification tests updated for the new None/Some verification result shape. |
| sdk/src/nonce_account.rs | 60 | SDK nonce-account tests updated to assert failed verification as None. |

## Code Snippets

## Snippet 1

Context: `sdk/src/nonce_account.rs:25` (changes signature or replay validation logic)

Before
```rust
// TODO: Consider changing argument from Hash to DurableNonce.
pub fn verify_nonce_account(acc: &AccountSharedData, hash: &Hash) -> bool {
    if acc.owner() != &crate::system_program::id() {
        return false;
    }
    match StateMut::<Versions>::state(acc).map(|v| v.convert_to_current()) {
        Ok(State::Initialized(ref data)) => hash == &data.blockhash(),
```
After
```rust
// TODO: Consider changing argument from Hash to DurableNonce.
pub fn verify_nonce_account(acc: &AccountSharedData, hash: &Hash) -> Option<Data> {
    if acc.owner() != &crate::system_program::id() {
        return None;
    }
    match StateMut::<Versions>::state(acc).map(|v| v.convert_to_current()) {
        Ok(State::Initialized(data)) => (hash == &data.blockhash()).then(|| data),
```

## Snippet 2

Context: `send-transaction-service/src/send_transaction_service.rs:238` (changes a sensitive control or state-update path)

Before
```rust
if let Some((nonce_pubkey, durable_nonce)) = transaction_info.durable_nonce_info {
                let nonce_account = working_bank.get_account(&nonce_pubkey).unwrap_or_default();
                if !nonce_account::verify_nonce_account(&nonce_account, &durable_nonce)
                    && working_bank.get_signature_status_slot(signature).is_none()
                {
```
After
```rust
if let Some((nonce_pubkey, durable_nonce)) = transaction_info.durable_nonce_info {
                let nonce_account = working_bank.get_account(&nonce_pubkey).unwrap_or_default();
                if nonce_account::verify_nonce_account(&nonce_account, &durable_nonce).is_none()
                    && working_bank.get_signature_status_slot(signature).is_none()
                {
```

## Snippet 3

Context: `runtime/src/nonce_keyed_account.rs:1107` (changes signature or replay validation logic)

Before
```rust
fn verify_nonce_bad_acc_state_fail() {
        with_test_keyed_account(42, true, |nonce_account| {
            assert!(!verify_nonce_account(
                &nonce_account.account.borrow(),
                &Hash::default()
            ));
        });
    }
```
After
```rust
fn verify_nonce_bad_acc_state_fail() {
        with_test_keyed_account(42, true, |nonce_account| {
            assert!(
                verify_nonce_account(&nonce_account.account.borrow(), &Hash::default()).is_none()
            );
        });
    }
```

## Snippet 4

Context: `sdk/src/nonce_account.rs:60` (changes signature or replay validation logic)

Before
```rust
)
        .expect("nonce_account");
        assert!(!verify_nonce_account(&account, &Hash::default()));
    }
}
```
After
```rust
)
        .expect("nonce_account");
        assert!(verify_nonce_account(&account, &Hash::default()).is_none());
    }
}
```

# Fix Pattern

Return validated nonce account state instead of a lossy boolean so downstream code can enforce additional nonce-account invariants such as authority authorization.

## How It Was Fixed

sdk/src/nonce_account.rs changed verify_nonce_account from bool to Option<Data>. It returns None for non-system-owned accounts, bad state, or hash mismatch, and Some(data) for a valid initialized nonce account with a matching blockhash. send-transaction-service/src/send_transaction_service.rs and tests were updated for the Option-returning API. The commit message supplies the authority-rejection intent, but the provided snippets do not show the final rejection condition.

# Why It Matters

1. Durable nonce handling is replay-sensitive transaction validity logic.

2. Nonce blockhash matching alone is not the full authority invariant stated by the commit.

3. Returning nonce Data preserves state needed for stronger downstream validation.

4. Exploitability, fund loss, and consensus impact are not established by the provided snippets.

# Evidence Notes

Primary code evidence is sdk/src/nonce_account.rs line 25, send-transaction-service/src/send_transaction_service.rs line 238, runtime/src/nonce_keyed_account.rs line 1107, and sdk/src/nonce_account.rs line 60. The commit subject/body explicitly says durable nonce transactions not signed by authority are rejected. The shown diff demonstrates an API change from bool to Option<Data> and caller/test adaptation. It does not show the authority signer comparison, the rejection branch, or an execution bypass. Protocol security invariant: A durable nonce transaction should only be treated as valid when it references a system-owned initialized nonce account whose stored blockhash matches the transaction nonce and when the transaction is authorized by the nonce account authority. The supplied code shows preservation of nonce account Data after nonce/hash verification, but does not show the final signer-authority comparison. Verification notes: The provided snippets do not show the exact authority signer comparison or rejection branch. The patch evidence does not prove transaction execution bypass, only a likely missing nonce-authority validation path. No exploitability, fund loss, or consensus impact is directly demonstrated by the supplied code. Some shown changes are API-shape and test updates; the security classification relies partly on the commit message and subsystem context. Confirmed by provided snippets: nonce verification now returns Option<Data>. Confirmed by provided snippets: failed verification cases are represented as None. Confirmed by provided snippets: send transaction service expiry logic was adapted to is_none(). Not shown: exact transaction signer check against nonce account authority. Not shown: concrete exploit path or impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `nonce-authority-validation`
Final impact type: `unauthorized-transaction-acceptance, replay-risk`
Final confidence: `medium`
Final tags: `blockchain-core, durable-nonce, authorization, signature-validation, replay-sensitive`

The commit metadata explicitly states that durable nonce transactions not signed by the nonce authority are rejected, and the shown patch changes nonce-account verification from a lossy boolean to returning initialized nonce account Data, which is consistent with enabling authority-aware validation in a replay-sensitive transaction path. However, the supplied snippets do not show the actual signer-versus-authority check or the rejection branch, so the evidence is not strong enough to validate this as a fully demonstrated security fix. It is best retained conservatively as security hardening.

## Security Evidence

1. Commit subject states durable nonce transactions not signed by authority are rejected.
2. Nonce verification now returns Option<Data> instead of bool, preserving initialized nonce account state after blockhash verification.
3. The changed path handles durable nonce transaction validity and expiry logic, which is replay-sensitive blockchain transaction processing.
4. Caller logic was updated to treat failed nonce verification as None.

## Missing Evidence

1. No supplied snippet shows comparing transaction signers against the nonce account authority.
2. No supplied snippet shows the final runtime rejection branch for unauthorized durable nonce transactions.
3. No concrete exploit path, fund loss, or consensus impact is demonstrated by the provided patch excerpts.
4. Several changed files named in the commit metadata are not represented with relevant authority-check diff evidence.

## Claim Boundaries

1. Do not claim the provided snippets alone prove unauthorized transactions were accepted before the patch.
2. Do not claim exploitability or concrete replay impact beyond replay-sensitive risk.
3. The validated finding should focus on durable nonce authority validation hardening, not broad cryptography changes.
4. Classification relies partly on the explicit commit message plus an API change that carries nonce account Data for downstream checks.
