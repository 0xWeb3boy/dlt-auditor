---
case_id: case_20250513_ac666695ee
project: moonbeam
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-05-13
source_refs:
  - git:ac666695eecfcd2dff76ff2f5fcdee290512ba1f
  - "runtime/common/src/apis.rs:513"
  - "runtime/common/src/apis.rs:457"
  - "runtime/common/src/apis.rs:338"
  - "runtime/common/Cargo.toml:20"
bug_class: evm-resource-accounting-and-reentrancy-hardening
impact_type:
  - resource-accounting-hardening
  - reentrancy-hardening
confidence: medium
tags:
  - moonbeam
  - evm-runtime-api
  - transaction-processing
  - proof-size-accounting
  - reentrancy-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch replaces manual encoded transaction length estimation in EVM runtime API paths with construction of pallet_ethereum::TransactionData, consistent with the commit subject about proof_size_base_cost. It also enables pallet_ethereum with the forbid-evm-reentrancy feature. The changes may be security relevant, but the provided evidence does not establish a concrete vulnerability, exploitability, accounting bypass, or prior reentrancy issue.

## Observed Patch Facts

1. In `runtime/common/src/apis.rs`, the patch replaces `let mut estimated_transaction_len = data.len() +` with `let transaction_data = pallet_ethereum::TransactionData::new(`.

2. In `runtime/common/src/apis.rs`, the patch replaces `// Estimated encoded transaction size must be based on the heaviest transaction` with `let transaction_data = pallet_ethereum::TransactionData::new(`.

3. In `runtime/common/src/apis.rs`, the patch replaces `let without_base_extrinsic_weight = true;` with `let transaction_data = pallet_ethereum::TransactionData::new(`.

4. In `runtime/common/Cargo.toml`, the patch adds `pallet-ethereum = { workspace = true, features = ["forbid-evm-reentrancy"] }`.

## Project Context

The changed code sits primarily in `runtime/common/src`, `runtime/common`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/common/src/impl_on_charge_evm_transaction.rs`, `runtime/common/src/migrations.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/common/src/migrations.rs`, `runtime/common/src/impl_xcm_evm_runner.rs`. The strongest project-level identifiers around this patch are `transaction`, `pallet`, `workspace`, and `pallet_ethereum::TransactionData::new`.

## Before/After Behavior

Before the change, trace_call, call, and create in runtime/common/src/apis.rs manually estimated encoded transaction length using data.len() plus hard-coded byte counts for transaction fields. After the change, those paths construct pallet_ethereum::TransactionData::new for the relevant transaction action and parameters. runtime/common/Cargo.toml also adds pallet_ethereum with the forbid-evm-reentrancy feature enabled.

# Root Cause

The supported root cause is duplicated transaction-size/accounting logic in runtime/common/src/apis.rs. The prior code manually maintained byte estimates instead of deriving proof-size/base-cost inputs through pallet_ethereum's transaction data representation. The evidence does not prove that this caused undercharging, overcharging, consensus failure, denial of service, or an exploitable vulnerability.

## Walkthrough

1. The affected paths are trace_call, call, and create in runtime/common/src/apis.rs.

2. The old code computed estimated_transaction_len from calldata length and fixed constants for transaction metadata and fee-related fields.

3. The patch removes the shown manual estimation blocks and creates pallet_ethereum::TransactionData values instead.

4. The Cargo.toml change enables the forbid-evm-reentrancy feature on pallet_ethereum.

5. No provided hunk shows the proof_size_base_cost calculation itself, the reentrancy guard implementation, or a failing security regression test.

6. The evidence supports an accounting-correctness or hardening interpretation, but not a confirmed vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/common/src/apis.rs | 317 | trace_call EVM runtime API now builds pallet_ethereum TransactionData instead of relying on manual estimated encoded length and without_base_extrinsic_weight handling |
| runtime/common/src/apis.rs | 437 | call EVM runtime API now builds pallet_ethereum TransactionData for proof-size/base-cost calculation |
| runtime/common/src/apis.rs | 494 | create EVM runtime API now builds pallet_ethereum TransactionData for proof-size/base-cost calculation |
| runtime/common/Cargo.toml | 20 | enables pallet_ethereum dependency with forbid-evm-reentrancy feature |

## Code Snippets

## Snippet 1

Context: `runtime/common/src/apis.rs:513` (changes signature or replay validation logic)

Before
```rust
let validate = true;

					let mut estimated_transaction_len = data.len() +
						// from: 20
						// value: 32
						// gas_limit: 32
						// nonce: 32
						// 1 byte transaction action variant
