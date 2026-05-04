---
case_id: case_20250915_d526593aff
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2025-09-15
source_refs:
  - git:d526593affe471cfca70bd125288f294d033c288
  - "crates/fuel-core/src/schema/tx.rs:303"
  - "crates/fuel-core/src/schema/message.rs:80"
  - "crates/fuel-core/src/graphql_api.rs:108"
bug_class: graphql-query-complexity-accounting-hardening
impact_type:
  - resource-exhaustion-mitigation
confidence: medium
tags:
  - graphql
  - query-complexity
  - resource-accounting
  - dos-hardening
  - api-resource-control
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects GraphQL complexity formulas for paginated transaction and message queries and raises several default GraphQL cost constants. The evidence supports a query cost-accounting correction in a potentially security-relevant resource-control subsystem, but it does not prove a vulnerability, a limit bypass, or an exploitable DoS condition.

## Observed Patch Facts

1. In `crates/fuel-core/src/schema/tx.rs`, the patch replaces `+ (query_costs().storage_read + first.unwrap_or_default() as usize) * child_complexity \` with `+ first.unwrap_or_default() as usize * (child_complexity + query_costs().storage_read) \`.

2. In `crates/fuel-core/src/schema/message.rs`, the patch replaces `+ (query_costs().storage_read + first.unwrap_or_default() as usize) * child_complexity \` with `+ first.unwrap_or_default() as usize * (child_complexity + query_costs().storage_read) \`.

3. In `crates/fuel-core/src/graphql_api.rs`, the patch replaces `tx_get: 50,` with `tx_get: 200,`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src/schema`, `crates/fuel-core/src`, `crates/fuel-core`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/fuel-core/src/schema/contract.rs`, `crates/fuel-core/src/schema/coins.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/fuel-core/src/schema/contract.rs`, `crates/fuel-core/src/schema/coins.rs`. The strongest project-level identifiers around this patch are `query_costs`, `storage_read`, `unwrap_or_default`, and `usize`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the patch, `transactions_by_owner` and `messages` computed pagination complexity as `storage_iterator + (storage_read + first) * child_complexity + (storage_read + last) * child_complexity`. After the patch, they compute it as `storage_iterator + first * (child_complexity + storage_read) + last * (child_complexity + storage_read)`. The patch also increases default costs for several transaction and block GraphQL fields, including `tx_get`, `tx_status_read`, `tx_raw_payload`, `block_header`, `block_transactions`, and `block_transactions_ids`.

# Root Cause

The root cause shown by the evidence is an incorrect GraphQL complexity calculation for paginated storage-backed fields. The prior formula did not express storage-read cost as a per-requested-entry cost alongside child selection complexity.

## Walkthrough

1. A client can query paginated transaction data through `transactions_by_owner` or paginated message data through `messages`.

2. The schema uses GraphQL complexity annotations to charge estimated query cost.

3. The old formula combined `storage_read` with the pagination argument before multiplying by `child_complexity`.

4. The new formula multiplies each requested `first` or `last` entry by `child_complexity + storage_read`.

5. Default cost constants for some transaction and block fields were also increased.

6. The provided evidence does not show whether the old accounting allowed exceeding configured limits or causing service degradation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/fuel-core/src/schema/tx.rs | 303 | Complexity calculation for transactions_by_owner pagination over transaction storage results. |
| crates/fuel-core/src/schema/message.rs | 80 | Complexity calculation for messages pagination over message storage results. |
| crates/fuel-core/src/graphql_api.rs | 108 | Default GraphQL query cost constants for transaction and block-related fields. |
| tests/tests/dos.rs | 0 | Regression coverage for denial-of-service/query-complexity behavior, referenced as changed but details not provided. |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/schema/tx.rs:303` (changes a sensitive control or state-update path)

Before
```rust
#[graphql(complexity = "{\
        query_costs().storage_iterator\
        + (query_costs().storage_read + first.unwrap_or_default() as usize) * child_complexity \
        + (query_costs().storage_read + last.unwrap_or_default() as usize) * child_complexity\
    }")]
    async fn transactions_by_owner(
```
After
```rust
#[graphql(complexity = "{\
        query_costs().storage_iterator\
        + first.unwrap_or_default() as usize * (child_complexity + query_costs().storage_read) \
        + last.unwrap_or_default() as usize * (child_complexity + query_costs().storage_read) \
    }")]
    async fn transactions_by_owner(
```

## Snippet 2

Context: `crates/fuel-core/src/schema/message.rs:80` (changes a sensitive control or state-update path)

