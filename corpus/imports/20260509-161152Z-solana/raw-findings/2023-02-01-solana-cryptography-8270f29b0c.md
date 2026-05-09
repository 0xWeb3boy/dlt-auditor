---
case_id: case_20230201_8270f29b0c
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2023-02-01
source_refs:
  - git:8270f29b0ce35d5b2c5e21c4e0d4f247ffd67b90
  - "runtime/src/accounts.rs:3800"
  - "runtime/src/accounts.rs:240"
  - "sdk/src/transaction/error.rs:150"
  - "runtime/src/accounts.rs:359"
bug_class: missing-resource-limit
impact_type:
  - denial-of-service
  - resource-exhaustion
confidence: medium
tags:
  - runtime
  - account-loading
  - resource-limit
  - denial-of-service
  - feature-gated
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a feature-gated cap on total loaded account data during Solana transaction account loading. The evidence supports resource-consumption hardening in the runtime account-loading path, not cryptography, replay, signature validation, consensus divergence, or proven exploitability.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch adds `#[test]`.

2. In `runtime/src/accounts.rs`, the patch replaces `fn load_transaction_accounts(` with `/// If feature 'cap_transaction_accounts_data_size' is active, total accounts data a`.

3. In `sdk/src/transaction/error.rs`, the patch adds `/// Transaction exceeded max loaded accounts data size cap`.

4. In `runtime/src/accounts.rs`, the patch replaces `if !validated_fee_payer && message.is_non_loader_key(i) {` with `Self::accumulate_and_check_loaded_account_data_size(`.

## Project Context

The changed code sits primarily in `runtime/src`, `sdk/src/transaction`, `sdk/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/read_only_accounts_cache.rs`, `runtime/src/cache_hash_data_stats.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `sdk/src/transaction/sanitized.rs`. The strongest project-level identifiers around this patch are `data`, `accounts`, `TransactionErrorMetrics::default`, and `Self::accumulate_and_check_loaded_account_data_size`.

## Before/After Behavior

Before the patch, the provided snippets do not show an accumulated transaction-level loaded-account-data-size check in `Accounts::load_transaction_accounts`, and the SDK transaction error enum had no specific error for exceeding such a cap. After the patch, `get_requested_loaded_accounts_data_size_limit` returns a 64 MiB limit when `cap_transaction_accounts_data_size` is active, each loaded account contributes `account.data().len()` to an accumulated total, exceeding the limit aborts loading via `?`, and `TransactionError::MaxLoadedAccountsDataSizeExceeded` records the rejection reason.

# Root Cause

The account-loading path lacked the newly added explicit accumulated loaded-account-data cap in the provided evidence. This is best characterized as missing or incomplete resource-limit enforcement, not a demonstrated cryptographic or replay-validation flaw.

## Walkthrough

1. A verified transaction reaches the runtime path that loads accounts before execution.

2. The patch defines `Accounts::get_requested_loaded_accounts_data_size_limit`, which returns a 64 MiB nonzero limit only when the feature gate is active.

3. During `Accounts::load_transaction_accounts`, the runtime obtains each loaded account's `account.data().len()`.

4. The loaded data length is added to `accumulated_accounts_data_size` through `Self::accumulate_and_check_loaded_account_data_size`.

5. If the accumulated size exceeds the requested cap, account loading returns an error and stops.

6. The SDK adds `TransactionError::MaxLoadedAccountsDataSizeExceeded` to represent that rejection.

7. Tests are added for the accumulation and cap-check behavior, including disabled-limit behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts.rs | 240 | defines the feature-gated 64 MiB loaded account data limit |
| runtime/src/accounts.rs | 359 | checks accumulated loaded account data while loading transaction accounts |
| sdk/src/transaction/error.rs | 150 | adds the rejection error for exceeding the loaded account data cap |
| runtime/src/accounts.rs | 3800 | adds tests for accumulated loaded account data size enforcement |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts.rs:3800` (changes the branch that decides whether execution stops or continues)

Before
```rust
}
    }
}
```
After
```rust
}
    }

    #[test]
    fn test_accumulate_and_check_loaded_account_data_size() {
        let mut error_counter = TransactionErrorMetrics::default();

        // assert check is OK if data limit is not enabled
```

## Snippet 2

