---
case_id: case_20250428_0e600693f7
project: moonbeam
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: medium
source_quality: medium
tags:
  - infrastructure
  - transaction-processing
  - access-control
  - privilege-misuse
date: 2025-04-28
source_refs:
  - git:0e600693f70b67c59ed6a9688deb91fa5339cd5a
  - "runtime/moonbase/src/lib.rs:978"
  - "precompiles/proxy/src/lib.rs:380"
  - "runtime/moonbeam/src/lib.rs:967"
  - "runtime/moonriver/src/precompiles.rs:151"
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely security fix in the EVM proxy precompile authorization path. Moonbase changed ProxyType::Any from unconditional allow to target-based filtering, and Moonbeam corrected an unrecognized-target branch so a target must be both code-free and not a precompile. Comments in the changed code explicitly tie this restriction to preventing unauthorized smart-contract calls indirectly. The exact exploit path and concrete state impact are not shown, so confidence should remain medium rather than high.

## Observed Patch Facts

1. In `runtime/moonbase/src/lib.rs`, the patch replaces `ProxyType::Any => true,` with `ProxyType::Any => {`.

2. In `precompiles/proxy/src/lib.rs`, the patch replaces `// AccountCodes: Blake2128(16) + H160(20) + Vec(5)` with `// AccountCodesMetadata: 16 (hash) + 20 (key) + 40 (CodeMetadata).`.

3. In `runtime/moonbeam/src/lib.rs`, the patch replaces `// If the address is not recognized, allow only evm transfert to "simple"` with `// If the address is not recognized, allow only evm transfer to "simple"`.

4. In `runtime/moonriver/src/precompiles.rs`, the patch replaces `AddressU64<2050>,` with `AddressU64<ERC20_BALANCES_PRECOMPILE>,`.

## Project Context

The changed code sits primarily in `runtime/moonbase/src`, `runtime/moonbase`, `precompiles/proxy/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/moonriver/src/lib.rs`, `runtime/moonriver/src/runtime_params.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/proxy/src/mock.rs`, `precompiles/proxy/src/tests.rs`. The strongest project-level identifiers around this patch are `ProxyType::Any`, `Runtime`, `precompile_utils::precompile_set::is_precompile_or_fail`, and `code`. Nearby tests or test-like files include `runtime/moonriver/tests/runtime_apis.rs`, `runtime/moonbeam/tests/runtime_apis.rs`.

## Before/After Behavior

Before the patch, Moonbase returned true for ProxyType::Any in the EVM proxy call filter, so that runtime-specific filter did not inspect the EVM subcall target. After the patch, it classifies the target with PrecompileName::from_address, permits only selected precompiles, rejects other recognized precompiles, and permits unrecognized targets only when they are simple accounts with no code and not precompiles. Before the patch, Moonbeam's unrecognized-target branch allowed !recipient_has_code && is_precompile_or_fail, contradicting the stated simple-account rule. After the patch, it requires !recipient_has_code && !is_precompile_or_fail. The proxy precompile also changed recipient code detection from AccountCodes::decode_len to AccountCodesMetadata::get before applying the filter. The Moonriver address constant change appears to be related cleanup, not an independent root cause.

# Root Cause

Runtime-specific EVM proxy filtering was inconsistent and overly permissive. In Moonbase, ProxyType::Any bypassed target filtering entirely. In Moonbeam, the simple-account branch used the precompile predicate in the wrong direction. These mistakes could allow proxy-mediated EVM subcalls to targets the runtime intended to block.

## Walkthrough

1. The proxy precompile verifies the real address is an EOA and resolves the caller as an authorized proxy.

2. It determines whether the EVM subcall recipient has code, then applies the runtime-specific EvmProxyCallFilter.

3. Before the patch, Moonbase accepted ProxyType::Any without checking whether the target was a contract, precompile, or simple account.

4. The patched Moonbase filter whitelists only selected precompiles, rejects other recognized precompiles, and allows unrecognized targets only if they have no code and are not precompiles.

