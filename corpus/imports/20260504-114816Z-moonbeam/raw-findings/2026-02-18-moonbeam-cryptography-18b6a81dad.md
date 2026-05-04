---
case_id: case_20260218_18b6a81dad
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2026-02-18
source_refs:
  - git:18b6a81dad4a5f296bc27a9a5c8c9fcbb9a78f90
  - "precompiles/balances-erc20/src/tests.rs:1140"
  - "precompiles/balances-erc20/src/eip2612.rs:112"
bug_class: permit-deadline-validation
impact_type:
  - expired-authorization-acceptance
  - authorization-bypass
confidence: high
tags:
  - blockchain-core
  - erc20-precompile
  - eip-2612
  - permit
  - deadline-validation
  - authorization
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes an authorization deadline check in the balances ERC20 permit precompile. Previously, the runtime timestamp was divided by 1000 before comparing it to the signed permit deadline, which could allow an expired permit to remain valid for part of the next second. The fix compares the unmodified millisecond timestamp against `deadline * 1000` and rejects overflow during that conversion.

## Observed Patch Facts

1. In `precompiles/balances-erc20/src/tests.rs`, the patch replaces `// This test checks the validity of a metamask signed message against the permit prec...` with `#[test]`.

2. In `precompiles/balances-erc20/src/eip2612.rs`, the patch replaces `let timestamp: U256 = U256::from(timestamp / 1000);` with `let timestamp: U256 = U256::from(timestamp);`.

## Project Context

The changed code sits primarily in `precompiles/balances-erc20/src`, `precompiles/balances-erc20`, which anchors the finding in the `cryptography` area of the project. Historical context from `precompiles/balances-erc20/src/mock.rs`, `precompiles/balances-erc20/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/balances-erc20/src/mock.rs`, `precompiles/balances-erc20/src/lib.rs`. The strongest project-level identifiers around this patch are `U256::from`, `timestamp`, `ExtBuilder::default`, and `into`.

## Before/After Behavior

Before the patch, `timestamp / 1000` was compared to `deadline`, so millisecond precision was lost and a permit could pass shortly after `deadline * 1000ms`. After the patch, the code keeps the timestamp in milliseconds, converts the deadline to milliseconds with `checked_mul(1000)`, rejects conversion overflow, and then applies the expiration check.

# Root Cause

The root cause was inconsistent time-unit handling in the permit expiration guard. The code converted the current millisecond timestamp to seconds using flooring division instead of converting the signed second-based deadline to milliseconds, weakening the expiration boundary.

## Walkthrough

1. A permit includes an owner, spender, value, nonce, and deadline.

2. The precompile reads the runtime timestamp through `<Runtime as pallet_evm::Config>::Timestamp::now()`.

3. The old guard converted the current millisecond timestamp with `timestamp / 1000`.

4. That flooring meant `deadline >= floor(now_ms / 1000)` could still hold after `now_ms` had passed `deadline * 1000`.

5. The fixed guard computes `deadline_ms` with checked multiplication by 1000.

6. The permit is rejected if the converted deadline overflows or if `deadline_ms < timestamp`.

7. A regression test named `permit_expired_deadline_milliseconds` was added for this boundary.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/balances-erc20/src/eip2612.rs | 112 | Permit expiration guard converts signed second-based deadline into milliseconds and rejects expired or overflowing deadlines before nonce and allowance handling. |
| precompiles/balances-erc20/src/tests.rs | 1140 | Regression test for an expired permit deadline at millisecond precision. |
| precompiles/balances-erc20/src/mock.rs | 76 | Test runtime timestamp configuration showing the timestamp unit used by the permit path. |

## Code Snippets

## Snippet 1

Context: `precompiles/balances-erc20/src/tests.rs:1140` (updates aggregate accounting or lifecycle state)

Before
```rust
}

// This test checks the validity of a metamask signed message against the permit precompile
// The code used to generate the signature is the following.
```
After
```rust
}

#[test]
fn permit_expired_deadline_milliseconds() {
	ExtBuilder::default()
		.with_balances(vec![(CryptoAlith.into(), 1000)])
		.build()
		.execute_with(|| {
```

## Snippet 2

Context: `precompiles/balances-erc20/src/eip2612.rs:112` (updates aggregate accounting or lifecycle state)