Before
```rust
#[graphql(complexity = "{\
        query_costs().storage_iterator\
        + (query_costs().storage_read + first.unwrap_or_default() as usize) * child_complexity \
        + (query_costs().storage_read + last.unwrap_or_default() as usize) * child_complexity\
    }")]
    async fn messages(
```
After
```rust
#[graphql(complexity = "{\
        query_costs().storage_iterator\
        + first.unwrap_or_default() as usize * (child_complexity + query_costs().storage_read) \
        + last.unwrap_or_default() as usize * (child_complexity + query_costs().storage_read) \
    }")]
    async fn messages(
```

## Snippet 3

Context: `crates/fuel-core/src/graphql_api.rs:108` (changes a sensitive control or state-update path)

Before
```rust
status_change: 40001,
    storage_read: 40,
    tx_get: 50,
    tx_status_read: 50,
    tx_raw_payload: 150,
    block_header: 150,
    block_transactions: 1500,
    block_transactions_ids: 50,
```
After
```rust
status_change: 40001,
    storage_read: 40,
    tx_get: 200,
    tx_status_read: 200,
    tx_raw_payload: 600,
    block_header: 600,
    block_transactions: 6000,
    block_transactions_ids: 200,
```

# Fix Pattern

Correct resource-accounting formulas so per-entry storage work is charged per requested pagination item, and adjust default cost constants for expensive GraphQL fields.

## How It Was Fixed

The complexity annotations in `crates/fuel-core/src/schema/tx.rs` and `crates/fuel-core/src/schema/message.rs` were rewritten to charge `first` and `last` entries for both child complexity and storage-read cost. `crates/fuel-core/src/graphql_api.rs` also raises several default query cost values for transaction and block-related fields.

# Why It Matters

1. GraphQL complexity limits can be part of API resource control.

2. Paginated storage-backed queries should be charged in proportion to requested entries.

3. The affected code is in transaction and message query APIs.

4. The evidence does not establish an exploitable denial-of-service vulnerability.

# Evidence Notes

Grounded evidence consists of the changed complexity annotations in `crates/fuel-core/src/schema/tx.rs` and `crates/fuel-core/src/schema/message.rs`, plus default cost changes in `crates/fuel-core/src/graphql_api.rs`. The commit message describes a complexity calculation bug and charging for additional entries. The evidence does not include the changed `tests/tests/dos.rs` contents, configured query limits, observed runtime impact, or an exploit scenario. Protocol security invariant: GraphQL query complexity accounting should model the backend work for paginated storage-backed fields closely enough that configured query limits reflect actual resource use. The provided evidence shows changes to this accounting, but does not establish that the previous behavior enabled an exploitable resource-consumption issue. Verification notes: No direct exploit path is shown by the provided patch evidence. No proof that an attacker could bypass GraphQL limits is provided. No consensus, transaction execution, or authorization invariant is shown changing. The commit message suggests a charging/calculation bug, not explicitly a vulnerability. The exact before/after behavior depends on configured child_complexity and query complexity limits, which are not fully provided. No direct exploit path is provided. No proof of GraphQL limit bypass is provided. No consensus, authorization, or transaction execution behavior is shown changing. Regression test details are referenced but not included in the evidence. Classified as unclear rather than security-hardening because security impact is plausible but not demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `graphql-query-complexity-accounting-hardening`
Final impact type: `resource-exhaustion-mitigation`
Final confidence: `medium`
Final tags: `graphql, query-complexity, resource-accounting, dos-hardening, api-resource-control`

The supplied patch evidence shows a focused tightening of GraphQL query complexity accounting for paginated storage-backed transaction and message APIs, plus increased default costs for transaction and block fields. This does not prove an exploitable denial-of-service vulnerability, but it clearly adjusts resource-control accounting in a DoS-relevant API surface, so it fits security-hardening rather than a confirmed security-fix.

## Security Evidence

1. Complexity formulas now charge storage_read per requested first/last entry instead of combining storage_read with the pagination count before multiplying by child_complexity.
2. Default GraphQL costs for transaction and block-related fields are increased substantially.
3. The changed files include tests/tests/dos.rs, indicating the project associated this area with denial-of-service/query-cost behavior, though test contents are not provided.
4. The affected endpoints are externally queryable GraphQL transaction and message list APIs backed by storage reads.

## Missing Evidence

1. No exploit scenario or proof of service degradation is provided.
2. No configured query limit values or before/after rejection behavior are shown.
3. The actual tests/tests/dos.rs diff is not included.
4. No advisory, CVE, or explicit security statement is present in the commit metadata.

## Claim Boundaries

1. Validate as security-hardening, not a confirmed security-fix.
2. Do not claim consensus, transaction execution, authorization, or funds impact.
3. Do not claim a proven DoS vulnerability from the supplied evidence alone.
4. The supported claim is limited to tighter GraphQL resource accounting for storage-backed queries.
