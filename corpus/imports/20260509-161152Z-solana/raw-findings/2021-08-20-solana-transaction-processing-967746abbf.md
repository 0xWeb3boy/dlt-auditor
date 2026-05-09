---
case_id: case_20210820_967746abbf
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2021-08-20
source_refs:
  - git:967746abbf1cb6fb1355323eb812373d0a1fc558
  - "rpc/src/rpc_subscriptions.rs:1447"
  - "account-decoder/src/lib.rs:62"
  - "rpc/src/rpc_subscriptions.rs:1430"
  - "rpc/src/rpc_pubsub.rs:836"
bug_class: unbounded-serialization
impact_type:
  - resource-exhaustion
confidence: medium
tags:
  - rpc
  - account-encoding
  - base58
  - serialization-bound
  - resource-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a size guard around base58 account-data encoding in Solana's account decoder and aligns RPC handling with the same `MAX_BASE58_BYTES` limit. Oversized account data now returns an explicit error string instead of being base58-encoded. The evidence supports serialization resource bounding, but does not prove a vulnerability, exploit path, crash, privilege bypass, consensus impact, or confirmed denial of service.

## Observed Patch Facts

1. In `rpc/src/rpc_subscriptions.rs`, the patch replaces `bank_forks` with `let expected1 = make_account_result(0, 1, "");`.

2. In `account-decoder/src/lib.rs`, the patch replaces `pub fn encode<T: ReadableAccount>(` with `fn encode_bs58<T: ReadableAccount>(`.

3. In `rpc/src/rpc_subscriptions.rs`, the patch replaces `subscriptions.add_account_subscription(` with `let tx0 = system_transaction::create_account(`.

4. In `rpc/src/rpc_pubsub.rs`, the patch replaces `encoding: None,` with `encoding: Some(encoding),`.

## Project Context

The changed code sits primarily in `rpc/src`, `account-decoder/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rpc/src/rpc.rs`, `rpc/src/parsed_token_accounts.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rpc/src/rpc.rs`, `rpc/src/parsed_token_accounts.rs`. The strongest project-level identifiers around this patch are `CommitmentConfig::processed`, `Some`, `encoding`, and `None`.

## Before/After Behavior

Before the patch, the shown evidence does not include a base58-specific size guard before `bs58::encode` in the account encoding path. After the patch, `encode_bs58` checks `account.data().len() <= MAX_BASE58_BYTES`; data within the limit is encoded, while larger data returns `error: data too large for bs58 encoding`. RPC code is updated to use the shared maximum and tests are adjusted around explicit account encoding behavior.

# Root Cause

Account data could reach base58 serialization without the size bound introduced by this patch. The provided evidence supports an unbounded or insufficiently bounded serialization path, but not a demonstrated security failure.

## Walkthrough

1. RPC account responses or subscription notifications serialize account data through `UiAccount` and `UiAccountEncoding`.

2. The patch adds a dedicated `encode_bs58` helper in `account-decoder/src/lib.rs`.

3. The helper checks the full account data length against `MAX_BASE58_BYTES` before calling `bs58::encode`.

4. If the data is within the limit, the sliced account data is base58-encoded.

5. If the data exceeds the limit, the helper returns an explicit error string.

6. RPC imports the same `MAX_BASE58_BYTES` constant so RPC-side handling uses the shared bound.

7. Subscription and pubsub test changes exercise explicit encoding configuration and expected notification behavior; they are supporting test changes, not root cause evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| account-decoder/src/lib.rs | 62 | adds encode_bs58 helper that refuses base58 encoding when account data length exceeds MAX_BASE58_BYTES |
| rpc/src/rpc.rs | 11 | imports shared MAX_BASE58_BYTES into RPC account handling so the RPC layer uses the same base58 size limit |
| rpc/src/rpc_pubsub.rs | 836 | updates account subscription tests/configuration around explicit account encoding behavior |
| rpc/src/rpc_subscriptions.rs | 1409 | updates account subscription notification tests for expected encoded account results under the new encoding limit |

## Code Snippets

## Snippet 1

Context: `rpc/src/rpc_subscriptions.rs:1447` (changes an authorization or privilege gate)

Before
```rust
Transaction::new(&[&alice, &mint_keypair], message, blockhash)
        };

        bank_forks
            .write()
            .unwrap()
            .get(1)
            .unwrap()
```
After
```rust
Transaction::new(&[&alice, &mint_keypair], message, blockhash)
        };
        let expected1 = make_account_result(0, 1, "");

        let tx2 = system_transaction::create_account(
            &mint_keypair,
            &alice,
            blockhash,
```

## Snippet 2

Context: `account-decoder/src/lib.rs:62` (changes persisted or aggregate state handling)

