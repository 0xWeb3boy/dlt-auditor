---
case_id: case_20230119_b133edf7fd
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-01-19
source_refs:
  - git:b133edf7fdadb397c516084af83730c497e5ecb6
  - "precompiles/randomness/src/lib.rs:96"
  - "precompiles/randomness/src/lib.rs:412"
  - "precompiles/randomness/src/tests.rs:410"
  - "precompiles/randomness/src/tests.rs:461"
bug_class: gas-accounting-hardening
impact_type:
  - resource-accounting
confidence: medium
tags:
  - blockchain-core
  - precompile
  - randomness
  - gas-accounting
  - resource-control
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch improves gas checks in the Moonbeam randomness precompile. It adds checked addition for request gas plus subcall overhead and adds an early fulfillment-side remaining-gas check based on the maximum preparation/finish cost. The evidence supports a correctness/resource-accounting fix, but it does not establish exploitability, consensus impact, node crash, randomness manipulation, or direct fund loss.

## Observed Patch Facts

1. In `precompiles/randomness/src/lib.rs`, the patch replaces `// assert fee > gasLimit * base_fee` with `let request_gas_limit_with_overhead = request_gas_limit`.

2. In `precompiles/randomness/src/lib.rs`, the patch replaces `let pallet_randomness::FulfillArgs {` with `// Since we cannot compute 'prepare_and_finish_fulfillment_cost' now (we don't`.

3. In `precompiles/randomness/src/tests.rs`, the patch replaces `.expect_log(crate::log_fulfillment_failed(Alice));` with `.with_target_gas(Some(total_cost - 1))`.

4. In `precompiles/randomness/src/tests.rs`, the patch replaces `// fulfill request` with `let pallet_randomness::FulfillArgs {`.

## Project Context

The changed code sits primarily in `precompiles/randomness/src`, `precompiles/randomness`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `precompiles/randomness/src/mock.rs`, `precompiles/randomness/src/solidity_types.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/randomness/src/mock.rs`, `precompiles/randomness/src/solidity_types.rs`. The strongest project-level identifiers around this patch are `Runtime`, `revert`, `pallet_randomness::FulfillArgs`, and `pallet_randomness`.

## Before/After Behavior

Before the patch, request-side validation compared gas cost against the request fee using `gas_limit * base_fee`, without the shown explicit checked addition of subcall overhead to the requested gas limit. After the patch, it computes `request_gas_limit + subcall_overhead_gas_costs` with `checked_add` and reverts on overflow. Before the patch, the shown fulfillment path proceeded after converting the request id without the shown early check for preparation/finish gas. After the patch, `fulfill_request` computes a maximum preparation/finish cost using `MaxRandomWords` and reverts if `handle.remaining_gas()` is below that value. Tests were updated to expect insufficient gas to revert before subcall execution, logs, or refund.

# Root Cause

The evidenced issue is incomplete upfront gas/resource accounting in the randomness precompile. The supplied evidence does not prove that this incomplete accounting was security-exploitable.

## Walkthrough

1. A caller interacts with the randomness precompile request or fulfillment path.

2. The request path now includes subcall overhead in a checked gas-limit computation.

3. If the gas-limit-plus-overhead computation overflows, the call reverts.

4. The fulfillment path now computes a conservative maximum preparation/finish gas cost before proceeding.

5. If remaining gas is below that maximum, the call reverts early.

6. The regression test confirms the insufficient-gas case does not perform the subcall, emit logs, or issue a refund.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/randomness/src/lib.rs | 87 | request-side gas and fee validation for randomness provisioning, including checked overhead addition |
| precompiles/randomness/src/lib.rs | 408 | fulfillment entry point enforcing sufficient remaining gas before preparing or performing fulfillment work |
| precompiles/randomness/src/tests.rs | 368 | regression coverage for insufficient fulfillment gas causing revert before subcall, logs, or refund |
| precompiles/randomness/src/tests.rs | 423 | successful fulfillment/refund behavior test updated around prepared randomness words and caller/refund accounting |

## Code Snippets

## Snippet 1

Context: `precompiles/randomness/src/lib.rs:96` (changes bounds, limits, or capacity handling)

Before
```rust
BalanceOf<Runtime>: Into<U256>,
{
	// assert fee > gasLimit * base_fee
	let gas_limit_as_u256: U256 = gas_limit.into();
	let (base_fee, _) = <Runtime as pallet_evm::Config>::FeeCalculator::min_gas_price();
	if let Some(gas_limit_times_base_fee) = gas_limit_as_u256.checked_mul(base_fee) {
		if gas_limit_times_base_fee >= request_fee.into() {
			return Err(revert(
```
After
```rust
BalanceOf<Runtime>: Into<U256>,
{
	let request_gas_limit_with_overhead = request_gas_limit
		.checked_add(subcall_overhead_gas_costs)
		.ok_or(revert(
			"overflow when computing request gas limit + overhead",
		))?;
```

## Snippet 2

Context: `precompiles/randomness/src/lib.rs:412` (changes the branch that decides whether execution stops or continues)

