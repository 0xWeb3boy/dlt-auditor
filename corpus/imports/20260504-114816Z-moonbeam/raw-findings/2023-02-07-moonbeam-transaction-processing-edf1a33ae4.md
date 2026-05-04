---
case_id: case_20230207_edf1a33ae4
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-02-07
source_refs:
  - git:edf1a33ae4c1046e91db9801fa67287729ed4d45
  - "precompiles/utils/src/precompile_set.rs:467"
  - "precompiles/utils/src/precompile_set.rs:576"
  - "precompiles/proxy/src/lib.rs:107"
  - "precompiles/utils/src/precompile_set.rs:30"
bug_class: precompile-call-policy-hardening
impact_type:
  - access-control-hardening
  - attack-surface-reduction
confidence: medium
tags:
  - blockchain-core
  - evm-precompiles
  - access-control
  - call-permission-checks
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears security-relevant because it replaces local precompile dispatch checks with shared `common_checks` and removes a bespoke proxy selector pre-check. However, the evidence supports a hardening or check-system refactor more than a demonstrated vulnerability fix. No concrete unauthorized call, exploit path, or broken invariant is proven from the provided snippets.

## Observed Patch Facts

1. In `precompiles/utils/src/precompile_set.rs`, the patch replaces `// Check DELEGATECALL config.` with `// Perform common checks.`.

2. In `precompiles/utils/src/precompile_set.rs`, the patch replaces `// Check DELEGATECALL config.` with `// Perform common checks.`.

3. In `precompiles/proxy/src/lib.rs`, the patch replaces `#[precompile::pre_check]` with `/// Register a proxy account for the sender that is able to make calls on its behalf.`.

4. In `precompiles/utils/src/precompile_set.rs`, the patch replaces `// CONFIGURATION TYPES` with `/// Trait representing checks that can be made on a precompile call.`.

## Project Context

The changed code sits primarily in `precompiles/utils/src`, `precompiles/utils`, `precompiles/proxy/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `precompiles/utils/src/handle.rs`, `precompiles/utils/src/substrate.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/utils/src/testing/modifier.rs`, `precompiles/utils/src/testing/execution.rs`. The strongest project-level identifiers around this patch are `Some`, `D::allow_delegate_call`, `handle`, and `recursion_limit`. Nearby tests or test-like files include `precompiles/utils/macro/tests/precompile/compile-fail/fn-modifiers/pre-check-multiple.rs`, `precompiles/utils/macro/tests/precompile/expand/precompileset.expanded.rs`.

## Before/After Behavior

Before the change, the shown precompile dispatch paths contained an inline `DELEGATECALL`/`CALLCODE` guard and the proxy precompile had a custom selector-based `pre_check` that allowed `isProxy` selectors. After the change, the dispatch paths call `common_checks::<R, C>(handle)` before recursion handling and execution, and the proxy-specific pre-check is removed in favor of the new centralized check system described by the commit message.

# Root Cause

The supported root cause is fragmented precompile check logic: some call-mode and selector/caller restrictions were implemented locally rather than through one shared precompile check configuration. The evidence does not prove that this fragmentation caused a specific security bypass.

## Walkthrough

1. A call enters a precompile dispatch path in `precompiles/utils/src/precompile_set.rs`.

2. The old shown logic checked the target precompile and then applied a local delegatecall/callcode guard.

3. The patch replaces that local guard with `common_checks::<R, C>(handle)` in the observed dispatch paths.

4. The shared check runs before recursion handling and precompile execution in the supplied after-context.

5. The proxy precompile previously had a custom selector-based pre-check for `isProxy`; that code is removed in the supplied after-context.

6. The commit message references `ContractCanCall(Selector)`, `CallableByPrecompile`, and subcall defaults, supporting a migration to explicit centralized checks.

7. The evidence does not show a transaction or call sequence that could exploit the previous behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/utils/src/precompile_set.rs | 30 | defines the shared precompile check trait/configuration used to compose call restrictions |
| precompiles/utils/src/precompile_set.rs | 458 | single-address precompile dispatch now runs common_checks before recursion handling and execution |
| precompiles/utils/src/precompile_set.rs | 568 | precompile-set dispatch now runs common_checks before recursion handling and execution |
| precompiles/proxy/src/lib.rs | 97 | proxy precompile removes custom selector pre_check in favor of centralized precompile call checks |

## Code Snippets

## Snippet 1

Context: `precompiles/utils/src/precompile_set.rs:467` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

		// Check DELEGATECALL config.
		if !D::allow_delegate_call() && code_address != handle.context().address {
			return Some(Err(revert(
				"Cannot be called with DELEGATECALL or CALLCODE",
			)));
		}
```
After
```rust
}

		// Perform common checks.
		if let Err(err) = common_checks::<R, C>(handle) {
			return Some(Err(err));
		}

		// Check and increase recursion level if needed.
```

## Snippet 2

Context: `precompiles/utils/src/precompile_set.rs:576` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

		// Check DELEGATECALL config.
		if !D::allow_delegate_call() && code_address != handle.context().address {
			return Some(Err(revert(
				"Cannot be called with DELEGATECALL or CALLCODE",
			)));
		}
