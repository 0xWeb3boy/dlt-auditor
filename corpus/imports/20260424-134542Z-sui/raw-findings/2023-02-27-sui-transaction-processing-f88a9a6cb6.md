---
case_id: case_20230227_f88a9a6cb6
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2023-02-27
source_refs:
  - git:f88a9a6cb6fa002412f4675312aab79d47ecaa03
  - "crates/sui-adapter/src/execution_engine.rs:546"
  - "crates/sui-adapter/src/execution_engine.rs:641"
  - "crates/sui-adapter/src/execution_engine.rs:885"
  - "crates/sui-types/src/messages.rs:2235"
bug_class: integer-overflow
impact_type:
  - integrity
tags:
  - blockchain-core
  - transaction-processing
  - integer-overflow
  - checked-arithmetic
  - monetary-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Sui pay transaction accounting against u64 overflow when summing coin balances. The strongest supported claim is integer-overflow hardening in coin payment execution, not a proven exploit, denial of service, theft, or consensus failure.

## Observed Patch Facts

1. In `crates/sui-adapter/src/execution_engine.rs`, the patch replaces `ExecutionErrorKind::TotalAmountOverflow,` with `ExecutionErrorKind::TotalPaymentAmountOverflow,`.

2. In `crates/sui-adapter/src/execution_engine.rs`, the patch replaces `// u64 overflow is impossible because the sum of all coin values is bounded by the to...` with `let Some(left_coins) = coins.iter().fold(Some(0u64), |acc, c| acc?.checked_add(c.valu...`.

3. In `crates/sui-adapter/src/execution_engine.rs`, the patch replaces `ExecutionFailureStatus::TotalAmountOverflow` with `ExecutionFailureStatus::TotalPaymentAmountOverflow`.

4. In `crates/sui-types/src/messages.rs`, the patch adds `},`.

## Project Context

The changed code sits primarily in `crates/sui-adapter/src`, `crates/sui-adapter`, `crates/sui-types/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-types/src/coin.rs`, `crates/sui-types/src/error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/coin.rs`, `crates/sui-types/src/error.rs`. The strongest project-level identifiers around this patch are `ExecutionError::new_with_source`, `coins`, `Some`, and `total`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/messages_tests.rs`, `crates/sui-types/src/unit_tests/signature_seed_tests.rs`.

## Before/After Behavior

Before the patch, requested payment amounts were already summed with checked_add, but input coin balances and leftover coin balances were summed with unchecked u64 addition under an assumption that overflow was impossible. After the patch, both input and leftover coin balance totals are accumulated with checked_add and fail with TotalCoinBalanceOverflow when the aggregate cannot fit in u64. Payment amount overflow is separately reported as TotalPaymentAmountOverflow, and display/test coverage was updated for the distinct statuses.

# Root Cause

The code used unchecked u64 addition for aggregate coin-balance accounting in pay-related execution. That relied on a SUI supply-bound assumption even though the commit states overflow may be possible for other coins.

## Walkthrough

1. check_total_coins receives validated coin objects and requested payment amounts for a pay transaction.

2. The requested amount total is accumulated with checked_add; the patch changes its failure status to TotalPaymentAmountOverflow.

3. Before the patch, total input coin balance was computed with plain addition over c.value(), so an aggregate overflow was not handled explicitly.

4. After the patch, total input coin balance uses checked_add and returns TotalCoinBalanceOverflow if accumulation overflows.

5. pay() then debits coins and transfers the requested amounts.

6. Before the patch, the leftover coin total was also computed with unchecked addition before debug-only conservation assertions.

7. After the patch, leftover coin totals are also checked and return TotalCoinBalanceOverflow on overflow.

8. messages.rs and execution_engine.rs tests were updated for the new execution failure statuses and regression coverage.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-adapter/src/execution_engine.rs | 545 | validates total requested payment amount and total input coin balance before pay execution |
| crates/sui-adapter/src/execution_engine.rs | 620 | executes pay transaction and rechecks post-debit coin balance conservation |
| crates/sui-adapter/src/execution_engine.rs | 869 | adds regression coverage for payment amount and coin balance overflow handling |
| crates/sui-types/src/messages.rs | 2229 | exposes distinct execution failure statuses for payment amount overflow and coin balance overflow |

## Code Snippets

## Snippet 1

Context: `crates/sui-adapter/src/execution_engine.rs:546` (changes persisted or aggregate state handling)

Before
```rust
let Some(total_amount) = amounts.iter().fold(Some(0u64), |acc, a| acc?.checked_add(*a)) else {
        return Err(ExecutionError::new_with_source(
            ExecutionErrorKind::TotalAmountOverflow,
            "Attempting to pay a total amount that overflows u64".to_string(),
        ));
    };
    // u64 overflow is impossible because the sum of all coin values is bounded by the total amount
    let total_coins = coins.iter().fold(0, |acc, c| acc + c.value());