```
After
```rust
let validate = true;

					let transaction_data = pallet_ethereum::TransactionData::new(
						pallet_ethereum::TransactionAction::Create,
						data.clone(),
						nonce.unwrap_or_default(),
						gas_limit,
						None,
```

## Snippet 2

Context: `runtime/common/src/apis.rs:457` (changes signature or replay validation logic)

Before
```rust
let validate = true;

							// Estimated encoded transaction size must be based on the heaviest transaction
							// type (EIP1559Transaction) to be compatible with all transaction types.
					// TODO: remove, since we will get rid of base_cost
					let mut estimated_transaction_len = data.len() +
						// pallet ethereum index: 1
						// transact call index: 1
```
After
```rust
let validate = true;

					let transaction_data = pallet_ethereum::TransactionData::new(
						pallet_ethereum::TransactionAction::Call(to),
						data.clone(),
						nonce.unwrap_or_default(),
						gas_limit,
						None,
```

## Snippet 3

Context: `runtime/common/src/apis.rs:338` (changes signature or replay validation logic)

Before
```rust
let is_transactional = false;
							let validate = true;
							let without_base_extrinsic_weight = true;


							// Estimated encoded transaction size must be based on the heaviest transaction
							// type (EIP1559Transaction) to be compatible with all transaction types.
							// TODO: remove, since we will get rid of base_cost
```
After
```rust
let is_transactional = false;
							let validate = true;

							let transaction_data = pallet_ethereum::TransactionData::new(
								pallet_ethereum::TransactionAction::Call(to),
								data.clone(),
								nonce.unwrap_or_default(),
								gas_limit,
```

## Snippet 4

Context: `runtime/common/Cargo.toml:20` (changes an authorization or privilege gate)

Before
```text
pallet-conviction-voting = { workspace = true }
pallet-ethereum-xcm = { workspace = true }
pallet-migrations = { workspace = true }
pallet-moonbeam-foreign-assets = { workspace = true }
```
After
```text
pallet-conviction-voting = { workspace = true }
pallet-ethereum-xcm = { workspace = true }
pallet-ethereum = { workspace = true, features = ["forbid-evm-reentrancy"] }
pallet-migrations = { workspace = true }
pallet-moonbeam-foreign-assets = { workspace = true }
```

# Fix Pattern

Replace duplicated manual resource-accounting estimates with a canonical transaction representation from the owning pallet; enable an existing pallet feature for reentrancy prevention.

## How It Was Fixed

runtime/common/src/apis.rs was updated so EVM runtime API paths build pallet_ethereum::TransactionData::new instead of maintaining local encoded-length arithmetic. runtime/common/Cargo.toml was updated to depend on pallet_ethereum with features = ["forbid-evm-reentrancy"].

# Why It Matters

1. Manual byte estimates can drift from actual encoded transaction representation.

2. Proof-size/base-cost calculation affects resource accounting.

3. The changed paths are central EVM runtime API entry points.

4. The reentrancy feature name is security relevant, but the evidence does not show a concrete prior bug.

# Evidence Notes

Evidence is limited to runtime/common/src/apis.rs hunks at lines 317, 437, and 494, plus runtime/common/Cargo.toml line 20 and the commit message. The supplied context does not demonstrate attacker control, fee or block-limit bypass, consensus impact, fund loss, privilege escalation, exact accounting error magnitude, or a specific reentrant execution path. The heuristic baseline's claims about input validation, late validation, cryptographic/replay-sensitive logic, and access-control changes are not supported by the shown code. Protocol security invariant: EVM runtime API call/create/trace paths should calculate proof-size/base-cost inputs consistently with the transaction representation used by pallet_ethereum. The evidence also shows a reentrancy-guard feature was enabled, but it does not show the guard implementation or a prior reentrant path. Verification notes: The patch does not prove that an attacker could bypass fees or block limits before the change. The evidence does not show the implementation details of forbid-evm-reentrancy or a specific reentrant call path. The changed tests listed are not clearly security regression tests from the provided context. The manual length estimation may have been incorrect, but the exact undercharge or overcharge magnitude is not shown. No consensus failure, fund loss, or privilege escalation is demonstrated by the patch alone. Downgraded from likely/security-hardening kept in corpus to unclear/not kept because vulnerability thesis is not established. Kept subsystem as evm-runtime-api because the changed functions are EVM runtime API paths. Kept bug_class as resource-accounting, but with low confidence for security relevance. Removed unsupported claims of validation ordering, exploitability, and concrete reentrancy behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `evm-resource-accounting-and-reentrancy-hardening`
Final impact type: `resource-accounting-hardening, reentrancy-hardening`
Final confidence: `medium`
Final tags: `moonbeam, evm-runtime-api, transaction-processing, proof-size-accounting, reentrancy-hardening`

The patch evidence does not prove a concrete exploitable vulnerability, so it should not be treated as a security-fix. However, it does show security hardening: EVM runtime API paths stop using duplicated manual transaction length estimates for proof_size_base_cost inputs, and the runtime enables pallet_ethereum with the explicitly security-oriented forbid-evm-reentrancy feature. That is enough to retain conservatively as hardening, with narrower claims than the original input-validation framing.

## Security Evidence

1. EVM call/create/trace paths replace hard-coded transaction length accounting with pallet_ethereum::TransactionData::new.
2. Commit subject explicitly ties the change to proof_size_base_cost calculation.
3. Cargo.toml enables pallet_ethereum with feature "forbid-evm-reentrancy".
4. Changed code is in runtime EVM transaction-processing paths.

## Missing Evidence

1. No hunk shows the actual proof_size_base_cost calculation or exact accounting delta.
2. No exploit path, undercharge magnitude, block-limit bypass, or denial-of-service scenario is demonstrated.
3. No reentrancy guard implementation or prior reentrant execution path is shown.
4. Listed tests are not shown to be security regression tests.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed vulnerability fix.
2. Do not claim input validation, access control, cryptographic, or replay protection changes from the shown code.
3. Do not claim fund loss, consensus failure, or exploitable fee bypass.
4. Reentrancy relevance is supported only by enabling the named feature, not by evidence of a specific prior bug.