```
After
```rust
}

		// Perform common checks.
		if let Err(err) = common_checks::<R, C>(handle) {
			return Some(Err(err));
		}

		// Check and increase recursion level if needed.
```

## Snippet 3

Context: `precompiles/proxy/src/lib.rs:107` (changes bounds, limits, or capacity handling)

Before
```rust
<Runtime as frame_system::Config>::RuntimeCall: From<ProxyCall<Runtime>>,
{
	#[precompile::pre_check]
	fn pre_check(handle: &mut impl PrecompileHandle) -> EvmResult {
		// Check if the selector is the one of `isProxy`, which is one which can
		// be called by smart contrats.
		if let Some(bytes) = handle.input().get(0..4) {
			let mut buffer = [0u8; 4];
```
After
```rust
<Runtime as frame_system::Config>::RuntimeCall: From<ProxyCall<Runtime>>,
{
	/// Register a proxy account for the sender that is able to make calls on its behalf.
	/// The dispatch origin for this call must be Signed.
```

## Snippet 4

Context: `precompiles/utils/src/precompile_set.rs:30` (changes bounds, limits, or capacity handling)

Before
```rust
};

// CONFIGURATION TYPES

mod sealed {
	pub trait Sealed {}
}
```
After
```rust
};

mod sealed {
	pub trait Sealed {}
}

/// Trait representing checks that can be made on a precompile call.
/// Types implementing this trait are made to be chained in a tuple.
```

# Fix Pattern

Centralize precompile call checks in shared dispatch infrastructure and replace bespoke per-precompile checks with composable policy configuration.

## How It Was Fixed

The patch introduces or expands shared precompile check configuration, invokes `common_checks::<R, C>(handle)` from the observed precompile dispatch paths, adjusts recursion-limit policy to use the shared configuration, and removes the proxy precompile's custom selector pre-check. Tests and check summaries are mentioned in the commit body as support for the migration.

# Why It Matters

1. Precompile dispatch is a sensitive EVM boundary.

2. Inconsistent per-precompile checks can increase review risk.

3. Centralized checks make policy easier to audit.

4. No concrete exploitable vulnerability is proven here.

# Evidence Notes

Grounded evidence is limited to changed snippets in `precompiles/utils/src/precompile_set.rs` and `precompiles/proxy/src/lib.rs`, plus the commit message. Claims about unauthorized proxy actions, concrete exploitability, replay, cryptography, storage corruption, or confirmed vulnerability impact are unsupported. Protocol security invariant: EVM precompile dispatch should apply consistent call-mode and caller-permission checks before executing precompile logic. The supplied evidence shows these checks being centralized, but it does not establish that the previous implementation allowed an exploitable bypass. Verification notes: No concrete exploit path is proven from the provided patch evidence. No specific unauthorized proxy operation is shown to have been reachable before the change. The patch appears to include broad refactor, test, and API cleanup work, so not every touched file is security-relevant. The evidence supports call-permission hardening, not a confirmed cryptographic, replay, or storage-corruption flaw. Confirmed from supplied evidence: shared `common_checks` replaced an inline delegatecall/callcode guard in two dispatch paths. Confirmed from supplied evidence: proxy custom selector pre-check was removed. Not confirmed: that the old behavior was exploitable. Not confirmed: any specific attacker-controlled unauthorized operation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `precompile-call-policy-hardening`
Final impact type: `access-control-hardening, attack-surface-reduction`
Final confidence: `medium`
Final tags: `blockchain-core, evm-precompiles, access-control, call-permission-checks, security-hardening`

The supplied evidence does not prove a concrete exploitable vulnerability, so this should not be retained as a security-fix. However, the commit and patch evidence do support security-hardening: precompile dispatch is a sensitive boundary, inline delegatecall/callcode handling is replaced by shared common checks, the commit explicitly adds ContractCanCall/CallableByPrecompile checks, and subcalls are disabled by default. That is enough to keep as a hardening case with conservative metadata.

## Security Evidence

1. Commit subject explicitly references an explicit list of security checks for precompile sets.
2. Commit body mentions subcalls disabled by default, ContractCanCall(Selector) checks, and CallableByPrecompile filtering.
3. Precompile dispatch paths now call common_checks::<R, C>(handle) before recursion handling and execution.
4. The changed code affects EVM precompile dispatch and proxy precompile behavior, both security-sensitive call boundaries.

## Missing Evidence

1. No exploit path or unauthorized transaction sequence is shown.
2. The snippets do not include the full common_checks implementation.
3. No before/after test demonstrates a previously allowed malicious call being rejected.
4. No advisory, CVE, incident, or concrete vulnerability impact is provided.

## Claim Boundaries

1. Validate only as security-hardening, not a confirmed vulnerability fix.
2. Do not claim cryptographic, replay, storage-corruption, or fund-loss impact from this evidence.
3. Do not claim a specific proxy authorization bypass was exploitable before the patch.
4. The supported claim is centralized and stricter precompile call-policy enforcement.