```
After
```rust
let Some(total_amount) = amounts.iter().fold(Some(0u64), |acc, a| acc?.checked_add(*a)) else {
        return Err(ExecutionError::new_with_source(
            ExecutionErrorKind::TotalPaymentAmountOverflow,
            "Attempting to pay a total amount that overflows u64".to_string(),
        ));
    };
    let Some(total_coins) = coins.iter().fold(Some(0u64), |acc, c| acc?.checked_add(c.value())) else {
        return Err(ExecutionError::new_with_source(
```

## Snippet 2

Context: `crates/sui-adapter/src/execution_engine.rs:641` (changes persisted or aggregate state handling)

Before
```rust
// double check that we didn't create or destroy money
    // u64 overflow is impossible because the sum of all coin values is bounded by the total amount
    let left_coins = coins.iter().fold(0, |acc, c| acc + c.value());
    debug_assert!(left_coins <= total_coins);
    debug_assert_eq!(total_coins - left_coins, total_amount);
```
After
```rust
// double check that we didn't create or destroy money
    let Some(left_coins) = coins.iter().fold(Some(0u64), |acc, c| acc?.checked_add(c.value())) else {
        return Err(ExecutionError::new_with_source(
            ExecutionErrorKind::TotalCoinBalanceOverflow,
            "Total balance of coins left overflows u64".to_string(),
        ));
    };
```

## Snippet 3

Context: `crates/sui-adapter/src/execution_engine.rs:885` (changes the branch that decides whether execution stops or continues)

Before
```rust
.to_execution_status()
            .0,
        ExecutionFailureStatus::TotalAmountOverflow
    );
}
```
After
```rust
.to_execution_status()
            .0,
        ExecutionFailureStatus::TotalPaymentAmountOverflow
    );
}

#[test]
fn test_pay_coin_overflow() {
```

## Snippet 4

Context: `crates/sui-types/src/messages.rs:2235` (changes persisted or aggregate state handling)

Before
```rust
ExecutionFailureStatus::VMInvariantViolation => {
                write!(f, "MOVE VM INVARIANT VIOLATION.")
            }
        }
    }
```
After
```rust
ExecutionFailureStatus::VMInvariantViolation => {
                write!(f, "MOVE VM INVARIANT VIOLATION.")
            },
            ExecutionFailureStatus::TotalPaymentAmountOverflow => {
                write!(
                    f,
                    "The total amount of coins to be paid overflows of u64"
                )
```

# Fix Pattern

Replace unchecked monetary aggregate arithmetic with checked_add accumulation and return explicit execution errors for unrepresentable totals. Split failure statuses so requested payment amount overflow and aggregate coin balance overflow are distinguishable.

## How It Was Fixed

In crates/sui-adapter/src/execution_engine.rs, the total input coin and leftover coin folds were changed from plain u64 addition to Option<u64> checked_add folds. On overflow, execution returns ExecutionErrorKind::TotalCoinBalanceOverflow. Payment amount overflow is reported as ExecutionErrorKind::TotalPaymentAmountOverflow. crates/sui-types/src/messages.rs adds display handling for the new failure statuses, and tests cover amount overflow and coin-balance overflow.

# Why It Matters

1. Keeps pay transaction balance comparisons from relying on wrapped aggregate totals.

2. Preserves the monetary accounting invariant for non-SUI coin types where the SUI supply-limit assumption may not hold.

3. Turns overflow in payment accounting into an explicit execution failure.

4. Does not prove theft, crash, or consensus divergence from the provided evidence.

# Evidence Notes

Evidence directly supports an integer overflow fix in pay transaction accounting: unchecked folds over coin values were replaced with checked_add, and tests were added for coin overflow. The commit message says SUI itself will not overflow u64::MAX but other coins might. The evidence does not establish remote denial of service, process crash behavior, successful money creation, theft, or consensus divergence, so confidence is medium rather than high. Protocol security invariant: Pay transaction execution must compute requested payment amounts, input coin totals, and leftover coin totals without overflowing the u64 accounting type; unrepresentable aggregates must be rejected before balance comparison or conservation checks are used. Verification notes: The patch does not prove remote denial of service or process crash in release builds. The patch does not prove that SUI coin itself could overflow total balance. The patch does not prove successful money creation or theft before the fix. The patch does not show consensus divergence, only arithmetic handling in pay execution. Reviewed only the provided mapper, draft, commit metadata, and quoted diff evidence. No independent file inspection, command execution, or external context was used. Security classification is limited to likely hardening of a monetary accounting invariant, not a confirmed exploitable vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow`
Final impact type: `integrity`
Final tags: `blockchain-core, transaction-processing, integer-overflow, checked-arithmetic, monetary-accounting`

The supplied patch evidence supports keeping this as security hardening: unchecked u64 addition in pay transaction coin-balance accounting was replaced with checked_add and explicit execution errors. This is a security-sensitive monetary accounting path, but the evidence does not prove an exploitable theft, denial of service, consensus failure, or liveness impact. The original liveness framing is too specific and not supported by the patch alone.

## Security Evidence

1. Pay transaction input coin balances were previously summed with unchecked u64 addition.
2. Leftover coin balances after debit/transfer were also previously summed with unchecked u64 addition.
3. The patch rejects overflowing aggregate coin balances with TotalCoinBalanceOverflow.
4. The commit message states overflow may happen for non-SUI coins despite SUI supply bounds.
5. Regression coverage was added for pay coin overflow behavior.

## Missing Evidence

1. No evidence that an attacker could trigger overflow in production with valid assets.
2. No evidence of theft, money creation, or balance manipulation before the fix.
3. No evidence of process crash, denial of service, liveness failure, or consensus divergence.
4. No details showing whether unchecked overflow wrapped in release builds for this configuration.

## Claim Boundaries

1. Treat as checked-arithmetic hardening for monetary accounting, not a proven exploit fix.
2. Do not claim SUI coin supply itself could overflow u64.
3. Do not claim liveness impact from the supplied evidence.
4. Do not claim successful asset theft or consensus failure.
