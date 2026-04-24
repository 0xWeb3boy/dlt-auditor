---
case_id: case_20260330_54e640f65d
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: medium
date: 2026-03-30
source_refs:
  - git:54e640f65d70ba7f1fa280c458671b381d687ec7
  - "crates/sui-core/src/authority_server.rs:740"
  - "crates/sui-core/src/authority_server.rs:707"
  - "crates/sui-core/src/authority_server.rs:924"
  - "crates/sui-core/src/authority_server.rs:1028"
bug_class: missing-traffic-control-accounting
impact_type:
  - denial-of-service
  - resource-exhaustion
confidence: high
tags:
  - blockchain-core
  - validator
  - traffic-control
  - gasless-transaction
  - dos-protection
  - spam-accounting
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The validator submit path previously returned zero traffic-control spam weight even when handling gasless transactions. The patch adds request-level spam-weight tracking, sets it to `Weight::one()` for transactions identified by `is_gasless_transaction()`, and returns the computed weight through the observed submit-response paths.

## Observed Patch Facts

1. In `crates/sui-core/src/authority_server.rs`, the patch replaces `let overload_check_res = state.check_system_overload(` with `if transaction`.

2. In `crates/sui-core/src/authority_server.rs`, the patch adds `// Traffic control spam weight to use for the transaction.`.

3. In `crates/sui-core/src/authority_server.rs`, the patch replaces `return Ok((Self::try_from_submit_tx_response(results)?, Weight::zero()));` with `return Ok((Self::try_from_submit_tx_response(results)?, spam_weight));`.

