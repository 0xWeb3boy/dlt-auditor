---
case_id: case_20220912_c7d8fc12f2
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
  - git:c7d8fc12f26286d20f8fa5edc6c19f83880e091c
  - "precompiles/proxy/src/lib.rs:58"
  - "precompiles/proxy/src/tests.rs:526"
  - "runtime/moonriver/src/precompiles.rs:108"
  - "runtime/moonbeam/src/precompiles.rs:108"
bug_class: evm-precompile-authorization-boundary-hardening
impact_type:
  - access-control-hardening
  - authorization-boundary-hardening
confidence: high
tags:
  - blockchain-core
  - evm-precompile
  - proxy-precompile
  - dispatch-precompile
  - access-control
  - authorization-boundary
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix for Moonbeam/Moonriver EVM precompile boundaries. It adds an early caller-code guard to the proxy precompile so arbitrary smart-contract accounts are rejected, and it disables the generic Dispatch precompile in the Moonbeam and Moonriver runtime precompile sets. The evidence supports a caller/origin authorization concern, but does not prove a complete external exploit path or concrete asset impact.

## Observed Patch Facts

1. In `precompiles/proxy/src/lib.rs`, the patch replaces `let selector = handle.read_selector()?;` with `handle.record_cost(RuntimeHelper::<Runtime>::db_read_gas_cost())?;`.

2. In `precompiles/proxy/src/tests.rs`, the patch adds `#[test]`.

3. In `runtime/moonriver/src/precompiles.rs`, the patch replaces `PrecompileAt<AddressU64<1025>, Dispatch<R>>,` with `// PrecompileAt<AddressU64<1025>, Dispatch<R>>,`.

4. In `runtime/moonbeam/src/precompiles.rs`, the patch replaces `PrecompileAt<AddressU64<1025>, Dispatch<R>>,` with `// PrecompileAt<AddressU64<1025>, Dispatch<R>>,`.

## Project Context

The changed code sits primarily in `precompiles/proxy/src`, `precompiles/proxy`, `runtime/moonriver/src`, which anchors the finding in the `staking` area of the project. Historical context from `precompiles/proxy/src/mock.rs`, `runtime/moonriver/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/proxy/src/mock.rs`, `runtime/moonriver/src/lib.rs`. The strongest project-level identifiers around this patch are `PrecompileAt`, `AddressU64`, `pallet_evm::AccountCodes`, and `Moonbeam`. Nearby tests or test-like files include `runtime/moonriver/tests/xcm_mock/parachain.rs`, `runtime/moonbeam/tests/xcm_mock/parachain.rs`.

## Before/After Behavior

Before the patch, the supplied proxy precompile hunk shows `ProxyWrapper::execute` proceeding to selector handling without a visible check on whether the EVM caller had deployed code. After the patch, it charges database-read gas, reads `pallet_evm::AccountCodes` for `handle.context().caller`, and reverts with `Batch not callable by smart contracts` unless the caller has no code or matches the explicit sentinel bytecode. Before the patch, Moonbeam and Moonriver registered `PrecompileAt<AddressU64<1025>, Dispatch<R>>`; after the patch, that registration is commented out. Tests were added or updated for smart-contract caller rejection and nested proxy/EVM behavior involving attempted proxy type escalation.

# Root Cause

The proxy precompile did not visibly enforce the new caller-code restriction before executing precompile logic, and the runtimes exposed a generic Dispatch precompile. The evidence supports an under-restricted EVM-to-runtime precompile boundary, but not a fully reconstructed exploit.

## Walkthrough

1. A call enters `ProxyWrapper::execute` through the proxy precompile.

2. Previously, the provided hunk shows execution moving directly toward selector parsing without the new caller-code check.

3. The patched code reads the caller account code from `pallet_evm::AccountCodes`.

4. If the caller has arbitrary deployed code, the proxy precompile now reverts with `Batch not callable by smart contracts`.

5. The guard allows empty caller code and one explicit sentinel bytecode case described by the source comment as related to another precompile.

6. The Moonbeam and Moonriver runtime precompile sets no longer register `Dispatch<R>` at address 1025.

7. Regression tests cover smart-contract caller rejection and nested proxy/EVM behavior where proxy type escalation should not succeed.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/proxy/src/lib.rs | 58 | Adds caller-code check in ProxyWrapper::execute and reverts when the proxy precompile is invoked by an arbitrary smart contract. |
| precompiles/proxy/src/tests.rs | 478 | Covers nested EVM/proxy behavior where proxy type escalation through a precompile call should not succeed. |
| precompiles/proxy/src/tests.rs | 526 | Adds regression coverage that calls from smart-contract accounts to the proxy precompile fail. |
| runtime/moonbeam/src/precompiles.rs | 108 | Removes the Dispatch precompile from the Moonbeam runtime precompile set. |
| runtime/moonriver/src/precompiles.rs | 108 | Removes the Dispatch precompile from the Moonriver runtime precompile set. |

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

