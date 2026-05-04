---
case_id: case_20241005_f5adbcfafe
project: fuel-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2024-10-05
source_refs:
  - git:f5adbcfafe4ad502df75ff480855a19726a792bd
  - "crates/fuel-core/src/schema/tx.rs:112"
  - "crates/fuel-core/src/schema/block.rs:319"
  - "crates/fuel-core/src/schema/block.rs:277"
  - "crates/fuel-core/src/schema/tx/types.rs:183"
bug_class: graphql-query-complexity-accounting
impact_type:
  - resource-exhaustion-mitigation
tags:
  - graphql-api
  - query-complexity
  - resource-accounting
  - dos-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch updates GraphQL complexity annotations for block, header, transaction, and transaction-status block resolvers. The evidence supports a likely API resource-accounting hardening for undercharged GraphQL queries, but does not prove a concrete exploit, exhaustion threshold, or consensus-level impact.

## Observed Patch Facts

1. In `crates/fuel-core/src/schema/tx.rs`, the patch replaces `QUERY_COSTS.storage_iterator\` with `// We assume that each block has 100 transactions.`.

2. In `crates/fuel-core/src/schema/block.rs`, the patch replaces `QUERY_COSTS.storage_iterator\` with `(QUERY_COSTS.block_header + child_complexity) \`.

3. In `crates/fuel-core/src/schema/block.rs`, the patch replaces `QUERY_COSTS.storage_iterator\` with `(QUERY_COSTS.block_header + child_complexity) \`.

4. In `crates/fuel-core/src/schema/tx/types.rs`, the patch replaces `#[graphql(complexity = "QUERY_COSTS.storage_read + child_complexity")]` with `#[graphql(complexity = "QUERY_COSTS.block_header + child_complexity")]`.

## Project Context

The changed code sits primarily in `crates/fuel-core/src/schema`, `crates/fuel-core/src`, `crates/fuel-core/src/schema/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/fuel-core/src/schema/message.rs`, `crates/fuel-core/src/schema/contract.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/fuel-core/src/schema/message.rs`, `crates/fuel-core/src/schema/contract.rs`. The strongest project-level identifiers around this patch are `unwrap_or_default`, `usize`, `child_complexity`, and `storage_read`. Nearby tests or test-like files include `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/tx_pool_gas_price_tests.rs`, `crates/fuel-core/src/service/adapters/fuel_gas_price_provider/tests/producer_gas_price_tests.rs`.

## Before/After Behavior

Before the patch, affected paginated resolvers used generic storage iterator/read-style complexity formulas. After the patch, `transactions` charges `QUERY_COSTS.tx_get + child_complexity` per requested item, `headers` and `blocks` charge `QUERY_COSTS.block_header + child_complexity` per requested item, and `SuccessStatus.block` charges `QUERY_COSTS.block_header + child_complexity` instead of `storage_read + child_complexity`.

# Root Cause

GraphQL complexity annotations for some block, header, and transaction-related resolvers used generic storage costs rather than operation-specific per-item costs, potentially undercounting the work implied by paginated API requests.

## Walkthrough

1. A GraphQL caller can request paginated block, header, or transaction fields using `first` and/or `last`.

2. The old annotations used storage iterator/read-style complexity terms for the changed fields.

3. Those formulas did not explicitly charge `block_header` or `tx_get` per requested item.

4. The patch replaces those formulas with per-item operation-specific costs plus selected child-field complexity.

5. This makes the complexity score better track the resolver work for these API paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/fuel-core/src/schema/tx.rs | 112 | GraphQL transactions connection complexity now charges tx_get plus child complexity per requested first/last item. |
| crates/fuel-core/src/schema/block.rs | 319 | GraphQL headers connection complexity now charges block_header plus child complexity per requested first/last item. |
| crates/fuel-core/src/schema/block.rs | 277 | GraphQL blocks connection complexity now charges block_header plus child complexity per requested first/last item. |
| crates/fuel-core/src/schema/tx/types.rs | 183 | Transaction success status block resolver complexity now uses block_header rather than generic storage_read. |

## Code Snippets

## Snippet 1

Context: `crates/fuel-core/src/schema/tx.rs:112` (changes a sensitive control or state-update path)

Before
```rust
}

    #[graphql(complexity = "{\
        QUERY_COSTS.storage_iterator\
        + (QUERY_COSTS.storage_read + first.unwrap_or_default() as usize) * child_complexity \
        + (QUERY_COSTS.storage_read + last.unwrap_or_default() as usize) * child_complexity\
    }")]
    async fn transactions(
```
After
```rust
}

    // We assume that each block has 100 transactions.
    #[graphql(complexity = "{\
        (QUERY_COSTS.tx_get + child_complexity) \
        * (first.unwrap_or_default() as usize + last.unwrap_or_default() as usize)
    }")]
    async fn transactions(
```

## Snippet 2

Context: `crates/fuel-core/src/schema/block.rs:319` (changes a sensitive control or state-update path)