Before
```rust
impl UiAccount {
    pub fn encode<T: ReadableAccount>(
        pubkey: &Pubkey,
```
After
```rust
impl UiAccount {
    fn encode_bs58<T: ReadableAccount>(
        account: &T,
        data_slice_config: Option<UiDataSliceConfig>,
    ) -> String {
        if account.data().len() <= MAX_BASE58_BYTES {
            bs58::encode(slice_data(account.data(), data_slice_config)).into_string()
```

## Snippet 3

Context: `rpc/src/rpc_subscriptions.rs:1430` (changes the branch that decides whether execution stops or continues)

Before
```rust
OptimisticallyConfirmedBank::locked_from_bank_forks_root(&bank_forks),
        );
        subscriptions.add_account_subscription(
            alice.pubkey(),
            Some(RpcAccountInfoConfig {
                commitment: Some(CommitmentConfig::processed()),
                encoding: None,
                data_slice: None,
```
After
```rust
OptimisticallyConfirmedBank::locked_from_bank_forks_root(&bank_forks),
        );

        let tx0 = system_transaction::create_account(
            &mint_keypair,
            &alice,
```

## Snippet 4

Context: `rpc/src/rpc_pubsub.rs:836` (changes a sensitive control or state-update path)

Before
```rust
Some(RpcAccountInfoConfig {
                commitment: Some(CommitmentConfig::processed()),
                encoding: None,
                data_slice: None,
            }),
```
After
```rust
Some(RpcAccountInfoConfig {
                commitment: Some(CommitmentConfig::processed()),
                encoding: Some(encoding),
                data_slice: None,
            }),
```

# Fix Pattern

Add a centralized size check before resource-sensitive serialization and reuse the same limit across decoder and RPC paths.

## How It Was Fixed

The fix introduced `encode_bs58`, guarded base58 encoding with `MAX_BASE58_BYTES`, returned an ordinary error string for oversized data, and updated RPC/tests to use or exercise the shared limit.

# Why It Matters

1. Bounds base58 encoding work for RPC account data.

2. Makes oversized base58 account responses fail explicitly.

3. Keeps account-decoder and RPC size limits consistent.

4. Does not establish a confirmed security vulnerability from the provided evidence.

# Evidence Notes

Strongest evidence is `account-decoder/src/lib.rs`, where `encode_bs58` checks `account.data().len() <= MAX_BASE58_BYTES` before `bs58::encode`. Related evidence shows RPC importing `MAX_BASE58_BYTES` and tests/configuration updates in pubsub/subscriptions. Claims about transaction processing, access control, privilege checks, consensus behavior, memory safety, crashability, or proven remote denial of service are unsupported by the provided evidence. Protocol security invariant: RPC account serialization should avoid base58-encoding account data above the configured maximum size; the provided evidence shows this bound being added, but does not establish a concrete security impact. Verification notes: Exploitability as a remote denial of service is not proven by the provided patch evidence. No access control or privilege check is shown to be fixed. No transaction validation, consensus, or block processing invariant is shown to be changed. The patch does not show memory corruption or secret exposure. The error behavior for all RPC methods using base58 is inferred from the shown helper and imports, not fully enumerated in the evidence. No exploit path is shown. No panic or crash behavior is shown. No access-control or privilege logic is changed in the evidence. No consensus or transaction-validation invariant is changed in the evidence. Security relevance is plausible as resource hardening, but the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unbounded-serialization`
Final impact type: `resource-exhaustion`
Final confidence: `medium`
Final tags: `rpc, account-encoding, base58, serialization-bound, resource-hardening`

The supplied evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The patch adds a hard size limit before base58 encoding account data in RPC/account-decoder paths and returns an explicit error for oversized data. That is a security-relevant resource bound on exposed serialization behavior, but the evidence does not prove an exploit, crash, consensus impact, or actual denial of service.

## Security Evidence

1. Adds `MAX_BASE58_BYTES` check before `bs58::encode` in `account-decoder/src/lib.rs`.
2. Oversized account data now returns `error: data too large for bs58 encoding` instead of being encoded.
3. RPC imports and uses the shared base58 size limit, aligning exposed account encoding behavior.
4. Tests were updated around explicit account encoding behavior in RPC pubsub/subscriptions.

## Missing Evidence

1. No demonstrated exploit path or attacker-controlled request sequence is shown.
2. No crash, panic, memory exhaustion, or CPU exhaustion measurement is provided.
3. No advisory, CVE, security note, or incident context is supplied.
4. No consensus, transaction validation, privilege, or access-control fix is evidenced.

## Claim Boundaries

1. Validate only as resource-oriented security hardening.
2. Do not claim a confirmed denial-of-service vulnerability.
3. Do not classify as access control, privilege bypass, transaction-processing, or consensus security.
4. The supported affected area is RPC/account data serialization, not core transaction execution.
