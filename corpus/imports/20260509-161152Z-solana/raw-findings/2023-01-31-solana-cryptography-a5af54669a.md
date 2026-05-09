---
case_id: case_20230131_a5af54669a
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2023-01-31
source_refs:
  - git:a5af54669a5e4947ee19e7872f71787d4164ff36
  - "runtime/src/accounts.rs:3800"
  - "runtime/src/accounts.rs:240"
  - "sdk/src/transaction/error.rs:150"
  - "runtime/src/accounts.rs:359"
bug_class: missing-resource-limit
impact_type:
  - resource-exhaustion
tags:
  - infrastructure
  - runtime
  - resource-control
  - transaction-account-loading
  - loaded-account-data-limit
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a feature-gated 64 MiB cap on total loaded account data during Solana transaction account loading and introduces a dedicated transaction error when the cap is exceeded. The evidence supports resource-control hardening in a critical runtime path, but does not establish a concrete exploit, crash, or network denial-of-service scenario.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch adds `#[test]`.

2. In `runtime/src/accounts.rs`, the patch replaces `fn load_transaction_accounts(` with `/// If feature 'cap_transaction_accounts_data_size' is active, total accounts data a`.

3. In `sdk/src/transaction/error.rs`, the patch adds `/// Transaction exceeded max loaded accounts data size cap`.

4. In `runtime/src/accounts.rs`, the patch replaces `if !validated_fee_payer && message.is_non_loader_key(i) {` with `Self::accumulate_and_check_loaded_account_data_size(`.

## Project Context

The changed code sits primarily in `runtime/src`, `sdk/src/transaction`, `sdk/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/read_only_accounts_cache.rs`, `runtime/src/cache_hash_data_stats.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `sdk/src/transaction/sanitized.rs`. The strongest project-level identifiers around this patch are `data`, `accounts`, `TransactionErrorMetrics::default`, and `Self::accumulate_and_check_loaded_account_data_size`.

## Before/After Behavior

Before the patch, the supplied account-loading evidence does not show accumulation or enforcement of a per-transaction loaded-account-data cap, and the transaction error enum had no dedicated cap-exceeded error. After the patch, an active `cap_transaction_accounts_data_size` feature causes a 64 MiB limit to be requested, each loaded account's data length is accumulated during loading, exceeding the limit can abort loading with `MaxLoadedAccountsDataSizeExceeded`, and tests cover the helper behavior.

# Root Cause

The supported root cause is missing transaction-level enforcement of a bounded total loaded account data size in the runtime account-loading path. The evidence does not support claims about cryptography, replay protection, or signature validation.

## Walkthrough

1. `runtime/src/accounts.rs` adds `get_requested_loaded_accounts_data_size_limit(feature_set)` to derive a feature-gated loaded account data limit.

2. The helper returns a nonzero 64 MiB limit only when `cap_transaction_accounts_data_size` is active.

3. During transaction account loading, the patch calls `Self::accumulate_and_check_loaded_account_data_size(...)` with the current accumulator and `account.data().len()`.

4. The `?` operator propagates failure from the cap check, stopping account loading for that transaction when the limit is exceeded.

5. `sdk/src/transaction/error.rs` adds `TransactionError::MaxLoadedAccountsDataSizeExceeded` as the dedicated failure reason.

6. `runtime/src/accounts.rs` adds unit coverage for loaded account data size accumulation and limit behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts.rs | 240 | Defines the feature-gated requested loaded account data size limit of 64 MiB. |
| runtime/src/accounts.rs | 359 | Adds loaded account data length accumulation and cap enforcement during transaction account loading. |
| sdk/src/transaction/error.rs | 150 | Adds the transaction-level error returned when the loaded account data cap is exceeded. |
| runtime/src/accounts.rs | 3800 | Adds tests for loaded account data size accumulation and limit behavior. |

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

Add feature-gated resource accounting in the transaction account-loading path, enforce a fixed upper bound, and return a dedicated transaction error on violation.

## How It Was Fixed

The patch introduces a feature-gated 64 MiB loaded-account-data limit, accumulates each loaded account's data length during account loading, checks the running total against the requested limit, returns `MaxLoadedAccountsDataSizeExceeded` if exceeded, and adds tests for the accumulation/check helper.

# Why It Matters

1. Bounds per-transaction account data loaded before execution.

2. Reduces unbounded resource use in a validator runtime path.

3. Provides a specific transaction error for cap violations.

4. Feature gating means the evidence does not prove universal activation.

5. No supplied evidence proves a concrete exploit or consensus failure.

# Evidence Notes

Primary evidence is from `runtime/src/accounts.rs` lines 240, 359, and 3800, plus `sdk/src/transaction/error.rs` line 150. The bank context places account loading in transaction processing, but the provided snippets do not prove exploitability or network-level denial of service. The heuristic cryptography/replay framing is unsupported and removed. Protocol security invariant: Transaction account loading should enforce a bounded total amount of account data per transaction before execution continues. Verification notes: No evidence in the patch proves signature validation, replay protection, or cryptographic behavior changed. No concrete exploit path, crash primitive, or network-level denial-of-service scenario is demonstrated by the provided evidence. The cap is feature-gated, so the evidence does not prove the behavior is active in all deployments or slots. The patch shows resource hardening; it does not prove prior transactions could exceed validator capacity in practice. Supported: feature-gated 64 MiB loaded account data cap. Supported: cap checked while loading accounts using `account.data().len()`. Supported: dedicated `MaxLoadedAccountsDataSizeExceeded` error added. Unsupported: signature validation, replay protection, or cryptographic behavior changed. Unsupported: confirmed exploitable vulnerability or demonstrated denial-of-service path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-resource-limit`
Final impact type: `resource-exhaustion`
Final tags: `infrastructure, runtime, resource-control, transaction-account-loading, loaded-account-data-limit`

The supplied patch evidence supports retaining this as security hardening: it adds feature-gated accounting and enforcement of a fixed 64 MiB cap on total account data loaded by a transaction in a core runtime transaction-loading path, with a dedicated transaction error when exceeded. The evidence does not support the original cryptography, replay, signature-validation, or request-forgery framing, and it does not prove a concrete exploitable denial-of-service bug.

## Security Evidence

1. Adds feature-gated requested loaded account data size limit of 64 MiB.
2. Accumulates each loaded account's data length during transaction account loading.
3. Propagates an error when accumulated loaded account data exceeds the configured cap.
4. Adds dedicated TransactionError::MaxLoadedAccountsDataSizeExceeded.
5. Adds tests for loaded account data size accumulation and limit behavior.

## Missing Evidence

1. No supplied evidence of a concrete exploit path.
2. No supplied evidence of validator crash, consensus failure, or network-wide denial of service.
3. No supplied evidence that signature validation, replay protection, or cryptographic behavior changed.
4. No supplied evidence that the feature gate was active for all deployments or slots.

## Claim Boundaries

1. Validate only as resource-control hardening in transaction account loading.
2. Do not classify as cryptography, replay, signature, or request-forgery related.
3. Do not claim a confirmed exploitable vulnerability from the supplied patch alone.
4. Do not claim universal runtime enforcement beyond the feature-gated behavior shown.
