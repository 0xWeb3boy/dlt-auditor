---
case_id: case_20231026_89049572df
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-10-26
source_refs:
  - git:89049572df50093a23b84186c3eda5658956c16d
  - "crates/sui-graphql-rpc/src/context_data/db_data_provider.rs:570"
  - "crates/sui-graphql-rpc/src/context_data/db_data_provider.rs:509"
  - "crates/sui-graphql-rpc/src/context_data/db_query_cost.rs:46"
  - "crates/sui-graphql-rpc/src/context_data/db_data_provider.rs:552"
bug_class: resource-control-hardening
impact_type:
  - denial-of-service
confidence: medium
tags:
  - graphql-rpc
  - database-query-costing
  - resource-control
  - denial-of-service-hardening
  - postgresql
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds cost-aware execution for selected Sui GraphQL RPC PostgreSQL-backed data-provider queries and improves SQL placeholder normalization used for cost estimation. The evidence supports a resource-control hardening or implementation improvement, not replay protection, signature validation, consensus safety, authorization, or a proven denial-of-service vulnerability.

## Observed Patch Facts

1. In `crates/sui-graphql-rpc/src/context_data/db_data_provider.rs`, the patch replaces `match epoch_id {` with `let query = match epoch_id {`.

2. In `crates/sui-graphql-rpc/src/context_data/db_data_provider.rs`, the patch adds `/// Takes a query fragment and a lambda that executes the query`.

3. In `crates/sui-graphql-rpc/src/context_data/db_query_cost.rs`, the patch replaces `let re = Regex::new(r"\$(\d+)")` with `// handle limits, as '0' is invalid - set to DEFAULT_PAGE_SIZE instead`.

4. In `crates/sui-graphql-rpc/src/context_data/db_data_provider.rs`, the patch replaces `self.run_query_async(|conn| {` with `self.run_query_async_with_cost(QueryBuilder::get_tx_by_digest(digest), |query| {`.

## Project Context

The changed code sits primarily in `crates/sui-graphql-rpc/src/context_data`, `crates/sui-graphql-rpc/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-graphql-rpc/src/context_data/package_cache.rs`, `crates/sui-graphql-rpc/src/context_data/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-graphql-rpc/src/context_data/package_cache.rs`, `crates/sui-graphql-rpc/src/types/query.rs`. The strongest project-level identifiers around this patch are `query`, `conn`, `Regex::new`, and `crate::error::Error::Internal`.

## Before/After Behavior

Before the patch, observed PgManager lookup methods such as transaction, object, and epoch queries executed through run_query_async directly. After the patch, those paths construct query fragments and pass them through run_query_async_with_cost, which is documented as determining query cost before execution. In db_query_cost.rs, placeholder normalization changed from replacing all bind placeholders generically with '0' to handling LIMIT placeholders with DEFAULT_PAGE_SIZE and adding handling for ANY($N) array-style expressions.

# Root Cause

The grounded pre-patch condition is that selected GraphQL RPC database lookup paths did not use the newly introduced cost-aware wrapper, and SQL normalization for cost extraction treated bind placeholders too generically. The evidence does not prove that this caused an exploitable resource-exhaustion flaw.

## Walkthrough

1. GraphQL RPC data-provider methods reach PgManager lookup functions backed by PostgreSQL queries.

2. Before the patch, the supplied snippets show selected lookups using run_query_async directly.

3. The patch introduces run_query_async_with_cost, described as determining the cost of a query fragment and executing it only if it is within limits.

4. Observed transaction, object, and epoch lookup paths are changed to pass QueryBuilder-generated query fragments into that wrapper.

5. Cost extraction depends on converting Diesel query fragments into SQL-like strings with placeholders normalized.

6. The prior normalization replaced all $N placeholders with '0'.

7. The patched normalization treats LIMIT $N and ANY($N) specially so the cost-estimation SQL shape is more representative.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-graphql-rpc/src/context_data/db_data_provider.rs | 509 | introduces cost-aware async query execution wrapper before running PostgreSQL queries |
| crates/sui-graphql-rpc/src/context_data/db_data_provider.rs | 552 | routes transaction digest lookup through query-cost enforcement |
| crates/sui-graphql-rpc/src/context_data/db_data_provider.rs | 560 | routes object lookup through query-cost enforcement |
| crates/sui-graphql-rpc/src/context_data/db_data_provider.rs | 570 | routes epoch lookup through query-cost enforcement |
| crates/sui-graphql-rpc/src/context_data/db_query_cost.rs | 46 | normalizes generated SQL placeholders for cost estimation, including LIMIT and ANY array handling |

## Code Snippets

## Snippet 1

Context: `crates/sui-graphql-rpc/src/context_data/db_data_provider.rs:570` (changes a consensus- or validator-sensitive branch)

Before
```rust
pub async fn get_epoch(&self, epoch_id: Option<i64>) -> Result<Option<StoredEpochInfo>, Error> {
        match epoch_id {
            Some(epoch_id) => {
                self.run_query_async(move |conn| {
                    QueryBuilder::get_epoch(epoch_id)
                        .get_result::<StoredEpochInfo>(conn)
                        .optional()
```
After
```rust
pub async fn get_epoch(&self, epoch_id: Option<i64>) -> Result<Option<StoredEpochInfo>, Error> {
        let query = match epoch_id {
            Some(epoch_id) => QueryBuilder::get_epoch(epoch_id),
            None => QueryBuilder::get_latest_epoch(),
        };

        self.run_query_async_with_cost(query, |query| {
```

## Snippet 2

Context: `crates/sui-graphql-rpc/src/context_data/db_data_provider.rs:509` (changes a sensitive control or state-update path)

