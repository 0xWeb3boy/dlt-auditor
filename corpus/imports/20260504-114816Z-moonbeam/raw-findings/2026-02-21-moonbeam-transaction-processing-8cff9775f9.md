---
case_id: case_20260221_8cff9775f9
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
  - git:8cff9775f957feee431078ad3f21945ed5239024
  - "node/service/src/rpc.rs:298"
  - "runtime/moonriver/src/lib.rs:695"
  - "runtime/moonbeam/src/lib.rs:692"
  - "runtime/moonbase/src/lib.rs:694"
bug_class: unprotected-transaction-admission
impact_type:
  - replay-risk-reduction
confidence: high
tags:
  - blockchain-core
  - transaction-processing
  - transaction-admission
  - ethereum
  - replay-protection
  - runtime-config
  - rpc
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely hardens Moonbeam Ethereum transaction admission by disabling acceptance of unprotected legacy transactions. The strongest evidence is the repeated `AllowUnprotectedTxs: bool = true` to `false` change in Moonriver, Moonbeam, and Moonbase runtime configuration, supported by the commit message stating that unprotected transactions are forbidden and tests must not use legacy transactions without chain id. The evidence does not prove an exploit, fund loss, or a concrete replay scenario.

## Observed Patch Facts

1. In `node/service/src/rpc.rs`, the patch replaces `true,` with `false,`.

2. In `runtime/moonriver/src/lib.rs`, the patch replaces `pub const AllowUnprotectedTxs: bool = true;` with `pub const AllowUnprotectedTxs: bool = false;`.

3. In `runtime/moonbeam/src/lib.rs`, the patch replaces `pub const AllowUnprotectedTxs: bool = true;` with `pub const AllowUnprotectedTxs: bool = false;`.

4. In `runtime/moonbase/src/lib.rs`, the patch replaces `pub const AllowUnprotectedTxs: bool = true;` with `pub const AllowUnprotectedTxs: bool = false;`.

## Project Context

The changed code sits primarily in `node/service/src`, `node/service`, `runtime/moonriver/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/moonriver/src/xcm_config.rs`, `runtime/moonriver/src/precompiles.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/moonriver/src/xcm_config.rs`, `runtime/moonriver/src/precompiles.rs`. The strongest project-level identifiers around this patch are `PostLogContent::BlockAndTxnHashes`, `const`, `PostLogContent`, and `AllowUnprotectedTxs`. Nearby tests or test-like files include `runtime/moonriver/tests/xcm_mock/parachain.rs`, `runtime/moonbeam/tests/xcm_mock/parachain.rs`.

## Before/After Behavior

Before the patch, Moonriver, Moonbeam, and Moonbase each configured `AllowUnprotectedTxs` as `true` in their `pallet_ethereum` runtime configuration. After the patch, each sets it to `false`. The RPC construction path in `node/service/src/rpc.rs` also changes a boolean argument from `true` to `false`; based on the commit context, this appears related to the same unprotected-transaction policy, but the full constructor signature is not provided.

# Root Cause

The root cause supported by the evidence is an overly permissive configuration that explicitly allowed unprotected legacy Ethereum transactions. The provided diff does not show the full validation implementation or prove a specific exploit path, so claims should stay at the configuration and replay-protection policy level.

## Walkthrough

1. The Ethereum runtime configuration for Moonriver, Moonbeam, and Moonbase included `AllowUnprotectedTxs: bool = true`.

2. That setting directly indicates that unprotected transactions were permitted by the runtime configuration.

3. The commit changes the setting to `false` in all three runtimes.

4. The node RPC setup also changes a related boolean from `true` to `false`, aligning the RPC-side configuration with the runtime policy, though the exact argument name is not shown in the provided evidence.

5. Tests were updated so legacy transactions without chain id are no longer used, matching the commit message and the configuration change.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| node/service/src/rpc.rs | 298 | RPC transaction-admission/configuration path now passes false for allowing unprotected transactions |
| runtime/moonriver/src/lib.rs | 695 | Moonriver pallet_ethereum runtime configuration disables unprotected transactions |
| runtime/moonbeam/src/lib.rs | 692 | Moonbeam pallet_ethereum runtime configuration disables unprotected transactions |
| runtime/moonbase/src/lib.rs | 694 | Moonbase pallet_ethereum runtime configuration disables unprotected transactions |

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

