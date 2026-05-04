---
case_id: case_20220912_dade7f12a7
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
source_quality: medium
date: 2022-09-12
source_refs:
  - git:dade7f12a7ba3e21a614282987de6acd4489cbce
  - "precompiles/proxy/src/lib.rs:58"
  - "precompiles/proxy/src/tests.rs:526"
  - "runtime/moonriver/src/precompiles.rs:109"
  - "runtime/moonbeam/src/precompiles.rs:109"
bug_class: evm-precompile-access-control-hardening
impact_type:
  - access-control-hardening
confidence: medium
tags:
  - blockchain-core
  - evm-precompile
  - proxy-precompile
  - dispatch-precompile
  - access-control-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for Moonbeam EVM precompile access control. The supported evidence shows two changes: the proxy precompile now rejects smart-contract callers based on pallet_evm::AccountCodes, and the Dispatch precompile at AddressU64<1025> is disabled in Moonbeam and Moonriver runtime precompile sets. The exact exploit impact is not fully proven by the provided evidence, so this should not be treated as a fully confirmed vulnerability.

## Observed Patch Facts

1. In `precompiles/proxy/src/lib.rs`, the patch replaces `let selector = handle.read_selector()?;` with `handle.record_cost(RuntimeHelper::<Runtime>::db_read_gas_cost())?;`.

2. In `precompiles/proxy/src/tests.rs`, the patch adds `#[test]`.

3. In `runtime/moonriver/src/precompiles.rs`, the patch replaces `PrecompileAt<AddressU64<1025>, Dispatch<R>>,` with `// PrecompileAt<AddressU64<1025>, Dispatch<R>>,`.

4. In `runtime/moonbeam/src/precompiles.rs`, the patch replaces `PrecompileAt<AddressU64<1025>, Dispatch<R>>,` with `// PrecompileAt<AddressU64<1025>, Dispatch<R>>,`.

## Project Context

The changed code sits primarily in `precompiles/proxy/src`, `precompiles/proxy`, `runtime/moonriver/src`, which anchors the finding in the `staking` area of the project. Historical context from `precompiles/proxy/src/mock.rs`, `runtime/moonriver/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/proxy/src/mock.rs`, `runtime/moonriver/src/lib.rs`. The strongest project-level identifiers around this patch are `PrecompileAt`, `AddressU64`, `pallet_evm::AccountCodes`, and `Moonbeam`. Nearby tests or test-like files include `runtime/moonriver/tests/xcm_mock/parachain.rs`, `runtime/moonbeam/tests/xcm_mock/parachain.rs`.

## Before/After Behavior

Before the patch, the visible proxy precompile execute path proceeded to selector handling without a shown caller-code gate. After the patch, it charges for a database read, loads AccountCodes for handle.context().caller, and reverts with "Batch not callable by smart contracts" unless the caller has no code or matches the allowed sentinel bytecode. Separately, MoonbeamPrecompiles and MoonriverPrecompiles previously registered PrecompileAt<AddressU64<1025>, Dispatch<R>>; after the patch that registration is commented out. A regression test models a caller with non-empty AccountCodes and exercises the rejection path.

# Root Cause

The visible root cause is missing or insufficient caller eligibility enforcement at EVM precompile entry points that bridge into runtime/proxy or dispatch behavior. The supplied evidence supports that the proxy precompile lacked the newly added smart-contract caller restriction and that the generic Dispatch precompile was exposed in the runtime registry.

## Walkthrough

1. ProxyWrapper<Runtime>::execute is an EVM precompile entry point for proxy-related runtime behavior.

2. The pre-patch snippet shows execute beginning with selector handling and does not show a check on whether the caller has EVM bytecode.

3. The patch adds a gas charge for reading storage, retrieves pallet_evm::AccountCodes for the caller, and rejects callers with deployed code unless the code is empty or equals the explicit sentinel bytecode.

4. The added test inserts vec![10u8] into AccountCodes for Alice to model a smart-contract caller and verifies the proxy precompile fails under that condition.

