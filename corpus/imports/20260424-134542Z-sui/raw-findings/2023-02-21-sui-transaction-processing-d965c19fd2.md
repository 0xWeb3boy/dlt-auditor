---
case_id: case_20230221_d965c19fd2
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2023-02-21
source_refs:
  - git:d965c19fd228b1282278a334bb3e526700ebab3d
  - "crates/sui-adapter/src/execution_engine.rs:541"
  - "crates/sui-adapter/src/execution_engine.rs:850"
  - "crates/sui-adapter/src/execution_engine.rs:634"
  - "crates/sui-types/src/messages.rs:2054"
bug_class: integer-overflow
impact_type:
  - asset-integrity
tags:
  - blockchain-core
  - transaction-processing
  - integer-overflow
  - monetary-validation
  - asset-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes unchecked aggregation of pay transaction recipient amounts. Previously, check_total_coins() summed u64 amounts with amounts.iter().sum() before comparing the result to available coin value. The patch uses checked_add and returns TotalAmountOverflow if the aggregate exceeds u64. This is security-relevant because it protects monetary validation in the pay execution path, but the supplied evidence does not prove an end-to-end theft, minting, consensus, or denial-of-service exploit.

## Observed Patch Facts

1. In `crates/sui-adapter/src/execution_engine.rs`, the patch replaces `let total_amount: u64 = amounts.iter().sum();` with `let Some(total_amount) = amounts.iter().fold(Some(0u64), |acc, a| acc?.checked_add(*a...`.

2. In `crates/sui-adapter/src/execution_engine.rs`, the patch replaces `fn test_pay_insufficient_balance() {` with `fn test_pay_amount_overflow() {`.

3. In `crates/sui-adapter/src/execution_engine.rs`, the patch replaces `debug_assert_eq!(` with `// u64 overflow is impossible because the sum of all coin values is bounded by the to...`.

4. In `crates/sui-types/src/messages.rs`, the patch replaces `ExecutionFailureStatus::EmptyInputCoins => {` with `},`.

## Project Context

