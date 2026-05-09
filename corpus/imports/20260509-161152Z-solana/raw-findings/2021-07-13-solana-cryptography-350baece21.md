---
case_id: case_20210713_350baece21
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2021-07-13
source_refs:
  - git:350baece21d8afd5397f6e516c1db61d9afb2916
  - "core/src/cost_model.rs:195"
  - "core/src/cost_tracker.rs:86"
  - "core/src/cost_tracker.rs:102"
  - "core/src/cost_model.rs:320"
bug_class: panic-on-invalid-transaction-index
impact_type:
  - availability-hardening
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - input-validation
  - bounds-check
  - panic-avoidance
  - availability-hardening
  - cost-model
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds bounds checking before `CostModel::find_transaction_cost` indexes `transaction.message().account_keys` with `instruction.program_id_index`. Before the change, an out-of-range program_id_index could cause an invalid index access in the cost-model path. After the change, the function returns `CostModelError::InvalidTransaction`. Related `CostTracker` changes replace string errors with typed `CostModelError` variants but do not show a new resource-limit policy. The change may be availability hardening, but the supplied evidence does not establish exploitability or a concrete security vulnerability.

## Observed Patch Facts

1. In `core/src/cost_model.rs`, the patch replaces `fn find_transaction_cost(&self, transaction: &Transaction) -> u64 {` with `fn find_transaction_cost(&self, transaction: &Transaction) -> Result<u64, CostModelEr...`.

2. In `core/src/cost_tracker.rs`, the patch replaces `fn would_fit(&self, keys: &[Pubkey], cost: &u64) -> Result<(), &'static str> {` with `fn would_fit(&self, keys: &[Pubkey], cost: &u64) -> Result<(), CostModelError> {`.

3. In `core/src/cost_tracker.rs`, the patch replaces `return Err("would exceed account cost limit");` with `return Err(CostModelError::WouldExceedAccountMaxLimit);`.

