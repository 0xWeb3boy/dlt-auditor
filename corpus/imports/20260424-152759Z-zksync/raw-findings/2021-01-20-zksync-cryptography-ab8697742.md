---
case_id: case_20210120_ab8697742
project: zksync
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2021-01-20
source_refs:
  - git:ab8697742a14a35cf0cb6cb900a8cc12018a35e1
  - "core/bin/zksync_api/src/api_server/tx_sender.rs:650"
  - "core/bin/zksync_api/src/api_server/tx_sender.rs:603"
  - "core/lib/types/src/tx/zksync_tx.rs:117"
  - "core/lib/storage/src/chain/account/mod.rs:23"
bug_class: transaction-authentication-hardening
impact_type:
  - authentication-integrity
confidence: medium
tags:
  - zksync
  - transaction-validation
  - signature-validation
  - create2
  - authentication-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes zkSync transaction sender signature verification so CREATE2 accounts reject supplied Ethereum signature data in both single and batch paths, and changes ZkSyncTx::account_id() to return an error for disabled Close transactions instead of panicking. These are plausibly security-relevant hardening changes, but the provided evidence does not prove an authorization bypass, denial of service, or other concrete vulnerability. Treat this as unclear rather than a confirmed security fix.

## Observed Patch Facts

1. In `core/bin/zksync_api/src/api_server/tx_sender.rs`, the patch replaces `for (tx, message) in batch.into_iter().zip(msgs_to_sign.into_iter()) {` with `for (tx, message, sender_type) in izip!(batch, msgs_to_sign, sender_types) {`.

2. In `core/bin/zksync_api/src/api_server/tx_sender.rs`, the patch replaces `Some(message_to_sign) => {` with `Some(message) => match account_type {`.

3. In `core/lib/types/src/tx/zksync_tx.rs`, the patch replaces `pub fn account_id(&self) -> AccountId {` with `pub fn account_id(&self) -> anyhow::Result<AccountId> {`.

4. In `core/lib/storage/src/chain/account/mod.rs`, the patch replaces `/// Obtains both committed and verified state for the account by its ID.` with `/// Stores account type in the databse`.

## Project Context