Before
```rust
let timestamp: u128 =
			<Runtime as pallet_evm::Config>::Timestamp::now().unique_saturated_into();
		let timestamp: U256 = U256::from(timestamp / 1000);

		ensure!(deadline >= timestamp, revert("Permit expired"));

		let nonce = NoncesStorage::<Instance>::get(owner);
```
After
```rust
let timestamp: u128 =
			<Runtime as pallet_evm::Config>::Timestamp::now().unique_saturated_into();
		let timestamp: U256 = U256::from(timestamp);

		let deadline_ms: U256 = deadline
			.checked_mul(U256::from(1000))
			.ok_or_else(|| revert("Deadline overflow"))?;
```

# Fix Pattern

Normalize both sides of an authorization deadline check to the same unit and fail closed on arithmetic overflow.

## How It Was Fixed

The implementation stopped dividing the current timestamp by 1000. It now keeps the timestamp in milliseconds, computes `deadline_ms = deadline.checked_mul(1000)`, returns `Deadline overflow` if conversion fails, and checks `deadline_ms >= timestamp`.

# Why It Matters

1. Expired signed permit authorizations must not remain usable after their deadline.

2. The old flooring behavior extended the acceptance window by up to nearly one second.

3. The evidence supports a bounded deadline-validation issue, not arbitrary token theft or a separate nonce-replay bug.

4. Checked multiplication avoids introducing overflow behavior while fixing the unit mismatch.

# Evidence Notes

The supported evidence is the focused change in `precompiles/balances-erc20/src/eip2612.rs` from `timestamp / 1000` comparison to `deadline.checked_mul(1000)` comparison, plus the new regression test in `precompiles/balances-erc20/src/tests.rs`. The heuristic baseline's accounting or aggregate-state-drift theory is unsupported by the provided diff evidence. Protocol security invariant: The balances ERC20 EIP-2612 permit path must reject a signed authorization once its deadline has expired. Since permit deadlines are second-based while the runtime timestamp is millisecond-based, the comparison must use consistent units without rounding the current time down in a way that extends validity. Verification notes: The patch does not prove arbitrary token theft or balance mutation by itself. The patch does not show a nonce replay bug independent of deadline validation. The demonstrated acceptance window appears limited to timestamp unit rounding, not unbounded permit validity. No exploit transaction, production impact, or attacker preconditions are shown beyond submitting a signed permit near or after its deadline. Implementation evidence directly shows the deadline guard changed. Test evidence directly targets millisecond-precision expiration. No exploit transaction or broader impact beyond expired permit acceptance is shown. No evidence supports classifying this as accounting drift, serialization, migration, or cleanup. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `permit-deadline-validation`
Final impact type: `expired-authorization-acceptance, authorization-bypass`
Final confidence: `high`
Final tags: `blockchain-core, erc20-precompile, eip-2612, permit, deadline-validation, authorization`

The provided patch directly changes an EIP-2612 permit expiration guard from comparing a second-rounded current timestamp to the signed deadline into comparing millisecond-normalized values, with overflow rejection. Because permits are signed authorizations for allowance changes, accepting an expired permit is security relevant. The original accounting/state-drift framing is too broad and misleading; the supported issue is narrowly an authorization deadline validation bug with a bounded timing window.

## Security Evidence

1. The changed code is in the permit path that validates owner, spender, value, nonce, and deadline before allowance handling.
2. Before the patch, current time was floored with timestamp / 1000 before comparison, extending permit validity past the intended deadline boundary.
3. After the patch, the deadline is converted to milliseconds with checked_mul(1000) and compared against the unrounded runtime timestamp.
4. The new regression test is specifically named permit_expired_deadline_milliseconds and targets expired permit behavior.

## Missing Evidence

1. No exploit transaction or demonstrated asset loss is provided.
2. No evidence shows arbitrary token theft, nonce replay, or unbounded permit validity.
3. No production impact or attacker timing feasibility analysis is provided beyond the deadline boundary condition.

## Claim Boundaries

1. Keep the finding limited to expired EIP-2612 permit acceptance caused by inconsistent time units.
2. Do not classify this as accounting drift or general state corruption.
3. The supported impact is a narrowly bounded authorization-window extension, apparently up to less than one second.
4. The overflow check is part of fail-closed hardening for the unit conversion, not separate evidence of an exploited overflow bug.