Context: `runtime/moonriver/src/precompiles.rs:108` (changes a sensitive control or state-update path)

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

Context: `runtime/moonbeam/src/precompiles.rs:108` (changes a sensitive control or state-update path)

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

Add an early precompile entry guard based on caller code, fail closed for arbitrary smart-contract callers, and remove a generic dispatch precompile from runtime exposure.

## How It Was Fixed

`precompiles/proxy/src/lib.rs` now records database-read gas, reads the caller's EVM account code, and rejects arbitrary smart-contract callers before selector handling proceeds. `runtime/moonbeam/src/precompiles.rs` and `runtime/moonriver/src/precompiles.rs` comment out the `Dispatch<R>` precompile registration at address 1025. Tests in `precompiles/proxy/src/tests.rs` exercise the new rejection behavior and nested proxy/EVM behavior.

# Why It Matters

1. Protects the EVM-to-Substrate precompile authorization boundary.

2. Prevents arbitrary deployed contract code from calling the proxy precompile under the patched rules.

3. Removes a generic Dispatch precompile from Moonbeam and Moonriver runtime exposure.

4. Adds regression coverage for smart-contract caller rejection and proxy escalation behavior.

5. The evidence does not establish direct fund theft or a complete exploit transaction.

# Evidence Notes

Grounded evidence comes from commit text stating `disable dispatch precompile` and `prevent smart contracts to call proxy precompile`, the added caller-code check and revert in `precompiles/proxy/src/lib.rs`, the commented-out `Dispatch<R>` registrations in Moonbeam and Moonriver runtime precompile sets, and tests for smart-contract caller failure and nested proxy/EVM behavior. Claims about staking, direct theft, all precompile bridges, or a complete exploit path are not supported by the provided evidence. Protocol security invariant: EVM precompiles that bridge into Substrate proxy or dispatch behavior must preserve the intended caller/origin authorization boundary and must not be callable from arbitrary deployed smart-contract code when that would bypass the expected access model. Verification notes: The patch does not prove that arbitrary users could steal funds directly. The patch does not show the complete pre-patch exploit transaction sequence. The patch does not establish that all precompile-to-runtime bridges were vulnerable. The special allowed bytecode case is treated as intended behavior, not proven independently safe by this evidence. Impact is limited to proxy/dispatch precompile authorization boundaries shown in the patch. Security relevance is supported by code guards, runtime exposure removal, commit text, and regression tests. Confidence is medium because the supplied evidence does not include a full exploit sequence or impact analysis. Subsystem should be proxy/dispatch EVM precompiles, not staking. Bug class should remain at caller authorization boundary level rather than a more specific asset-loss claim. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `evm-precompile-authorization-boundary-hardening`
Final impact type: `access-control-hardening, authorization-boundary-hardening`
Final confidence: `high`
Final tags: `blockchain-core, evm-precompile, proxy-precompile, dispatch-precompile, access-control, authorization-boundary, security-hardening`

The supplied evidence strongly supports retaining this as security hardening, not as a proven exploit fix. The patch restricts a security-sensitive EVM-to-runtime boundary by rejecting arbitrary smart-contract callers to the proxy precompile and removes the generic Dispatch precompile from Moonbeam and Moonriver runtime exposure. The original staking framing and security-fix classification are too specific or too strong; the supported claim is precompile authorization boundary hardening.

## Security Evidence

1. Commit body explicitly says "disable dispatch precompile" and "prevent smart contracts to call proxy precompile".
2. Proxy precompile now reads caller account code and reverts with "Batch not callable by smart contracts" for arbitrary deployed-code callers.
3. Moonbeam and Moonriver runtime precompile sets comment out `PrecompileAt<AddressU64<1025>, Dispatch<R>>`.
4. Tests cover smart-contract caller rejection and nested proxy/EVM behavior involving attempted proxy type escalation.

## Missing Evidence

1. No complete exploit transaction or attacker workflow is shown.
2. No direct asset-loss, privilege escalation impact, or affected funds are proven.
3. No external advisory or vulnerability description is provided.
4. The special allowed sentinel bytecode case is not independently justified by the supplied evidence.

## Claim Boundaries

1. Validate as security hardening of proxy/dispatch EVM precompile exposure, not as a confirmed concrete exploit fix.
2. Do not classify this as staking-specific based on the supplied patch evidence.
3. Do not claim fund theft, universal precompile compromise, or a complete authorization bypass beyond the shown proxy/dispatch boundary.
4. The evidence supports arbitrary smart-contract caller restriction, while allowing EOAs and one explicit sentinel bytecode case under the patched logic.