The changed code sits primarily in `crates/sui-adapter/src`, `crates/sui-adapter`, `crates/sui-types/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-types/src/gas.rs`, `crates/sui-types/src/object.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/gas.rs`, `crates/sui-types/src/object.rs`. The strongest project-level identifiers around this patch are `SuiAddress::random_for_testing_only`, `coins`, `value`, and `total_amount`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/messages_tests.rs`, `crates/sui-types/src/unit_tests/base_types_tests.rs`.

## Before/After Behavior

Before the patch, overflowing recipient amounts could produce an unchecked u64 aggregate that was then used in the balance comparison. After the patch, overflow while summing requested amounts is rejected as ExecutionErrorKind::TotalAmountOverflow before debiting or transferring coins. A regression test covers amounts [u64::MAX, 100] with insufficient input value, and display text was added for the new failure status.

# Root Cause

The pay validation path used unchecked u64 summation for the requested payment total, so the value used for balance validation was not guaranteed to represent the true aggregate requested amount.

## Walkthrough

1. pay() receives input coin objects, recipients, and per-recipient amounts.

2. pay() validates recipient arity and coin objects, then calls check_total_coins() before transfer execution.

3. Before the fix, check_total_coins() computed total_amount with amounts.iter().sum().

4. The patch changes that aggregation to checked_add over the amounts list.

5. If any addition overflows u64, check_total_coins() returns TotalAmountOverflow instead of continuing.

6. The regression test exercises an overflowing aggregate request.

7. The display layer adds text for the TotalAmountOverflow execution failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-adapter/src/execution_engine.rs | 541 | validates aggregate recipient payment amount and rejects u64 overflow before balance comparison |
| crates/sui-adapter/src/execution_engine.rs | 613 | pay transaction flow depends on checked total amount before debiting coins and asserting conservation |
| crates/sui-adapter/src/execution_engine.rs | 850 | regression test covers overflowing payment amounts |
| crates/sui-types/src/messages.rs | 2054 | surfaces TotalAmountOverflow execution failure status |

## Code Snippets

## Snippet 1

Context: `crates/sui-adapter/src/execution_engine.rs:541` (changes a sensitive control or state-update path)

Before
```rust
fn check_total_coins(coins: &[Coin], amounts: &[u64]) -> Result<(u64, u64), ExecutionError> {
    let total_amount: u64 = amounts.iter().sum();
    let total_coins = coins.iter().fold(0, |acc, c| acc + c.value());
    if total_amount > total_coins {
```
After
```rust
fn check_total_coins(coins: &[Coin], amounts: &[u64]) -> Result<(u64, u64), ExecutionError> {
    let Some(total_amount) = amounts.iter().fold(Some(0u64), |acc, a| acc?.checked_add(*a)) else {
        return Err(ExecutionError::new_with_source(
            ExecutionErrorKind::TotalAmountOverflow,
            "Attempting to pay a total amount that overflows u64".to_string(),
        ));
    };
```

## Snippet 2

Context: `crates/sui-adapter/src/execution_engine.rs:850` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

#[test]
fn test_pay_insufficient_balance() {
```
After
```rust
}

#[test]
fn test_pay_amount_overflow() {
    let coin_objects = vec![Object::new_gas_with_balance_and_owner_for_testing(
        10,
        SuiAddress::random_for_testing_only(),
    )];
```

## Snippet 3

Context: `crates/sui-adapter/src/execution_engine.rs:634` (changes a sensitive control or state-update path)

Before
```rust
// double check that we didn't create or destroy money
    debug_assert_eq!(
        total_coins - coins.iter().fold(0, |acc, c| acc + c.value()),
        total_amount
    );

    // update the input coins to reflect the decrease in value.
```
After
```rust
// double check that we didn't create or destroy money
    // u64 overflow is impossible because the sum of all coin values is bounded by the total amount
    let left_coins = coins.iter().fold(0, |acc, c| acc + c.value());
    debug_assert!(left_coins <= total_coins);
    debug_assert_eq!(total_coins - left_coins, total_amount);

    // update the input coins to reflect the decrease in value.
```

## Snippet 4

Context: `crates/sui-types/src/messages.rs:2054` (changes a sensitive control or state-update path)

Before
```rust
"Coin exceeds maximum value for a single coin"
                )
            }
            ExecutionFailureStatus::EmptyInputCoins => {
                write!(f, "Expected a non-empty list of input Coin objects")
```
After
```rust
"Coin exceeds maximum value for a single coin"
                )
            },
            ExecutionFailureStatus::TotalAmountOverflow => {
                write!(
                    f,
                    "The total amount of coins to be paid is larger than the maximum value of u64"
                )
```

# Fix Pattern

Replace unchecked monetary aggregation with checked accumulation and reject overflow as a validation error before balance comparison or state mutation.

## How It Was Fixed

check_total_coins() now folds amounts with checked_add and returns ExecutionErrorKind::TotalAmountOverflow on overflow. The pay conservation debug check was adjusted to assert left_coins <= total_coins before subtraction. A regression test and failure-status display text were added.

# Why It Matters

1. Prevents balance validation from using an overflowed requested-payment total.

2. Keeps invalid pay requests on an explicit execution-error path.

3. Protects a core coin conservation precondition before debit and transfer logic.

4. Evidence does not establish a complete exploit path or actual fund loss.

# Evidence Notes

Grounded evidence is limited to check_total_coins(), pay(), test_pay_amount_overflow(), and TotalAmountOverflow display text. The evidence supports an integer-overflow validation bug in coin payment execution. It does not support claims of remote crash, consensus acceptance, fund theft, authorization bypass, signature bypass, or serialization issues. Protocol security invariant: A pay transaction must not proceed unless the aggregate of all requested recipient amounts is representable as a u64 and does not exceed the total value of the input coins. Verification notes: No proof is provided that an overflowing pay transaction could be accepted by consensus end to end. No proof is provided of remote node crash, panic, or denial of service from this patch alone. No proof is provided that coins could actually be minted or stolen after the balance-check bypass without inspecting debit_coins_and_transfer behavior. The evidence supports transaction validation hardening/fix, not signature, authorization, or serialization bypass. Reviewed only the provided diff excerpts and draft/mapper claims. Downgraded confidence from high to medium because security impact is plausible but not fully demonstrated. Kept the finding in the security corpus because the changed check guards monetary validation in a transaction execution path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow`
Final impact type: `asset-integrity`
Final tags: `blockchain-core, transaction-processing, integer-overflow, monetary-validation, asset-integrity`

The evidence shows a focused change from unchecked u64 summation of pay recipient amounts to checked_add with an explicit TotalAmountOverflow error before the pay path proceeds. Because this guards coin-payment validation in a blockchain transaction execution path, it is security-relevant hardening. However, the supplied patch does not prove an end-to-end exploitable asset theft, minting, consensus, or denial-of-service issue, so the original security-fix/liveness framing is too strong and partly misleading.

## Security Evidence

1. Unchecked aggregation of payment amounts was replaced with checked addition and explicit overflow rejection.
2. The guarded value is used by check_total_coins before pay() calls debit_coins_and_transfer.
3. A regression test covers an overflowing amount list using u64::MAX plus another value.
4. The new ExecutionFailureStatus::TotalAmountOverflow makes overflow an expected validation failure.

## Missing Evidence

1. No debit_coins_and_transfer implementation evidence proving funds could be stolen or minted.
2. No end-to-end transaction acceptance or consensus impact evidence.
3. No evidence of remote crash, panic, or sustained denial of service.
4. No proof that the overflow was reachable from an untrusted external transaction format beyond the pay path context.

## Claim Boundaries

1. Keep as security-hardening, not a proven security-fix exploit case.
2. Supported claim is unchecked monetary amount aggregation in transaction validation.
3. Do not claim liveness impact from the provided evidence.
4. Do not claim theft, minting, authorization bypass, signature bypass, or consensus failure.