5. The Moonbeam and Moonriver runtime precompile registries previously included Dispatch<R> at address 1025.

6. The patch comments out that Dispatch<R> registration in both runtimes, removing that generic precompile entry point from the shown registries.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/proxy/src/lib.rs | 58 | adds runtime guard that rejects proxy precompile execution when the EVM caller has deployed smart contract code |
| precompiles/proxy/src/tests.rs | 526 | adds regression coverage for rejecting proxy precompile calls from a smart contract caller |
| runtime/moonbeam/src/precompiles.rs | 109 | removes generic Dispatch precompile from the Moonbeam runtime precompile registry |
| runtime/moonriver/src/precompiles.rs | 109 | removes generic Dispatch precompile from the Moonriver runtime precompile registry |

## Code Snippets

## Snippet 1

Context: `precompiles/proxy/src/lib.rs:58` (changes the branch that decides whether execution stops or continues)

Before
```rust
{
	fn execute(handle: &mut impl PrecompileHandle) -> EvmResult<PrecompileOutput> {
		let selector = handle.read_selector()?;
```
After
```rust
{
	fn execute(handle: &mut impl PrecompileHandle) -> EvmResult<PrecompileOutput> {
		handle.record_cost(RuntimeHelper::<Runtime>::db_read_gas_cost())?;
		let caller_code = pallet_evm::Pallet::<Runtime>::account_codes(handle.context().caller);
		// Check that caller is not a smart contract s.t. no code is inserted into
		// pallet_evm::AccountCodes except if the caller is another precompile i.e. CallPermit
		if !(caller_code.is_empty() || &caller_code == &[0x60, 0x00, 0x60, 0x00, 0xfd]) {
			return Err(revert("Batch not callable by smart contracts"));
```

## Snippet 2

Context: `precompiles/proxy/src/tests.rs:526` (changes aggregate state or economic accounting)

Before
```rust
})
}
```
After
```rust
})
}

#[test]
fn fails_if_called_by_smart_contract() {
	ExtBuilder::default()
		.with_balances(vec![(Alice, 1000), (Bob, 1000)])
		.build()
```

## Snippet 3

Context: `runtime/moonriver/src/precompiles.rs:109` (changes a sensitive control or state-update path)

Before
```rust
// Non-Moonbeam specific nor Ethereum precompiles :
				PrecompileAt<AddressU64<1024>, Sha3FIPS256>,
				PrecompileAt<AddressU64<1025>, Dispatch<R>>,
				PrecompileAt<AddressU64<1026>, ECRecoverPublicKey>,
				// Moonbeam specific precompiles:
```
After
```rust
// Non-Moonbeam specific nor Ethereum precompiles :
				PrecompileAt<AddressU64<1024>, Sha3FIPS256>,
				// PrecompileAt<AddressU64<1025>, Dispatch<R>>,
				PrecompileAt<AddressU64<1026>, ECRecoverPublicKey>,
				// Moonbeam specific precompiles:
```

## Snippet 4

Context: `runtime/moonbeam/src/precompiles.rs:109` (changes a sensitive control or state-update path)

Before
```rust
// Non-Moonbeam specific nor Ethereum precompiles :
				PrecompileAt<AddressU64<1024>, Sha3FIPS256>,
				PrecompileAt<AddressU64<1025>, Dispatch<R>>,
				PrecompileAt<AddressU64<1026>, ECRecoverPublicKey>,
				// Moonbeam specific precompiles:
```
After
```rust
// Non-Moonbeam specific nor Ethereum precompiles :
				PrecompileAt<AddressU64<1024>, Sha3FIPS256>,
				// PrecompileAt<AddressU64<1025>, Dispatch<R>>,
				PrecompileAt<AddressU64<1026>, ECRecoverPublicKey>,
				// Moonbeam specific precompiles:
```

# Fix Pattern

Add an explicit caller-code eligibility guard at precompile entry and remove a broad dispatch precompile from runtime registration.

## How It Was Fixed

