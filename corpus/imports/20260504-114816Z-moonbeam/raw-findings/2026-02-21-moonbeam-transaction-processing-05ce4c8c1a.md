---
case_id: case_20260221_05ce4c8c1a
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2026-02-21
source_refs:
  - git:05ce4c8c1aacfb430fbecf86435cf4ba78a045a7
  - "node/service/src/rpc.rs:298"
  - "runtime/moonriver/src/lib.rs:695"
  - "runtime/moonbeam/src/lib.rs:692"
  - "runtime/moonbase/src/lib.rs:694"
bug_class: replay-protection-policy-hardening
impact_type:
  - replay-protection-hardening
confidence: high
tags:
  - blockchain-core
  - transaction-processing
  - transaction-admission
  - rpc
  - replay-protection
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Moonbeam, Moonriver, and Moonbase Ethereum transaction admission by changing `AllowUnprotectedTxs` from `true` to `false` and changing a related RPC setup boolean from `true` to `false`. The commit message directly says to forbid unprotected transactions and that tests must not use legacy transactions without chain id. The evidence supports security hardening against acceptance of replay-unprotected legacy Ethereum transactions, but it does not establish a concrete exploit or observed vulnerability.

## Observed Patch Facts

1. In `node/service/src/rpc.rs`, the patch replaces `true,` with `false,`.

2. In `runtime/moonriver/src/lib.rs`, the patch replaces `pub const AllowUnprotectedTxs: bool = true;` with `pub const AllowUnprotectedTxs: bool = false;`.

3. In `runtime/moonbeam/src/lib.rs`, the patch replaces `pub const AllowUnprotectedTxs: bool = true;` with `pub const AllowUnprotectedTxs: bool = false;`.

4. In `runtime/moonbase/src/lib.rs`, the patch replaces `pub const AllowUnprotectedTxs: bool = true;` with `pub const AllowUnprotectedTxs: bool = false;`.

## Project Context

The changed code sits primarily in `node/service/src`, `node/service`, `runtime/moonriver/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/moonriver/src/xcm_config.rs`, `runtime/moonriver/src/precompiles.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/moonriver/src/xcm_config.rs`, `runtime/moonriver/src/precompiles.rs`. The strongest project-level identifiers around this patch are `PostLogContent::BlockAndTxnHashes`, `const`, `PostLogContent`, and `AllowUnprotectedTxs`. Nearby tests or test-like files include `runtime/moonriver/tests/xcm_mock/parachain.rs`, `runtime/moonbeam/tests/xcm_mock/parachain.rs`.

## Before/After Behavior

Before the patch, the runtimes configured `AllowUnprotectedTxs: bool = true`, allowing unprotected Ethereum transactions in the `pallet_ethereum` configuration. After the patch, Moonriver, Moonbeam, and Moonbase set this parameter to `false`. The RPC setup in `node/service/src/rpc.rs` also changes a boolean argument from `true` to `false`; its exact parameter name is not shown, but the surrounding commit context indicates it is related to disabling unprotected transaction acceptance.

# Root Cause

The prior configuration was permissive: runtime Ethereum transaction configuration allowed unprotected legacy transactions. This left replay-protection policy disabled at configuration/admission time. The evidence does not support stronger claims about deeper logic executing before validation, fund loss, privilege escalation, or consensus failure.

## Walkthrough

1. A legacy Ethereum transaction without chain id could be submitted to the Ethereum transaction path under the prior permissive configuration.

2. Moonriver, Moonbeam, and Moonbase each had `AllowUnprotectedTxs` set to `true`.

3. The patch changes that runtime parameter to `false` in all three runtimes.

4. The patch also changes a related boolean in Ethereum RPC setup from `true` to `false`.

5. Tests were updated so they no longer use legacy transactions without chain id.

6. The resulting policy is to reject or avoid accepting unprotected Ethereum transactions, based on the changed configuration and commit message.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| node/service/src/rpc.rs | 298 | RPC transaction handling configuration now disables acceptance of unprotected transactions before they enter the Ethereum transaction path. |
| runtime/moonriver/src/lib.rs | 695 | Moonriver runtime `pallet_ethereum` configuration now sets `AllowUnprotectedTxs` to false. |
| runtime/moonbeam/src/lib.rs | 692 | Moonbeam runtime `pallet_ethereum` configuration now sets `AllowUnprotectedTxs` to false. |
| runtime/moonbase/src/lib.rs | 694 | Moonbase runtime `pallet_ethereum` configuration now sets `AllowUnprotectedTxs` to false. |

## Code Snippets

## Snippet 1

Context: `node/service/src/rpc.rs:298` (changes a sensitive control or state-update path)

Before
```rust
fee_history_limit,
			10,
			true,
			forced_parent_hashes,
			pending_create_inherent_data_providers,
```
After
```rust
fee_history_limit,
			10,
			false,
			forced_parent_hashes,
			pending_create_inherent_data_providers,
```

## Snippet 2

Context: `runtime/moonriver/src/lib.rs:695` (changes a sensitive control or state-update path)