Before
```rust
#[graphql(complexity = "{\
        QUERY_COSTS.storage_iterator\
        + (QUERY_COSTS.storage_read + first.unwrap_or_default() as usize) * child_complexity \
        + (QUERY_COSTS.storage_read + last.unwrap_or_default() as usize) * child_complexity\
    }")]
    async fn headers(
```
After
```rust
#[graphql(complexity = "{\
        (QUERY_COSTS.block_header + child_complexity) \
        * (first.unwrap_or_default() as usize + last.unwrap_or_default() as usize) \
    }")]
    async fn headers(
```

## Snippet 3

Context: `crates/fuel-core/src/schema/block.rs:277` (changes a sensitive control or state-update path)

Before
```rust
#[graphql(complexity = "{\
        QUERY_COSTS.storage_iterator\
        + (QUERY_COSTS.storage_read + first.unwrap_or_default() as usize) * child_complexity \
        + (QUERY_COSTS.storage_read + last.unwrap_or_default() as usize) * child_complexity\
    }")]
    async fn blocks(
```
After
```rust
#[graphql(complexity = "{\
        (QUERY_COSTS.block_header + child_complexity) \
        * (first.unwrap_or_default() as usize + last.unwrap_or_default() as usize) \
    }")]
    async fn blocks(
```

## Snippet 4

Context: `crates/fuel-core/src/schema/tx/types.rs:183` (changes a sensitive control or state-update path)

Before
```rust
}

    #[graphql(complexity = "QUERY_COSTS.storage_read + child_complexity")]
    async fn block(&self, ctx: &Context<'_>) -> async_graphql::Result<Block> {
        let query = ctx.read_view()?;
```
After
```rust
}

    #[graphql(complexity = "QUERY_COSTS.block_header + child_complexity")]
    async fn block(&self, ctx: &Context<'_>) -> async_graphql::Result<Block> {
        let query = ctx.read_view()?;
```

# Fix Pattern

Replace generic GraphQL storage complexity annotations with operation-specific per-item costs for paginated resolver fields.

## How It Was Fixed

The patch changed complexity annotations in `crates/fuel-core/src/schema/tx.rs`, `crates/fuel-core/src/schema/block.rs`, and `crates/fuel-core/src/schema/tx/types.rs`. The file list also shows `tests/tests/dos.rs` was touched, but the supplied evidence does not include the test contents.

# Why It Matters

1. GraphQL complexity limits depend on accurate resolver cost estimates.

2. Paginated public API queries can request many returned items.

3. Undercounting list queries can weaken resource-control protections.

4. The evidence does not show funds-at-risk, authorization bypass, or consensus failure.

# Evidence Notes

The strongest evidence is the direct replacement of `storage_iterator` and `storage_read` complexity formulas with `block_header` or `tx_get` formulas in public GraphQL schema code, plus the commit subject `Fix block query complexity (#2297)`. The touched DoS test file supports but does not prove a DoS vulnerability because its contents are not provided. Exact complexity constants, maximum query complexity settings, and exploit payloads are not included. Protocol security invariant: Public GraphQL query complexity accounting should scale with the requested number of paginated block, header, and transaction items so configured complexity limits can bound resolver work. Verification notes: The patch does not show a consensus, validator, or transaction-execution correctness change. The evidence does not prove a concrete exploit request or measurable node exhaustion by itself. The patch does not show authorization bypass, data corruption, or funds-at-risk behavior. The exact complexity constants and configured maximum query complexity are not provided in the input. Supported: changed code is GraphQL complexity accounting. Supported: affected fields are block/header/transaction query paths. Not supported: consensus, validator, transaction execution, or funds-at-risk impact. Not supported: confirmed exploitability or measurable node exhaustion threshold. Downgraded confidence from high to medium due to missing test body and runtime configuration details. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `graphql-query-complexity-accounting`
Final impact type: `resource-exhaustion-mitigation`
Final tags: `graphql-api, query-complexity, resource-accounting, dos-hardening`

The supplied patch evidence supports retaining this as security hardening, not a confirmed security fix. The code changes adjust async-graphql complexity annotations for public block/header/transaction query paths so paginated requests are charged with operation-specific per-item costs, and the touched file list includes a DoS test. However, the evidence does not show the test body, configured complexity limits, actual cost constants, an exploit query, or measured exhaustion, so the claim should stay bounded to API resource-accounting hardening.

## Security Evidence

1. Patch changes GraphQL complexity annotations on block, headers, transactions, and transaction-status block resolvers.
2. New formulas multiply operation-specific costs such as block_header or tx_get by requested first/last item counts.
3. Affected fields are public query-style API paths where inaccurate complexity accounting can weaken request cost limiting.
4. Commit subject says "Fix block query complexity" and the file list includes tests/tests/dos.rs.

## Missing Evidence

1. No DoS test contents are provided.
2. No maximum query complexity configuration or runtime enforcement details are shown.
3. No concrete exploit query, exhaustion threshold, benchmark, or incident context is supplied.
4. No evidence of consensus, validator, authorization, data integrity, or funds-at-risk impact is shown.

## Claim Boundaries

1. Validate only as GraphQL API resource-accounting hardening.
2. Do not claim a confirmed exploitable DoS from the supplied patch alone.
3. Do not classify as transaction-processing or consensus security impact.
4. Do not infer financial loss, authorization bypass, or chain correctness impact.
