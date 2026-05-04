---
case_id: case_20231031_456027eece
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2023-10-31
source_refs:
  - git:456027eeced03ec78a2915659074a5e66d7684a9
  - "runtime/common/src/weights/pallet_proxy.rs:61"
  - "runtime/moonriver/src/lib.rs:1157"
  - "runtime/moonbeam/src/lib.rs:1148"
  - "runtime/moonbase/src/lib.rs:1138"
bug_class: proxy-call-filter-hardening
impact_type:
  - authorization-policy-restriction
  - restricted-dispatch-prevention
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - proxy
  - evm
  - call-filter
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a NormalFilter rule in Moonriver, Moonbeam, and Moonbase that rejects pallet_proxy::Call::proxy when the delegated real account is an EVM contract account. It also updates proxy weights for the extra AccountCodes storage read. The evidence supports a proxy-call filtering change for contract accounts, but it does not prove an exploitable vulnerability or a concrete unsafe outcome, so this should be treated as security-relevant but unconfirmed.

## Observed Patch Facts

1. In `runtime/common/src/weights/pallet_proxy.rs`, the patch adds `// Manually adding 1 DB read that happen when filtering the proxy call transaction`.

2. In `runtime/moonriver/src/lib.rs`, the patch adds `pallet_proxy::Call::proxy { real, .. } => {`.

3. In `runtime/moonbeam/src/lib.rs`, the patch adds `pallet_proxy::Call::proxy { real, .. } => {`.

4. In `runtime/moonbase/src/lib.rs`, the patch adds `pallet_proxy::Call::proxy { real, .. } => {`.

## Project Context

The changed code sits primarily in `runtime/common/src/weights`, `runtime/common/src`, `runtime/moonriver/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/moonriver/src/xcm_config.rs`, `runtime/moonriver/src/asset_config.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/moonriver/src/xcm_config.rs`, `runtime/moonriver/src/asset_config.rs`. The strongest project-level identifiers around this patch are `pallet_proxy::Call::create_pure`, `pallet_proxy::Call::kill_pure`, `pallet_proxy::Call::proxy`, and `pallet_evm::AccountCodes`. Nearby tests or test-like files include `runtime/moonriver/tests/xcm_mock/parachain.rs`, `runtime/moonriver/tests/xcm_mock/mod.rs`.

## Before/After Behavior

Before the patch, RuntimeCall::Proxy denied create_pure and kill_pure, while pallet_proxy::Call::proxy fell through to the permissive `_ => true` branch. After the patch, pallet_proxy::Call::proxy checks whether `pallet_evm::AccountCodes::<Runtime>` contains code for `H160::from(*real)` and denies the call when code exists. The weight function adds one database read to account for that new lookup.

# Root Cause

The call filter did not distinguish proxy calls targeting accounts with deployed EVM code from other proxy calls. The evidence does not establish why allowing such proxy calls was exploitable, only that the runtime now treats contract-account proxy targets as disallowed.

## Walkthrough

1. A RuntimeCall::Proxy is evaluated by NormalFilter::contains.

2. Before the change, create_pure and kill_pure were denied, but proxy calls were allowed by the fallback branch.

3. The patch adds an explicit pallet_proxy::Call::proxy match arm.

4. The new arm converts the real account to H160 and checks AccountCodes for deployed EVM bytecode.

5. If bytecode exists, the filter returns false and rejects the proxy call.

6. The proxy weight is increased by one database read for the added AccountCodes lookup.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/moonriver/src/lib.rs | 1157 | NormalFilter denies pallet_proxy::Call::proxy when real is an EVM contract account |
| runtime/moonbeam/src/lib.rs | 1148 | Same production runtime filter rule for Moonbeam |
| runtime/moonbase/src/lib.rs | 1138 | Same runtime filter rule for Moonbase/test network |
| runtime/common/src/weights/pallet_proxy.rs | 61 | Proxy weight updated for the additional AccountCodes database read performed by the filter |

## Code Snippets

## Snippet 1

Context: `runtime/common/src/weights/pallet_proxy.rs:61` (updates aggregate accounting or lifecycle state)

Before
```rust
.saturating_add(Weight::from_parts(45_679, 0).saturating_mul(p.into()))
			.saturating_add(T::DbWeight::get().reads(2))
			.saturating_add(Weight::from_parts(0, 25).saturating_mul(p.into()))
	}
```
After
```rust
.saturating_add(Weight::from_parts(45_679, 0).saturating_mul(p.into()))
			.saturating_add(T::DbWeight::get().reads(2))
			// Manually adding 1 DB read that happen when filtering the proxy call transaction
			.saturating_add(T::DbWeight::get().reads(1))
			.saturating_add(Weight::from_parts(0, 25).saturating_mul(p.into()))
	}
```

## Snippet 2

Context: `runtime/moonriver/src/lib.rs:1157` (updates aggregate accounting or lifecycle state)

Before
```rust
pallet_proxy::Call::create_pure { .. } => false,
				pallet_proxy::Call::kill_pure { .. } => false,
				_ => true,
			},
```
After
```rust
pallet_proxy::Call::create_pure { .. } => false,
				pallet_proxy::Call::kill_pure { .. } => false,
				pallet_proxy::Call::proxy { real, .. } => {
					!pallet_evm::AccountCodes::<Runtime>::contains_key(H160::from(*real))
				}
				_ => true,
			},
```