5. Before the patch, Moonbeam's unrecognized-target branch required the target to be a precompile despite comments saying only simple accounts should be allowed.

6. The patched Moonbeam branch negates the precompile check, matching the stated rule.

7. The recipient_has_code lookup was moved to AccountCodesMetadata, with the recorded database read updated accordingly.

8. The Moonriver constant replacement is best treated as consistency cleanup unless further evidence links it to enforcement.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/moonbase/src/lib.rs | 978 | Implements EvmProxyCallFilter for ProxyType; changes ProxyType::Any from unconditional allow to precompile/simple-account filtering. |
| precompiles/proxy/src/lib.rs | 380 | Proxy precompile inner_proxy path; determines whether subcall recipient has contract code before applying the proxy type filter. |
| runtime/moonbeam/src/lib.rs | 967 | Runtime EVM proxy call filter; fixes unrecognized target handling to require no recipient code and not a precompile. |
| runtime/moonriver/src/precompiles.rs | 151 | Precompile address constant cleanup related to runtime precompile mapping consistency. |

## Code Snippets

## Snippet 1

Context: `runtime/moonbase/src/lib.rs:978` (changes a sensitive control or state-update path)

Before
```rust
) -> precompile_utils::EvmResult<bool> {
		Ok(match self {
			ProxyType::Any => true,
			ProxyType::NonTransfer => {
				call.value == U256::zero()
```
After
```rust
) -> precompile_utils::EvmResult<bool> {
		Ok(match self {
			ProxyType::Any => {
				match PrecompileName::from_address(call.to.0) {
					// Any precompile that can execute a subcall should be forbidden here,
					// to ensure that unauthorized smart contract can't be called
					// indirectly.
					// To be safe, we only allow the precompiles we need.
```

## Snippet 2

Context: `precompiles/proxy/src/lib.rs:380` (changes a sensitive control or state-update path)

Before
```rust
// Read subcall recipient code
		// AccountCodes: Blake2128(16) + H160(20) + Vec(5)
		// decode_len reads the first 5 bytes to find the payload len under this key
		handle.record_db_read::<Runtime>(41)?;
		let recipient_has_code =
			pallet_evm::AccountCodes::<Runtime>::decode_len(evm_subcall.to.0).unwrap_or(0) > 0;
```
After
```rust
// Read subcall recipient code
		// AccountCodesMetadata: 16 (hash) + 20 (key) + 40 (CodeMetadata).
		handle.record_db_read::<Runtime>(ACCOUNT_CODES_METADATA_PROOF_SIZE.saturated_into())?;
		let recipient_has_code =
			pallet_evm::AccountCodesMetadata::<Runtime>::get(evm_subcall.to.0).is_some();

		// Apply proxy type filter
```

## Snippet 3

Context: `runtime/moonbeam/src/lib.rs:967` (changes a sensitive control or state-update path)

Before
```rust
// smart contracts through governance.
					None => {
						// If the address is not recognized, allow only evm transfert to "simple"
						// accounts (no code nor precompile).
						// Note: Checking the presence of the code is not enough because some
						// precompiles have no code.
						!recipient_has_code
							&& precompile_utils::precompile_set::is_precompile_or_fail::<Runtime>(
```
After
```rust
// smart contracts through governance.
					None => {
						// If the address is not recognized, allow only evm transfer to "simple"
						// accounts (no code nor precompile).
						// Note: Checking the presence of the code is not enough because some
						// precompiles have no code.
						!recipient_has_code
							&& !precompile_utils::precompile_set::is_precompile_or_fail::<Runtime>(
```

## Snippet 4

Context: `runtime/moonriver/src/precompiles.rs:151` (changes aggregate state or economic accounting)

Before
```rust
>,
	PrecompileAt<
		AddressU64<2050>,
		Erc20BalancesPrecompile<R, NativeErc20Metadata>,
		(CallableByContract, CallableByPrecompile),
```
After
```rust
>,
	PrecompileAt<
		AddressU64<ERC20_BALANCES_PRECOMPILE>,
		Erc20BalancesPrecompile<R, NativeErc20Metadata>,
		(CallableByContract, CallableByPrecompile),
```