Before
```rust
parameter_types! {
	pub const PostBlockAndTxnHashes: PostLogContent = PostLogContent::BlockAndTxnHashes;
	pub const AllowUnprotectedTxs: bool = true;
}
```
After
```rust
parameter_types! {
	pub const PostBlockAndTxnHashes: PostLogContent = PostLogContent::BlockAndTxnHashes;
	pub const AllowUnprotectedTxs: bool = false;
}
```

## Snippet 3

Context: `runtime/moonbeam/src/lib.rs:692` (changes a sensitive control or state-update path)

Before
```rust
parameter_types! {
	pub const PostBlockAndTxnHashes: PostLogContent = PostLogContent::BlockAndTxnHashes;
	pub const AllowUnprotectedTxs: bool = true;
}
```
After
```rust
parameter_types! {
	pub const PostBlockAndTxnHashes: PostLogContent = PostLogContent::BlockAndTxnHashes;
	pub const AllowUnprotectedTxs: bool = false;
}
```

## Snippet 4

Context: `runtime/moonbase/src/lib.rs:694` (changes a sensitive control or state-update path)

Before
```rust
parameter_types! {
	pub const PostBlockAndTxnHashes: PostLogContent = PostLogContent::BlockAndTxnHashes;
	pub const AllowUnprotectedTxs: bool = true;
}
```
After
```rust
parameter_types! {
	pub const PostBlockAndTxnHashes: PostLogContent = PostLogContent::BlockAndTxnHashes;
	pub const AllowUnprotectedTxs: bool = false;
}
```

# Fix Pattern

Configuration hardening: disable permissive acceptance of unprotected legacy Ethereum transactions at runtime and RPC admission boundaries.

## How It Was Fixed

The patch sets `AllowUnprotectedTxs` to `false` in `runtime/moonriver/src/lib.rs`, `runtime/moonbeam/src/lib.rs`, and `runtime/moonbase/src/lib.rs`, and changes a related RPC configuration boolean in `node/service/src/rpc.rs` from `true` to `false`. Tests were adjusted to stop relying on legacy transactions without chain id.

# Why It Matters

1. Touches Ethereum transaction admission policy.

2. Disallows legacy transactions without chain id according to the commit message.

3. Improves replay-protection posture.

4. No concrete replay exploit or asset impact is proven by the supplied evidence.

# Evidence Notes

Strongest evidence is the direct `AllowUnprotectedTxs: bool = true` to `false` change in three runtime files and the commit text `forbid unprotected txs` / `Tests must not use legacy txs without chain id`. The RPC boolean change is consistent with the same policy but its exact meaning is inferred because the parameter name is not provided. Claims about practical exploitability, cross-chain replay execution, loss of funds, privilege escalation, or consensus failure are unsupported by the provided input. Protocol security invariant: Ethereum transactions accepted by the node/runtime should be replay-protected; legacy Ethereum transactions without a chain id should not be accepted unless the system intentionally permits unprotected transactions. Verification notes: The patch does not prove that unprotected transactions were exploitable in practice on these networks. The patch does not show a concrete cross-chain replay example. The patch does not show loss of funds, privilege escalation, or consensus failure. The exact semantics of the boolean argument in `node/service/src/rpc.rs` are inferred from the commit context and surrounding `AllowUnprotectedTxs` changes. Confirmed by provided diff snippets only; no external code inspection was used. Runtime configuration change is directly evidenced. RPC flag semantics are inferred from commit context and adjacent changes. Classified as security hardening rather than confirmed exploited vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `replay-protection-policy-hardening`
Final impact type: `replay-protection-hardening`
Final confidence: `high`
Final tags: `blockchain-core, transaction-processing, transaction-admission, rpc, replay-protection, security-hardening`

The supplied patch evidence directly shows Moonbeam, Moonriver, and Moonbase changing `AllowUnprotectedTxs` from `true` to `false`, and the commit message explicitly says to forbid unprotected transactions and stop tests from using legacy transactions without chain id. That is enough to retain this as security hardening of Ethereum transaction admission and replay-protection policy, but not enough to classify it as a concrete exploitable security fix.

## Security Evidence

1. Commit subject and body explicitly state unprotected transactions are being forbidden.
2. Runtime configuration changes `AllowUnprotectedTxs` from `true` to `false` in three runtimes.
3. Tests were updated because legacy transactions without chain id should no longer be used.
4. RPC setup also flips a related boolean from `true` to `false`, consistent with transaction admission hardening.

## Missing Evidence

1. No concrete exploit scenario is shown in the supplied patch evidence.
2. No proof of asset loss, privilege escalation, consensus failure, or observed attack is provided.
3. The exact RPC boolean parameter name and semantics are not shown, only inferred from nearby evidence.

## Claim Boundaries

1. Validate as security hardening, not a confirmed vulnerability fix.
2. Supported claim is rejection or disabling of replay-unprotected legacy Ethereum transactions.
3. Do not claim practical exploitability or cross-chain replay execution from this evidence alone.
4. Do not rely on unrelated XCM or precompile context to broaden the finding.