Context: `runtime/src/accounts.rs:240` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    fn load_transaction_accounts(
        &self,
```
After
```rust
}

    /// If feature `cap_transaction_accounts_data_size` is active, total accounts data a
    /// transaction can load is limited to 64MiB to not break anyone in Mainnet-beta today.
    /// (It will be set by compute_budget instruction in the future to more reasonable level).
    fn get_requested_loaded_accounts_data_size_limit(
        feature_set: &FeatureSet,
    ) -> Option<NonZeroUsize> {
```

## Snippet 3

Context: `sdk/src/transaction/error.rs:150` (changes a sensitive control or state-update path)

Before
```rust
)]
    InsufficientFundsForRent { account_index: u8 },
}
```
After
```rust
)]
    InsufficientFundsForRent { account_index: u8 },

    /// Transaction exceeded max loaded accounts data size cap
    #[error("Transaction exceeded max loaded accounts data size cap")]
    MaxLoadedAccountsDataSizeExceeded,
}
```

## Snippet 4

Context: `runtime/src/accounts.rs:359` (changes a sensitive control or state-update path)

Before
```rust
})
                    };

                    if !validated_fee_payer && message.is_non_loader_key(i) {
```
After
```rust
})
                    };
                    Self::accumulate_and_check_loaded_account_data_size(
                        &mut accumulated_accounts_data_size,
                        account.data().len(),
                        requested_loaded_accounts_data_size_limit,
                        error_counters,
                    )?;
```

# Fix Pattern

Add a feature-gated runtime resource budget, account for usage while loading transaction accounts, and reject transactions that exceed the budget with a dedicated error.

## How It Was Fixed

The patch adds a 64 MiB feature-gated loaded-account-data limit, wires the limit into transaction account loading, accumulates each loaded account's data length, returns `MaxLoadedAccountsDataSizeExceeded` on cap violation, and adds tests for the helper behavior.

# Why It Matters

1. Limits runtime work and memory exposure during transaction account loading.

2. Rejects oversized loaded-account-data transactions before deeper execution.

3. Makes the rejection reason explicit and observable.

4. Does not establish crashability, remote exploitability, replay risk, signature bypass, or consensus failure.

# Evidence Notes

Grounded evidence is limited to `runtime/src/accounts.rs` lines 240, 359, and 3800, plus `sdk/src/transaction/error.rs` line 150. The heuristic baseline's cryptography and replay interpretation is unsupported. The evidence supports runtime resource hardening, but because no concrete attack path, crash condition, or cluster activation status is shown, confidence is downgraded from high to medium. Protocol security invariant: When the `cap_transaction_accounts_data_size` feature is active, a transaction must not cause the runtime account-loading path to load more than the configured total account data cap before execution; exceeding the cap rejects the transaction with `MaxLoadedAccountsDataSizeExceeded`. Verification notes: Does not show signature validation, replay protection, or cryptographic behavior changing. Does not prove remote exploitability or validator crash conditions. Does not show whether the cap is active on all clusters because enforcement is feature-gated. Does not prove consensus divergence; it shows resource-limit rejection behavior. No external context was used. No claim is made that the bug was exploitable in practice. No claim is made that all clusters had the feature active. No claim is made about signature validation, replay protection, or consensus divergence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-resource-limit`
Final impact type: `denial-of-service, resource-exhaustion`
Final confidence: `medium`
Final tags: `runtime, account-loading, resource-limit, denial-of-service, feature-gated`

The supplied patch evidence supports a security-hardening interpretation, but not the original cryptography/replay classification. The change adds a feature-gated 64 MiB cap on total account data loaded by a transaction, accumulates each loaded account's data size during runtime account loading, and rejects transactions that exceed the cap with a dedicated error. This is best kept as resource-exhaustion or denial-of-service hardening, not as a proven exploitable security fix.

## Security Evidence

1. Adds a transaction-level cap for loaded account data when the feature gate is active.
2. Checks accumulated loaded account data size inside the runtime account-loading path.
3. Returns a dedicated MaxLoadedAccountsDataSizeExceeded transaction error on cap violation.
4. Tests cover the accumulation and cap-check behavior.

## Missing Evidence

1. No evidence of cryptography, signature validation, or replay behavior changing.
2. No concrete exploit path, validator crash, or demonstrated denial-of-service is shown.
3. No evidence that the feature gate was active on all deployed clusters at the time.
4. No consensus-divergence or remote exploitability proof is provided.

## Claim Boundaries

1. Classify as resource-limit hardening only.
2. Do not claim a replay, signature, or cryptographic validation flaw.
3. Do not claim confirmed exploitability from the patch alone.
4. Do not claim universal enforcement outside the feature-gated behavior shown.