# Fix Pattern

Replace broad or inconsistent allow logic in proxy subcall filtering with explicit target classification: whitelist intended precompiles, reject non-whitelisted precompiles, and allow ordinary transfers only to no-code, non-precompile accounts.

## How It Was Fixed

Moonbase changed ProxyType::Any from unconditional allow to whitelist-style target filtering. Moonbeam corrected the simple-account condition by negating the precompile check. The proxy precompile now uses AccountCodesMetadata to classify whether the recipient has code before invoking the runtime filter. A Moonriver hard-coded precompile address was replaced with a named constant as cleanup.

# Why It Matters

1. ProxyType::Any can still require runtime-specific limits for EVM subcalls.

2. Subcall-capable precompiles may create indirect paths to otherwise unauthorized calls.

3. A no-code check alone is insufficient because some precompiles may not have contract code.

4. The evidence supports an authorization-boundary issue, but not a proven exploit or asset impact.

# Evidence Notes

Strongest evidence is in runtime/moonbase/src/lib.rs changing ProxyType::Any from true to target filtering, runtime/moonbeam/src/lib.rs changing is_precompile_or_fail to !is_precompile_or_fail in the simple-account branch, and comments stating that precompiles capable of subcalls should be forbidden to prevent unauthorized smart-contract calls indirectly. precompiles/proxy/src/lib.rs supports the path by showing recipient_has_code is computed before the filter. The provided evidence does not enumerate a concrete forbidden target, attacker transaction, or resulting state impact. Protocol security invariant: EVM proxy subcalls should be constrained by the runtime proxy filter before execution. Even for ProxyType::Any, the filter is expected to prevent indirect calls to non-whitelisted precompiles or smart contracts, allowing only explicitly permitted precompiles and simple no-code, non-precompile accounts. Verification notes: No concrete attacker transaction or end-to-end exploit is shown in the provided evidence. No proof is provided that funds, staking state, governance state, or balances were actually modifiable through the prior behavior. The Moonriver precompile constant change alone looks like consistency cleanup, not independently security-relevant. The patch supports an indirect-call authorization concern, but exact reachable forbidden precompiles or contracts are not enumerated. No end-to-end exploit transaction is provided. No concrete funds, staking, governance, or balance impact is proven. Tests were updated, but their assertions are not included in the provided input. Moonriver constant replacement is not independently security-relevant on the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied patch evidence supports retaining this as a security fix. The main change replaces unconditional acceptance of `ProxyType::Any` EVM proxy calls with explicit target filtering, and the in-code comments state the reason is to prevent unauthorized smart contract calls through indirect precompile subcalls. A separate Moonbeam branch changes the precompile predicate from allowing precompiles to rejecting them for simple-account transfers, matching an authorization boundary. Concrete exploit details and asset impact are not shown, so medium confidence remains appropriate.

## Security Evidence

1. `ProxyType::Any => true` was replaced with target classification and whitelisting logic.
2. Changed comments explicitly say subcall-capable precompiles should be forbidden to prevent unauthorized smart contract calls indirectly.
3. Moonbeam changed `&& is_precompile_or_fail` to `&& !is_precompile_or_fail` in a branch intended to allow only no-code, non-precompile accounts.
4. The proxy precompile computes recipient code presence before applying the runtime-specific proxy call filter.

## Missing Evidence

1. No end-to-end attacker transaction is provided.
2. No concrete forbidden precompile or contract target is demonstrated as exploitable before the patch.
3. No specific funds, governance, staking, or balance impact is proven.
4. Updated test assertions are not included in the supplied evidence.

## Claim Boundaries

1. Classify this as an EVM proxy authorization fix, not as a proven fund-loss or governance-takeover issue.
2. The Moonriver address constant replacement should be treated as related cleanup unless separately evidenced.
3. The evidence supports indirect unauthorized-call prevention, but not a specific exploited incident.
4. Confidence should remain medium rather than high because exploitability and concrete impact are not fully demonstrated.