4. In `crates/sui-core/src/authority_server.rs`, the patch replaces `Ok((Self::try_from_submit_tx_response(results)?, Weight::zero()))` with `Ok((Self::try_from_submit_tx_response(results)?, spam_weight))`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `crates/sui-core/src/transaction_orchestrator.rs`, `crates/sui-core/src/transaction_input_loader.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/transaction_orchestrator.rs`, `crates/sui-core/src/transaction_input_loader.rs`. The strongest project-level identifiers around this patch are `Self::try_from_submit_tx_response`, `Weight::zero`, `try_from_submit_tx_response`, and `results`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/submit_transaction_tests.rs`, `crates/sui-core/src/unit_tests/batch_verification_tests.rs`.

## Before/After Behavior

Before the change, the submit path tracked request size but returned `Weight::zero()` on both the no-consensus early return and the normal completion path. The provided snippets do not show any special traffic-control accounting for gasless transactions. After the change, the path initializes `spam_weight`, sets it to `Weight::one()` when a validated transaction is gasless, and returns that computed value instead of a constant zero.

# Root Cause

The submit-transaction path used a fixed zero spam weight for this response path, so gasless transactions were not reflected in the traffic-control weight returned by the handler. The supported root cause is missing DoS/accounting treatment for gasless transactions, not a signature, consensus, serialization, or authorization flaw.

## Walkthrough

1. The submit path initializes per-request state including transaction lists, results, total size, and now `spam_weight`.

2. Each transaction is validity checked before the new gasless-transaction accounting check.

3. The patch checks `transaction.data().transaction_data().is_gasless_transaction()`.

4. For gasless transactions, it assigns `spam_weight = Weight::one()`.

5. The early return for empty `consensus_transactions` now returns the computed `spam_weight`.

6. The normal completion path also returns the computed `spam_weight`.

7. This changes the observed behavior from always returning zero spam weight to returning nonzero weight for gasless transactions.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority_server.rs | 707 | initializes per-request traffic-control spam weight to zero |
| crates/sui-core/src/authority_server.rs | 740 | detects gasless transactions and assigns nonzero traffic-control weight |
| crates/sui-core/src/authority_server.rs | 924 | preserves spam weight on early return when no consensus transactions are submitted |
| crates/sui-core/src/authority_server.rs | 1028 | returns computed spam weight to the caller instead of always returning zero |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/authority_server.rs:740` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
let tx_size = transaction.validity_check(&epoch_store.tx_validity_check_context())?;

            let overload_check_res = state.check_system_overload(
                consensus_adapter,
```
After
```rust
let tx_size = transaction.validity_check(&epoch_store.tx_validity_check_context())?;

            if transaction
                .data()
                .transaction_data()
                .is_gasless_transaction()
            {
                // Gasless transactions count for traffic control, since they have no economic cost.
```

## Snippet 2

Context: `crates/sui-core/src/authority_server.rs:707` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
// Total size of all transactions in the request.
        let mut total_size_bytes = 0;

        let req_type = if is_ping_request {
```
After
```rust
// Total size of all transactions in the request.
        let mut total_size_bytes = 0;
        // Traffic control spam weight to use for the transaction.
        let mut spam_weight = Weight::zero();

        let req_type = if is_ping_request {
```

## Snippet 3

Context: `crates/sui-core/src/authority_server.rs:924` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
if consensus_transactions.is_empty() && !is_ping_request {
            return Ok((Self::try_from_submit_tx_response(results)?, Weight::zero()));
        }
```
After
```rust
if consensus_transactions.is_empty() && !is_ping_request {
            return Ok((Self::try_from_submit_tx_response(results)?, spam_weight));
        }
```

## Snippet 4

Context: `crates/sui-core/src/authority_server.rs:1028` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

        Ok((Self::try_from_submit_tx_response(results)?, Weight::zero()))
    }
```
After
```rust
}

        Ok((Self::try_from_submit_tx_response(results)?, spam_weight))
    }
```

# Fix Pattern

Add explicit traffic-control accounting state for the request, update it when a gasless transaction is observed, and propagate the computed value through all relevant return paths instead of returning a constant zero.

## How It Was Fixed

`authority_server.rs` now initializes `spam_weight` to `Weight::zero()`, detects gasless transactions after validity checking, assigns `Weight::one()` for that case, and replaces the observed `Weight::zero()` return values with `spam_weight`.

# Why It Matters

1. Gasless transactions have no normal sender gas cost in the provided commit description.

2. Zero spam weight would undercount economically free validator submission work.

3. The fix supports DoS-oriented traffic-control accounting.

4. The evidence does not prove a practical network-level DoS exploit or broader protocol compromise.

# Evidence Notes

Grounded evidence comes from `crates/sui-core/src/authority_server.rs` lines 707, 740, 924, and 1028, plus the commit description stating that gasless transactions should be counted in traffic controller because they have no cost to sender. The provided evidence supports a missing traffic-control accounting issue. It does not establish signature-verification bypass, consensus safety impact, unauthorized state changes, economic loss, or a demonstrated exploit. Protocol security invariant: Transactions that impose validator submission work without normal sender gas cost should still contribute nonzero traffic-control spam weight instead of being reported as zero-cost to traffic-control accounting. Verification notes: The patch does not prove a practical network-level DoS exploit. The patch does not show bypass of signature verification or transaction validity checks. The patch does not establish consensus safety impact. The patch does not show economic loss or unauthorized state changes. The provided evidence does not include the regression test details. Regression test details were not provided, only that a test file changed. The caller-side use of returned `Weight` is not shown in the supplied snippets. Confidence is medium because the traffic-control purpose is supported by the commit text and comments, but exploitability is not demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-traffic-control-accounting`
Final impact type: `denial-of-service, resource-exhaustion`
Final confidence: `high`
Final tags: `blockchain-core, validator, traffic-control, gasless-transaction, dos-protection, spam-accounting`

The supplied evidence supports retaining this as security hardening, not as the original serialization/state-consistency finding. The commit explicitly frames the change as DoS protection, the code adds nonzero traffic-control spam weight for gasless transactions, and the comment explains that gasless transactions have no economic cost. The patch does not prove an exploitable DoS incident or broader consensus/state impact, so security-fix is too strong, but the traffic-control accounting change is clearly security-relevant.

## Security Evidence

1. Commit subject says gasless transactions are counted for DoS protection.
2. Commit body says gasless transactions should be counted because they have no cost to the sender.
3. Patch adds `spam_weight` tracking in the validator submit path.
4. Patch sets `spam_weight = Weight::one()` when `is_gasless_transaction()` is true.
5. Return paths now propagate computed spam weight instead of always returning `Weight::zero()`.
6. Inline code comment states gasless transactions count for traffic control because they have no economic cost.

## Missing Evidence

1. No caller-side traffic-controller enforcement logic is shown.
2. No regression test contents are provided.
3. No demonstrated exploit, attack volume, or practical network-level DoS impact is shown.
4. No evidence of signature bypass, consensus safety failure, unauthorized state change, or client-view divergence is shown.

## Claim Boundaries

1. Validate only as DoS-oriented traffic-control hardening/accounting.
2. Do not classify as serialization, state representation, signature, consensus, or RPC client-view divergence.
3. Do not claim proven exploitability or confirmed service outage from the patch alone.
4. Do not claim economic loss or unauthorized transaction execution.