Before
```rust
let request_id = request_id.converted();

		let pallet_randomness::FulfillArgs {
			request,
```
After
```rust
let request_id = request_id.converted();

		// Since we cannot compute `prepare_and_finish_fulfillment_cost` now (we don't
		// know the number of words), we compute the cost for the maximum allowed number of
		// words.
		let max_prepare_and_finish_fulfillment_cost =
			prepare_and_finish_fulfillment_gas_cost::<Runtime>(
				<Runtime as pallet_randomness::Config>::MaxRandomWords::get(),
```

## Snippet 3

Context: `precompiles/randomness/src/tests.rs:410` (changes the branch that decides whether execution stops or continues)

Before
```rust
},
				)
				.expect_log(crate::log_fulfillment_failed(Alice));
		})
}
```
After
```rust
},
				)
				.with_target_gas(Some(total_cost - 1))
				.with_subcall_handle(|_| panic!("should not perform subcall"))
				.expect_no_logs()
				.execute_reverts(|revert| revert == b"not enough gas to perform the call");

			// no refund
```

## Snippet 4

Context: `precompiles/randomness/src/tests.rs:461` (changes the branch that decides whether execution stops or continues)

Before
```rust
filled_results.randomness = Some(H256::default());
			RandomnessResults::<Runtime>::insert(RequestType::Local(3), filled_results);
			// fulfill request
			PrecompilesValue::get()
				.prepare_test(
					Alice,
					Precompile1,
					PCall::fulfill_request {
```
After
```rust
filled_results.randomness = Some(H256::default());
			RandomnessResults::<Runtime>::insert(RequestType::Local(3), filled_results);

			let pallet_randomness::FulfillArgs {
				randomness: random_words,
				..
			} = pallet_randomness::Pallet::<Runtime>::prepare_fulfillment(0)
				.expect("can prepare values");
```

# Fix Pattern

Add conservative upfront resource checks with checked arithmetic, and fail early before downstream execution when gas is insufficient.

## How It Was Fixed

`precompiles/randomness/src/lib.rs` now uses `checked_add` when combining `request_gas_limit` with `subcall_overhead_gas_costs`. The fulfillment entry point now calculates `max_prepare_and_finish_fulfillment_cost` from `MaxRandomWords` and rejects calls with too little remaining gas. Tests were adjusted to cover the early-revert behavior and refund expectations.

# Why It Matters

1. Gas accounting should include overhead as well as requested callback gas.

2. Fulfillment should reject underfunded calls before subcalls or observable side effects.

3. The evidence supports resource-accounting hardening, not a confirmed vulnerability.

# Evidence Notes

Grounded evidence comes from `precompiles/randomness/src/lib.rs` around `ensure_can_provide_randomness` and `fulfill_request`, plus tests in `precompiles/randomness/src/tests.rs`. Unsupported claims removed: malformed-input panic, node crash, consensus failure, randomness manipulation, direct theft, and proven exploitability. Protocol security invariant: Potential resource-accounting invariant: the randomness precompile should account for callback gas, subcall overhead, and fulfillment preparation/finish gas before continuing into fulfillment work. The provided evidence does not establish that violating this invariant created an exploitable security vulnerability. Verification notes: No exploitability is proven by the patch alone. No consensus failure or node crash is shown. No randomness manipulation is shown. No malformed-input panic path is supported by the provided evidence. No direct theft of funds is shown; only gas/fee/refund accounting behavior is evidenced. Patch touches live precompile gas-checking logic, not only tests. Regression evidence shows early revert on insufficient gas. No provided evidence demonstrates an attacker impact beyond incorrect or incomplete gas accounting. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gas-accounting-hardening`
Final impact type: `resource-accounting`
Final confidence: `medium`
Final tags: `blockchain-core, precompile, randomness, gas-accounting, resource-control, security-hardening`

The patch does not prove a concrete exploitable vulnerability, but it clearly tightens gas/resource checks in an externally callable blockchain precompile. It adds checked arithmetic for gas limit plus overhead, rejects insufficient fulfillment gas before subcall execution, and updates tests to confirm no subcall, logs, or refund occur in the under-gas case. This supports retaining it as security hardening rather than a confirmed security fix.

## Security Evidence

1. Adds checked_add when combining request gas limit with subcall overhead and reverts on overflow.
2. Adds an upfront remaining-gas check before fulfillment preparation and downstream execution.
3. Regression test expects under-gas fulfillment to revert before subcall execution, logs, or refund.
4. The changed path is an EVM precompile handling randomness request and fulfillment resource accounting.

## Missing Evidence

1. No proof of a concrete exploit path.
2. No demonstrated consensus failure, node crash, or chain halt.
3. No demonstrated randomness manipulation.
4. No demonstrated direct fund theft or unauthorized state change.
5. No evidence that the prior behavior was externally exploitable beyond incorrect gas accounting.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Impact should be limited to resource accounting and gas-control behavior.
3. Do not claim liveness failure unless additional evidence shows service disruption or stuck requests.
4. Do not claim fund loss, randomness compromise, consensus impact, or denial of service from this patch alone.