## Snippet 3

Context: `runtime/moonbeam/src/lib.rs:1148` (updates aggregate accounting or lifecycle state)

Before
```rust
pallet_proxy::Call::create_pure { .. } => false,
				pallet_proxy::Call::kill_pure { .. } => false,
				_ => true,
			},
```
After
```rust
pallet_proxy::Call::create_pure { .. } => false,
				pallet_proxy::Call::kill_pure { .. } => false,
				pallet_proxy::Call::proxy { real, .. } => {
					!pallet_evm::AccountCodes::<Runtime>::contains_key(H160::from(*real))
				}
				_ => true,
			},
```

## Snippet 4

Context: `runtime/moonbase/src/lib.rs:1138` (updates aggregate accounting or lifecycle state)

Before
```rust
pallet_proxy::Call::create_pure { .. } => false,
				pallet_proxy::Call::kill_pure { .. } => false,
				_ => true,
			},
```
After
```rust
pallet_proxy::Call::create_pure { .. } => false,
				pallet_proxy::Call::kill_pure { .. } => false,
				pallet_proxy::Call::proxy { real, .. } => {
					!pallet_evm::AccountCodes::<Runtime>::contains_key(H160::from(*real))
				}
				_ => true,
			},
```

# Fix Pattern

Add an explicit runtime call-filter rule for proxy calls that targets EVM contract accounts, and update weight accounting for the added storage read.

## How It Was Fixed

The three runtimes add the same `pallet_proxy::Call::proxy { real, .. }` filter arm under `RuntimeCall::Proxy`. The arm denies proxy dispatch when `pallet_evm::AccountCodes::<Runtime>::contains_key(H160::from(*real))` is true. The common proxy weight function adds `T::DbWeight::get().reads(1)` for the extra lookup.

# Why It Matters

1. Prevents proxy dispatch to accounts with deployed EVM code under the new policy.

2. Closes a previously permissive filter branch for pallet_proxy::Call::proxy.

3. Keeps runtime weight accounting aligned with the added storage access.

4. Security impact is plausible but not demonstrated by the supplied evidence.

# Evidence Notes

Grounded evidence is limited to the changed NormalFilter match arms in runtime/moonriver/src/lib.rs, runtime/moonbeam/src/lib.rs, and runtime/moonbase/src/lib.rs, plus the added database read in runtime/common/src/weights/pallet_proxy.rs. The draft's accounting-drift theory is unsupported. Claims about attacker profit, reentrancy, authorization bypass consequences, or concrete exploitability are not established by the provided snippets. Protocol security invariant: Runtime call filtering now prevents pallet_proxy::Call::proxy from delegating through a real account that has EVM bytecode in pallet_evm::AccountCodes. The provided evidence supports this as an enforced policy boundary, but does not establish the concrete security property that was violated before the patch. Verification notes: No concrete exploit transaction or attacker profit is shown by the patch evidence. No proof is provided that non-contract proxy delegation was unsafe. No evidence shows asset accounting drift or stale aggregate state as the root cause. The weight update is supporting fee/accounting maintenance, not the primary security fix. No exploit transaction or attacker-controlled scenario is provided. No test assertions are included in the supplied evidence, only test file names. The weight change appears to be support code for the new filter lookup. Classified as unclear because the patch may be security relevant, but the vulnerability thesis is not proven. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `proxy-call-filter-hardening`
Final impact type: `authorization-policy-restriction, restricted-dispatch-prevention`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, proxy, evm, call-filter, security-hardening`

The supplied patch evidence shows a deliberate runtime filter tightening: proxy calls whose real account has deployed EVM code are now rejected across Moonbeam, Moonriver, and Moonbase, with weight accounting updated for the added AccountCodes lookup. The evidence does not prove a concrete exploit, attacker path, asset loss, or accounting drift, so this should not be treated as a confirmed security fix. It is appropriate as security hardening because it narrows an exposed delegation path in a security-sensitive proxy/call-filter boundary.

## Security Evidence

1. NormalFilter now explicitly matches pallet_proxy::Call::proxy and rejects it when the real account has EVM bytecode in pallet_evm::AccountCodes.
2. The same restrictive rule was added to Moonbeam, Moonriver, and Moonbase runtimes.
3. The commit subject and body describe fixing delegation/proxy behavior for contracts.
4. The proxy weight function was updated for the additional database read introduced by the new contract-account filter.

## Missing Evidence

1. No exploit transaction or attacker-controlled scenario is provided.
2. No proof is supplied that proxying through EVM contract accounts caused privilege escalation, fund loss, or state corruption.
3. No included test assertions show the concrete unsafe behavior before the patch.
4. The accounting-or-state-drift and economic-distortion claims are not supported by the shown patch evidence.

## Claim Boundaries

1. Validate only as hardening of proxy dispatch filtering for EVM contract accounts.
2. Do not claim a confirmed vulnerability or concrete exploitability from the supplied evidence.
3. Do not retain the original accounting/state-drift framing.
4. The weight change is supporting accounting for the new lookup, not itself the security-relevant behavior.