4. In `core/src/cost_model.rs`, the patch replaces `assert_eq!(expected_cost, testee.find_transaction_cost(&tx));` with `assert_eq!(expected_cost, testee.find_transaction_cost(&tx).unwrap());`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/src/cost_update_service.rs`, `core/src/execute_cost_table.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/validator.rs`, `core/src/tvu.rs`. The strongest project-level identifiers around this patch are `cost`, `CostModelError`, `transaction`, and `CostModelError::WouldExceedAccountMaxLimit`.

## Before/After Behavior

Before the patch, `find_transaction_cost(&self, transaction: &Transaction) -> u64` directly resolved each instruction program id using `transaction.message().account_keys[instruction.program_id_index as usize]`. If the transaction was unsanitized and the index was out of range, the shown code could panic. After the patch, `find_transaction_cost` returns `Result<u64, CostModelError>`, checks the index against `account_keys.len()`, and returns `Err(CostModelError::InvalidTransaction)` before indexing. `CostTracker::would_fit` now returns typed `CostModelError` variants for existing block and account cost-limit failures.

# Root Cause

Transaction cost calculation assumed every instruction's `program_id_index` was valid for the message's `account_keys` array, even though the patched comment states the transaction may not be sanitized at that point.

## Walkthrough

1. Transaction cost calculation iterates over `transaction.message().instructions`.

2. The pre-patch code used `instruction.program_id_index as usize` directly as an index into `transaction.message().account_keys`.

3. The patch adds an explicit bounds check against `transaction.message().account_keys.len()`.

4. If the index is invalid, the function returns `CostModelError::InvalidTransaction` instead of indexing.

5. The return type changes from `u64` to `Result<u64, CostModelError>` so callers can propagate the invalid-transaction condition.

6. Cost tracker errors are converted from string literals to `CostModelError` variants, supporting typed propagation but not changing the shown resource-limit rules.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/cost_model.rs | 195 | Calculates transaction execution cost by iterating instructions and resolving each instruction program id from account_keys; now rejects out-of-range program_id_index before indexing. |
| core/src/cost_tracker.rs | 80 | Attempts to add calculated transaction cost to block/account cost tracking and propagates CostModelError through admission/resource-control logic. |
| core/src/cost_tracker.rs | 86 | Checks block cost and per-account cost limits; error type changed from string literals to CostModelError variants. |
| core/src/cost_model.rs | 320 | Test expectation updated for find_transaction_cost returning Result. |

## Code Snippets

## Snippet 1

Context: `core/src/cost_model.rs:195` (changes a sensitive control or state-update path)

Before
```rust
}

    fn find_transaction_cost(&self, transaction: &Transaction) -> u64 {
        let mut cost: u64 = 0;

        for instruction in &transaction.message().instructions {
            let program_id =
                transaction.message().account_keys[instruction.program_id_index as usize];
```
After
```rust
}

    fn find_transaction_cost(&self, transaction: &Transaction) -> Result<u64, CostModelError> {
        let mut cost: u64 = 0;

        for instruction in &transaction.message().instructions {
            // The Transaction may not be sanitized at this point
            if instruction.program_id_index as usize >= transaction.message().account_keys.len() {
```

## Snippet 2

Context: `core/src/cost_tracker.rs:86` (changes bounds, limits, or capacity handling)

Before
```rust
}

    fn would_fit(&self, keys: &[Pubkey], cost: &u64) -> Result<(), &'static str> {
        // check against the total package cost
        if self.block_cost + cost > self.block_cost_limit {
            return Err("would exceed block cost limit");
        }
```
After
```rust
}

    fn would_fit(&self, keys: &[Pubkey], cost: &u64) -> Result<(), CostModelError> {
        // check against the total package cost
        if self.block_cost + cost > self.block_cost_limit {
            return Err(CostModelError::WouldExceedBlockMaxLimit);
        }
```

## Snippet 3

Context: `core/src/cost_tracker.rs:102` (changes bounds, limits, or capacity handling)

Before
```rust
Some(chained_cost) => {
                    if chained_cost + cost > self.account_cost_limit {
                        return Err("would exceed account cost limit");
                    } else {
                        continue;
```
After
```rust
Some(chained_cost) => {
                    if chained_cost + cost > self.account_cost_limit {
                        return Err(CostModelError::WouldExceedAccountMaxLimit);
                    } else {
                        continue;
```

## Snippet 4

Context: `core/src/cost_model.rs:320` (changes the branch that decides whether execution stops or continues)

Before
```rust
.upsert_instruction_cost(&system_program::id(), program_cost)
            .unwrap();
        assert_eq!(expected_cost, testee.find_transaction_cost(&tx));
    }
```
After
```rust
.upsert_instruction_cost(&system_program::id(), program_cost)
            .unwrap();
        assert_eq!(expected_cost, testee.find_transaction_cost(&tx).unwrap());
    }
```

# Fix Pattern

Validate transaction message indexes before dereferencing message arrays, and convert panic-prone assumptions into typed error returns.

## How It Was Fixed

`find_transaction_cost` was changed to return `Result<u64, CostModelError>`. Before reading `account_keys[instruction.program_id_index as usize]`, it now checks whether the index is within bounds and returns `CostModelError::InvalidTransaction` on failure. `CostTracker::would_fit` was updated to use `CostModelError` variants instead of `&'static str` errors for existing limit checks, and tests were updated to unwrap successful cost calculations.

# Why It Matters

1. Prevents a malformed or unsanitized transaction from causing a panic-prone index operation in cost calculation.

2. Makes invalid transaction handling explicit through a typed error.

3. Keeps existing cost-limit failures distinguishable from invalid transaction errors.

4. Security impact is not proven by the provided evidence.

# Evidence Notes

The strongest evidence is `core/src/cost_model.rs` around line 195, where direct indexing into `transaction.message().account_keys[instruction.program_id_index as usize]` is guarded by a bounds check and `CostModelError::InvalidTransaction`. The comment says the transaction may not be sanitized at this point. `core/src/cost_tracker.rs` shows typed error propagation for cost-limit failures but no new admission policy. The evidence does not prove that attacker-controlled malformed transactions can reach this path, that a validator crash is externally reachable, or that consensus, replay, or signature validation is affected. Protocol security invariant: If transaction cost calculation can receive an unsanitized transaction, each instruction.program_id_index must be checked against message.account_keys before indexing so invalid input is rejected instead of causing a panic. The provided evidence does not establish a cryptographic, replay, signature-validation, consensus-safety, or externally reachable validator-crash invariant. Verification notes: The patch does not show a signature-validation or replay-protection fix. The evidence does not prove malformed transactions can reach this path from the network before sanitization. The evidence does not prove consensus safety impact or state corruption. The cost_tracker changes appear to be typed error propagation, not a new resource-limit policy. Exploitability beyond possible panic avoidance is not established by the provided patch context. Supported: unchecked index panic avoidance in transaction cost calculation. Supported: typed error propagation via `CostModelError`. Not supported: cryptography, replay, or signature-validation bug class. Not supported: proven externally reachable denial of service. Not supported: consensus corruption or state integrity impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `panic-on-invalid-transaction-index`
Final impact type: `availability-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, input-validation, bounds-check, panic-avoidance, availability-hardening, cost-model`

The evidence supports retaining this as security hardening, not as the original cryptography/replay/signature-validation claim. The patch adds an explicit bounds check before indexing transaction account keys with an instruction program_id_index, and the code comment states the transaction may be unsanitized at that point. That converts a panic-prone invalid transaction condition into a typed error. The supplied evidence does not prove external exploitability or a concrete validator denial of service, so this should not be classified as a confirmed security fix.

## Security Evidence

1. Direct unchecked indexing into transaction.message().account_keys was replaced with an index bounds check.
2. The added comment says the Transaction may not be sanitized at this point.
3. Invalid program_id_index now returns CostModelError::InvalidTransaction instead of panicking.
4. The change is in core transaction cost/admission-related code, a security-sensitive availability path.

## Missing Evidence

1. No proof that attacker-controlled malformed transactions can reach this path before sanitization.
2. No demonstrated validator crash, network-triggered denial of service, or exploit scenario.
3. No evidence of cryptography, replay, signature-validation, consensus, or state-integrity impact.
4. CostTracker changes mostly show typed error propagation, not a new resource-control policy.

## Claim Boundaries

1. Classify as availability-oriented hardening through input validation and panic avoidance.
2. Do not retain the original replay-or-signature-validation bug class.
3. Do not claim a confirmed externally reachable denial of service from the supplied patch alone.
4. Do not treat the typed CostTracker error conversion as independently security-relevant.