Before
```rust
.map_err(|e| Error::Internal(e.to_string()))
    }
}
```
After
```rust
.map_err(|e| Error::Internal(e.to_string()))
    }

    /// Takes a query fragment and a lambda that executes the query
    /// Spawns a blocking task that determines the cost of the query fragment
    /// And if within limits, executes the query
    async fn run_query_async_with_cost<T, Q, EF, E, F>(
        &self,
```

## Snippet 3

Context: `crates/sui-graphql-rpc/src/context_data/db_query_cost.rs:46` (changes bounds, limits, or capacity handling)

Before
```rust
let sql: String = query_builder.finish();

    let re = Regex::new(r"\$(\d+)")
        .map_err(|e| crate::error::Error::Internal(format!("Failed create valid regex: {}", e)))?;
    Ok(re.replace_all(&sql, "'0'").to_string())
}

pub fn extract_cost(
```
After
```rust
let sql: String = query_builder.finish();

    // handle limits, as '0' is invalid - set to DEFAULT_PAGE_SIZE instead
    let re = Regex::new(r"(LIMIT\s+)\$(\d+)")
        .map_err(|e| crate::error::Error::Internal(format!("Failed create valid regex: {}", e)))?;
    let replacement_string = format!("LIMIT {}", DEFAULT_PAGE_SIZE);
    let output = re
        .replace_all(&sql, replacement_string.as_str())
```

## Snippet 4

Context: `crates/sui-graphql-rpc/src/context_data/db_data_provider.rs:552` (changes a sensitive control or state-update path)

Before
```rust
impl PgManager {
    async fn get_tx(&self, digest: Vec<u8>) -> Result<Option<StoredTransaction>, Error> {
        self.run_query_async(|conn| {
            QueryBuilder::get_tx_by_digest(digest)
                .get_result::<StoredTransaction>(conn) // Expect exactly 0 to 1 result
                .optional()
        })
        .await
```
After
```rust
impl PgManager {
    async fn get_tx(&self, digest: Vec<u8>) -> Result<Option<StoredTransaction>, Error> {
        self.run_query_async_with_cost(QueryBuilder::get_tx_by_digest(digest), |query| {
            move |conn| query.get_result::<StoredTransaction>(conn).optional()
        })
        .await
```

# Fix Pattern

Route selected database-backed GraphQL RPC queries through a centralized cost-aware execution wrapper and make SQL placeholder normalization more context-sensitive for cost estimation.

## How It Was Fixed

The patch adds run_query_async_with_cost in db_data_provider.rs and updates observed PgManager lookup methods to use it instead of direct run_query_async execution. It also changes raw_sql_string_values_set in db_query_cost.rs so LIMIT placeholders are rewritten using DEFAULT_PAGE_SIZE and ANY($N) expressions receive separate handling.

# Why It Matters

1. Resource limits can reduce unexpectedly expensive database work.

2. Cost estimation is more useful when placeholder normalization preserves important SQL structure.

3. The evidence supports hardening, but not a confirmed vulnerability.

# Evidence Notes

Evidence is limited to snippets from crates/sui-graphql-rpc/src/context_data/db_data_provider.rs and crates/sui-graphql-rpc/src/context_data/db_query_cost.rs. The supplied material does not show exploitability, attacker control, configured thresholds, complete coverage of GraphQL query paths, or any authentication, authorization, replay, signature-validation, consensus, or validator-safety behavior. Protocol security invariant: GraphQL RPC database-backed queries may need resource-budget checks before execution, but the provided evidence only shows added query-costing and SQL normalization support. It does not establish a violated protocol security invariant or a concrete vulnerability. Verification notes: No evidence of replay protection or signature-validation behavior is changed. No evidence that consensus or validator logic is affected despite heuristic labels. No proof that a remote denial-of-service exploit was possible before the patch. No proof that all GraphQL query paths are covered by the new costing wrapper. No evidence of authorization, authentication, or state-transition integrity changes. Classified as unclear rather than likely because the vulnerability thesis is not established. Downgraded keep_in_security_corpus to false under the instruction for potentially security-relevant but unproven patches. Rejected the heuristic transaction-processing and replay/signature-validation framing as unsupported. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-control-hardening`
Final impact type: `denial-of-service`
Final confidence: `medium`
Final tags: `graphql-rpc, database-query-costing, resource-control, denial-of-service-hardening, postgresql`

The supplied patch evidence supports retaining this as security hardening, not as a confirmed security fix. The change routes exposed GraphQL RPC PostgreSQL-backed lookup paths through a query-cost wrapper that only executes queries within limits and improves SQL placeholder normalization used for cost estimation. That is a clear resource-control tightening on an RPC/database path, but the evidence does not prove a concrete exploitable denial-of-service vulnerability or any replay, signature-validation, consensus, or validator-safety issue.

## Security Evidence

1. Adds run_query_async_with_cost, documented as determining query cost before execution and executing only if within limits.
2. Routes transaction, object, and epoch database lookup paths through the new cost-aware execution wrapper.
3. Updates SQL normalization for cost estimation, including LIMIT placeholders and ANY($N) array expressions.
4. Changed subsystem is GraphQL RPC backed by PostgreSQL queries, an externally reachable resource-consumption surface.

## Missing Evidence

1. No exploit scenario or attacker-controlled query example is shown.
2. No pre-patch query cost bypass, threshold configuration, or expensive query proof is supplied.
3. No evidence shows authentication, authorization, replay protection, signature validation, consensus, or validator state-transition behavior.
4. No evidence proves full coverage of all GraphQL query paths.

## Claim Boundaries

1. Classify as resource-control hardening only, not a confirmed vulnerability fix.
2. Do not retain the original replay-or-signature-validation classification.
3. Do not claim consensus or validator safety impact from the supplied evidence.
4. Do not claim proven denial-of-service exploitability; only DoS-oriented hardening is supported.