The proxy precompile now checks pallet_evm::AccountCodes for handle.context().caller before handling selectors and reverts for callers with deployed code outside the allowed sentinel case. The Moonbeam and Moonriver precompile sets no longer register Dispatch<R> at AddressU64<1025>. Tests were updated to cover rejection of a smart-contract caller.

# Why It Matters

1. Restricts smart-contract access to the proxy precompile path shown in the patch.

2. Removes a generic dispatch precompile entry point from two runtime registries.

3. Adds regression coverage for the newly enforced caller-code condition.

4. Exact privilege impact is not established by the supplied evidence.

# Evidence Notes

Grounded evidence comes from precompiles/proxy/src/lib.rs line 58, precompiles/proxy/src/tests.rs line 526, runtime/moonbeam/src/precompiles.rs line 109, and runtime/moonriver/src/precompiles.rs line 109. The commit message also states "disable dispatch precompile" and "prevent smart contracts to call proxy precompile." Unsupported or over-strong claims removed: the evidence does not prove a full exploit transaction, does not prove arbitrary privilege escalation, does not establish the safety of the sentinel bytecode exception, and does not provide concrete Moonbase hunks despite listing Moonbase files. Protocol security invariant: Runtime-bridging EVM precompiles should not expose proxy or generic dispatch behavior to callers that are not eligible to invoke those paths. In the supplied patch, the proxy precompile rejects callers with deployed EVM code except for a specific sentinel bytecode case, and the generic Dispatch precompile is removed from Moonbeam and Moonriver registration. Verification notes: The patch does not prove a complete end-to-end exploit transaction from the provided evidence alone. The exact privilege impact of the disabled Dispatch precompile is not shown beyond removal from the runtime registry. The special allowed bytecode sentinel for CallPermit is accepted by the guard but its safety properties are not established in the provided context. Moonbase changes are listed in the commit files but no concrete hunk evidence is provided here. Do not classify this as staking; the supported subsystem is EVM precompiles/proxy/dispatch. Confidence is medium because the access-control intent is clear but complete exploitability is not shown. The Dispatch precompile removal is security-relevant, but its exact impact is not demonstrated beyond removal from registration. Helper and test files should be treated as supporting evidence, not root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `evm-precompile-access-control-hardening`
Final impact type: `access-control-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, evm-precompile, proxy-precompile, dispatch-precompile, access-control-hardening`

The supplied patch evidence supports retaining this as security hardening, not a fully proven security fix. The code adds an explicit caller-code guard that prevents smart contracts from invoking the proxy precompile, adds a regression test for that rejection, and removes the generic Dispatch precompile from Moonbeam and Moonriver runtime registries. These are security-sensitive exposure reductions, but the provided evidence does not prove a concrete exploit path or exact impact. The original staking classification is misleading; the supported subsystem is EVM precompiles/proxy/dispatch.

## Security Evidence

1. Proxy precompile now reads pallet_evm::AccountCodes for handle.context().caller and reverts when the caller has deployed code outside the allowed sentinel case.
2. The revert message explicitly states "Batch not callable by smart contracts".
3. A test named fails_if_called_by_smart_contract models non-empty AccountCodes and covers rejection of smart-contract callers.
4. Moonbeam and Moonriver runtime registries comment out PrecompileAt<AddressU64<1025>, Dispatch<R>>, removing a broad dispatch precompile entry point.
5. Commit body states "disable dispatch precompile" and "prevent smart contracts to call proxy precompile".

## Missing Evidence

1. No complete exploit transaction or proof of privilege escalation is supplied.
2. The exact capabilities exposed by Dispatch<R> are not shown in the provided evidence.
3. The safety rationale for the allowed sentinel bytecode exception is not established.
4. Moonbase files are listed in commit metadata, but no concrete Moonbase patch evidence is provided.

## Claim Boundaries

1. Classify as EVM precompile/proxy/dispatch access-control hardening, not staking.
2. Do not claim confirmed arbitrary privilege escalation from the supplied patch alone.
3. Do not claim the Dispatch precompile removal fixes a specific demonstrated exploit without more context.
4. Treat the test evidence as supporting the new access restriction, not as proof of full exploitability.