The changed code sits primarily in `core/bin/zksync_api/src/api_server`, `core/bin/zksync_api/src`, `core/lib/types/src/tx`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/lib/types/src/tx/withdraw.rs`, `core/lib/types/src/tx/transfer.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/lib/types/src/operations/mod.rs`, `core/lib/types/src/tx/primitives/tests.rs`. The strongest project-level identifiers around this patch are `account_id`, `ZkSyncTx`, `ZkSyncTx::Transfer`, and `ZkSyncTx::Withdraw`. Nearby tests or test-like files include `core/lib/types/src/tests/hardcoded.rs`, `core/lib/types/src/tests/mod.rs`.

## Before/After Behavior

Before the patch, the batch verification path iterated over transactions and messages without also applying a per-sender EthAccountType check before constructing EthSignData. After the patch, it zips in sender_types and rejects Ethereum signature data for CREATE2 senders. Before the patch, the single-transaction path appears to derive account type through storage using tx.account_id(); after the patch, account_type is passed in and matched directly. Before the patch, ZkSyncTx::account_id() panicked for Close; after the patch, it returns anyhow::Result and reports Close as an error.

# Root Cause

The evidence suggests the old code did not consistently enforce the intended CREATE2 authentication-mode rule at the exact point Ethereum signature data was accepted into verification. Separately, a disabled Close transaction variant was represented with a panic in a shared account_id helper. The evidence does not establish that either behavior was exploitable in production.

## Walkthrough

1. Transaction signature verification receives a zkSync transaction plus optional Ethereum signature material.

2. The patched single-transaction verifier receives EthAccountType and checks it before constructing EthSignData.

3. For EthAccountType::CREATE2, the patched code rejects a present Ethereum signature with SubmitError::IncorrectTx.

4. The patched batch verifier carries sender_types alongside batch transactions and messages, applying the same CREATE2 check per sender.

5. The storage change adds set_account_type support, but the evidence only shows it as supporting account classification, not as a root cause.

6. ZkSyncTx::account_id() now returns a Result and treats Close as a recoverable error rather than panicking.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/bin/zksync_api/src/api_server/tx_sender.rs | 596 | verifies per-transaction Ethereum signature data against the already-known EthAccountType and rejects signatures for CREATE2 accounts |
| core/bin/zksync_api/src/api_server/tx_sender.rs | 643 | verifies batch transaction signature data and applies the same CREATE2 no-Ethereum-signature rule per sender |
| core/lib/types/src/tx/zksync_tx.rs | 117 | returns account_id as a fallible result so disabled Close transactions do not panic through this helper |
| core/lib/storage/src/chain/account/mod.rs | 23 | stores account EthAccountType used by transaction authentication logic |

## Code Snippets

## Snippet 1

Context: `core/bin/zksync_api/src/api_server/tx_sender.rs:650` (changes signature or replay validation logic)

Before
```rust
) -> Result<VerifiedTx, SubmitError> {
    let mut txs = Vec::with_capacity(batch.len());
    for (tx, message) in batch.into_iter().zip(msgs_to_sign.into_iter()) {
        // If we have more signatures provided than required,
        // we will verify those too.
        let eth_sign_data = if let (Some(signature), Some(message)) = (tx.signature, message) {
            Some(EthSignData { signature, message })
        } else {
```
After
```rust
) -> Result<VerifiedTx, SubmitError> {
    let mut txs = Vec::with_capacity(batch.len());
    for (tx, message, sender_type) in izip!(batch, msgs_to_sign, sender_types) {
        // If we have more signatures provided than required,
        // we will verify those too.
        let eth_sign_data = if let (Some(signature), Some(message)) = (tx.signature, message) {
            if let EthAccountType::CREATE2 = sender_type {
                return Err(SubmitError::IncorrectTx(
```

## Snippet 2

Context: `core/bin/zksync_api/src/api_server/tx_sender.rs:603` (changes the branch that decides whether execution stops or continues)

Before
```rust
) -> Result<VerifiedTx, SubmitError> {
    let eth_sign_data = match msg_to_sign {
        Some(message_to_sign) => {
            // Check if account is a CREATE2 account
            // These accounts do not have to pass 2FA
            let id = tx.account_id();
            let connection_pool = zksync_storage::ConnectionPool::new(None);
            let mut storage = connection_pool
```
After
```rust
) -> Result<VerifiedTx, SubmitError> {
    let eth_sign_data = match msg_to_sign {
        Some(message) => match account_type {
            // Check if account is a CREATE2 account
            // These accounts do not have to pass 2FA
            EthAccountType::CREATE2 => {
                if signature.is_some() {
                    return Err(SubmitError::IncorrectTx(
```

## Snippet 3

Context: `core/lib/types/src/tx/zksync_tx.rs:117` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    pub fn account_id(&self) -> AccountId {
        match self {
            ZkSyncTx::Transfer(tx) => tx.account_id,
            ZkSyncTx::Withdraw(tx) => tx.account_id,
            ZkSyncTx::Close(_) => panic!("Close operation is disabled"),
            ZkSyncTx::ChangePubKey(tx) => tx.account_id,
```
After
```rust
}

    pub fn account_id(&self) -> anyhow::Result<AccountId> {
        match self {
            ZkSyncTx::Transfer(tx) => Ok(tx.account_id),
            ZkSyncTx::Withdraw(tx) => Ok(tx.account_id),
            ZkSyncTx::ChangePubKey(tx) => Ok(tx.account_id),
            ZkSyncTx::ForcedExit(tx) => Ok(tx.initiator_account_id),
```

## Snippet 4

Context: `core/lib/storage/src/chain/account/mod.rs:23` (changes persisted or aggregate state handling)

Before
```rust
impl<'a, 'c> AccountSchema<'a, 'c> {
    /// Obtains both committed and verified state for the account by its ID.
    pub async fn account_state_by_id(
        &mut self,
        account_id: AccountId,
    ) -> QueryResult<StoredAccountState> {
        let start = Instant::now();
```
After
```rust
impl<'a, 'c> AccountSchema<'a, 'c> {
    /// Stores account type in the databse
    /// There are 2 types: Owned and CREATE2
    pub async fn set_account_type(
        &mut self,
        account_id: AccountId,
        account_type: EthAccountType,
```

# Fix Pattern

Thread account classification into transaction authentication checks, reject authentication material that is invalid for that account type, and replace a panic for a disabled transaction variant with fallible error handling.

## How It Was Fixed

The tx sender functions now take or consume EthAccountType values and reject Ethereum signature data for CREATE2 accounts. The batch path uses izip! to align transactions, messages, and sender types. ZkSyncTx::account_id() was changed from returning AccountId directly to returning anyhow::Result<AccountId>, with Close mapped to an error.

# Why It Matters

1. Keeps observed transaction admission logic aligned with account type.

2. Applies the CREATE2 signature rule consistently to single and batch verification paths.

3. Reduces panic-based handling for a disabled transaction variant.

4. Does not prove a concrete exploit from the supplied evidence.

# Evidence Notes

Grounded evidence comes from tx_sender.rs changes in verify_tx_info_message_signature and verify_txs_batch_signature, zksync_tx.rs changing account_id() to a Result, and account/mod.rs adding set_account_type. The evidence does not prove that accepting Ethereum signature data for CREATE2 bypassed authorization, does not prove unauthenticated reachability of the Close panic, and does not show cryptographic primitive correctness issues. The commit subject is review-comment cleanup, which further weakens a vulnerability-fix classification. Protocol security invariant: Potentially, transaction admission should handle Ethereum signature data according to the sender's EthAccountType, and disabled transaction variants should fail with ordinary errors rather than panics. The provided evidence supports this as an intended validation rule, but does not establish a concrete vulnerability or exploit path. Verification notes: No concrete exploit path is shown by the patch evidence. No proof that accepting an Ethereum signature for CREATE2 directly bypassed authorization. No proof that the Close account_id panic was reachable from unauthenticated remote input in production. The commit subject is review-cleanup oriented, so some changes may be defensive cleanup rather than a vulnerability fix. No impact on cryptographic primitive correctness is shown. No concrete exploit path is provided. No tests or issue discussion are provided in the input. No evidence proves remote unauthenticated denial of service from the Close panic. No evidence proves an authorization bypass from the prior CREATE2 signature handling. Classified as unclear and excluded from the security corpus under the strict evidence rules. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-authentication-hardening`
Final impact type: `authentication-integrity`
Final confidence: `medium`
Final tags: `zksync, transaction-validation, signature-validation, create2, authentication-hardening`

The patch does not prove a concrete exploitable vulnerability, but it clearly tightens security-sensitive transaction admission behavior by rejecting Ethereum signature data for CREATE2 accounts in both single and batch verification paths. The panic-to-error change for disabled Close transactions is reliability-oriented on its own, but the CREATE2 signature handling is enough to retain this as security hardening rather than a confirmed security fix.

## Security Evidence

1. Single-transaction verification now receives account_type and rejects signatures when account_type is EthAccountType::CREATE2.
2. Batch verification now threads sender_types alongside transactions and messages, applying the same CREATE2 signature rejection per transaction.
3. The changed code is in transaction sender signature verification, a security-sensitive authentication/admission path.
4. The added error explicitly states that an Ethereum signature from a CREATE2 account is not expected.

## Missing Evidence

1. No issue, advisory, test, or commit message establishes a concrete vulnerability.
2. No evidence shows accepting an Ethereum signature for CREATE2 accounts bypassed authorization or changed transaction ownership.
3. No evidence proves the Close transaction panic was remotely reachable or exploitable as denial of service.
4. No before/after behavioral proof shows funds, replay protection, or signature validity could be compromised.

## Claim Boundaries

1. Classify as hardening, not a confirmed security fix.
2. Do not claim an authorization bypass or cryptographic primitive flaw from this evidence alone.
3. Do not treat the account_id panic change as independently security-proven.
4. The supported claim is limited to stricter validation of unexpected Ethereum signature material for CREATE2 accounts.