Disable permissive transaction-admission configuration for unprotected legacy Ethereum transactions across RPC and runtime configuration boundaries.

## How It Was Fixed

The patch changes `AllowUnprotectedTxs` from `true` to `false` in `runtime/moonriver/src/lib.rs`, `runtime/moonbeam/src/lib.rs`, and `runtime/moonbase/src/lib.rs`. It also changes a boolean in `node/service/src/rpc.rs` from `true` to `false`, apparently for the corresponding RPC-side policy. Tests were adjusted away from legacy transactions without chain id.

# Why It Matters

1. Reduces acceptance of Ethereum transactions lacking chain-id replay protection.

2. Aligns runtime configuration across Moonriver, Moonbeam, and Moonbase.

3. Aligns tests with the stricter transaction policy.

4. No supplied evidence proves exploitation, fund loss, or a specific replay target.

# Evidence Notes

Grounded evidence consists of the explicit `AllowUnprotectedTxs: bool = true` to `false` changes in three runtime files, the RPC boolean change from `true` to `false`, and the commit message `forbid unprotected txs` / `Tests must not use legacy txs without chain id`. The surrounding `ConvertTransaction` excerpts show proximity to Ethereum transaction wrapping, but they do not by themselves prove where validation occurs. XCM, bridge, and precompile traces are incidental and should not define the subsystem. Protocol security invariant: Ethereum transaction admission should not accept legacy unprotected transactions without chain-id replay protection unless that compatibility behavior is explicitly intended. The patch changes explicit `AllowUnprotectedTxs` runtime settings from `true` to `false` and changes a related RPC configuration boolean from `true` to `false`. Verification notes: The patch does not by itself prove a demonstrated exploit or fund loss. The evidence does not show which external networks or chain ids could be replay targets. The evidence does not prove consensus invalidity or block-production compromise. The evidence does not show the full RPC constructor signature, only the changed boolean argument. XCM and precompile contexts are incidental trace results, not the primary affected subsystem. Full RPC constructor signature is not provided, so the RPC boolean role is inferred from commit context rather than independently proven. No exploit, incident, or concrete replay target is shown in the supplied input. The evidence supports replay-protection hardening more strongly than a confirmed exploited vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unprotected-transaction-admission`
Final impact type: `replay-risk-reduction`
Final confidence: `high`
Final tags: `blockchain-core, transaction-processing, transaction-admission, ethereum, replay-protection, runtime-config, rpc`

The supplied patch evidence clearly shows Moonbeam disabling acceptance of unprotected legacy Ethereum transactions by changing `AllowUnprotectedTxs` from `true` to `false` across Moonriver, Moonbeam, and Moonbase, with a matching commit message about forbidding unprotected transactions and avoiding legacy transactions without chain id. This supports a security-hardening corpus entry focused on replay-protection policy, but not a concrete security-fix claim because no exploit, incident, or demonstrated replay path is shown.

## Security Evidence

1. Commit subject and body explicitly state unprotected transactions are forbidden and tests must not use legacy transactions without chain id.
2. Runtime configuration changes `AllowUnprotectedTxs: bool = true` to `false` in Moonriver, Moonbeam, and Moonbase.
3. RPC-side code changes a related boolean from `true` to `false`, aligning node transaction handling with the stricter policy.
4. The changed setting is located near Ethereum transaction conversion and `pallet_ethereum::Config`, a security-sensitive transaction-processing path.

## Missing Evidence

1. No exploit, incident report, or demonstrated replay attack is provided.
2. No full validation implementation is shown to prove exactly how unprotected transactions were previously accepted or rejected.
3. The RPC constructor argument name is not shown, so its precise role is inferred from commit context.
4. No concrete affected chain, asset, or fund-loss scenario is established.

## Claim Boundaries

1. Keep claims to disabling unprotected legacy Ethereum transaction admission.
2. Do not claim proven exploitation or fund loss.
3. Do not claim consensus compromise or block-production impact from the supplied evidence.
4. Treat XCM, bridge, and precompile contexts as incidental rather than primary affected subsystems.
