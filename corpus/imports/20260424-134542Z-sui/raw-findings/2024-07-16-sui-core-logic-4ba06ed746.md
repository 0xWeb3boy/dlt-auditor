---
case_id: case_20240716_4ba06ed746
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
source_quality: medium
date: 2024-07-16
source_refs:
  - git:4ba06ed7463743fa46f6b5879b7cd1f4b76da2dc
  - "crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:409"
  - "crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:437"
  - "crates/sui-graphql-rpc/src/server/builder.rs:949"
  - "crates/sui-graphql-rpc/src/server/builder.rs:898"
bug_class: graphql-query-limit-hardening
impact_type:
  - denial-of-service-risk-reduction
confidence: medium
tags:
  - graphql
  - rpc
  - query-limits
  - resource-exhaustion
  - denial-of-service-hardening
  - introspection-bypass-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch rewrites Sui GraphQL query limit accounting and tightens several limit-checking behaviors. The evidence supports a correctness and hardening change in a resource-limit guard, but it does not establish a concrete vulnerability, exploit path, or externally demonstrated denial of service.

## Observed Patch Facts

1. In `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs`, the patch replaces `let cfg = ctx` with `let cfg: &ServiceConfig = ctx.data_unchecked();`.

2. In `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs`, the patch replaces `// TODO: Limit the complexity of fragments early on` with `// If the query is pure introspection, we don't need to check the limits. Pure intros...`.

3. In `crates/sui-graphql-rpc/src/server/builder.rs`, the patch replaces `assert_eq!(` with `assert_eq!(err, vec!["Query has over 0 nodes".to_string()]);`.

4. In `crates/sui-graphql-rpc/src/server/builder.rs`, the patch replaces `assert_eq!(` with `assert_eq!(errs, vec!["Query nesting is over 0".to_string()]);`.

## Project Context

The changed code sits primarily in `crates/sui-graphql-rpc/src/extensions`, `crates/sui-graphql-rpc/src`, `crates/sui-graphql-rpc/src/server`, which anchors the finding in the `core-logic` area of the project. Historical context from `crates/sui-graphql-rpc/src/types/query.rs`, `crates/sui-graphql-rpc/src/server/watermark_task.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-graphql-rpc/src/data/pg.rs`, `crates/sui-graphql-rpc/src/types/type_filter.rs`. The strongest project-level identifiers around this patch are `assert_eq`, `Query`, `to_string`, and `query`.

## Before/After Behavior

Before the change, the commit says the checker counted upward toward limits, had overflow-sensitive multiplication handling, over-approximated paginated connection output, missed some connection fields through fragments, skipped requests that started with a __schema introspection query, and failed to record some metrics after limits were hit. After the change, it counts down from configured budgets, narrows the pure-introspection exemption to a single operation with a single __schema field, improves output-node estimation for connections and fragments, records metrics at limits, and updates tests for node and depth rejection messages.

# Root Cause

The supported root cause is imprecise GraphQL query limit accounting and exemption logic. The provided evidence does not prove that this imprecision was exploitable as a security vulnerability.

## Walkthrough

1. GraphQL requests enter QueryLimitsCheckerExt::parse_query in crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs.

2. The checker reads ServiceConfig limits and rejects payloads larger than max_query_payload_size before parsing.

3. The parsed document is then checked for a narrow pure-introspection shape using DocumentOperations::Single and a single selected field.

4. Only that narrow shape is exempted from the remaining limit checks.

5. The commit description says the rewritten checker uses budget-based accounting, improves paginated connection estimation, detects fragment-obscured connection fields, and records metrics when limits are hit.

6. Tests in crates/sui-graphql-rpc/src/server/builder.rs assert the new rejection messages for zero node and depth limits.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs | 401 | GraphQL parse_query extension entry point that reads service limits, rejects oversized payloads, parses the executable document, and applies query limit checks. |
| crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs | 437 | Pure introspection exemption and rewritten traversal/accounting path for query depth and node limits. |
| crates/sui-graphql-rpc/src/server/builder.rs | 863 | Unit coverage for configured query nesting depth limit rejection. |
| crates/sui-graphql-rpc/src/server/builder.rs | 915 | Unit coverage for configured query node limit rejection. |
| crates/sui-graphql-e2e-tests/tests/limits/output_node_estimation.exp | 1 | End-to-end expected output for GraphQL output node estimation behavior. |
| crates/sui-graphql-e2e-tests/tests/limits/output_node_estimation.move | 1 | End-to-end test fixture for output node estimation behavior. |

## Code Snippets

## Snippet 1

Context: `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:409` (changes the branch that decides whether execution stops or continues)

Before
```rust
let session_id: &SocketAddr = ctx.data_unchecked();
        let metrics: &Metrics = ctx.data_unchecked();
        let instant = Instant::now();
        let cfg = ctx
            .data::<ServiceConfig>()
            .expect("No service config provided in schema data");
        if query.len() > cfg.limits.max_query_payload_size as usize {
            metrics
```
After
```rust
let session_id: &SocketAddr = ctx.data_unchecked();
        let metrics: &Metrics = ctx.data_unchecked();
        let cfg: &ServiceConfig = ctx.data_unchecked();
        let instant = Instant::now();

        if query.len() > cfg.limits.max_query_payload_size as usize {
            metrics
```

## Snippet 2

Context: `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:437` (changes the branch that decides whether execution stops or continues)

Before
```rust
let doc = next.run(ctx, query, variables).await?;

        // TODO: Limit the complexity of fragments early on

        let mut running_costs = ComponentCost {
            depth: 0,
            input_nodes: 0,
            output_nodes: 0,
```
After
```rust
let doc = next.run(ctx, query, variables).await?;

        // If the query is pure introspection, we don't need to check the limits. Pure introspection
        // queries are queries that only have one operation with one field and that field is a
        // `__schema` query
        if let DocumentOperations::Single(op) = &doc.operations {
            if let [field] = &op.node.selection_set.node.items[..] {
                if let Selection::Field(f) = &field.node {
```

## Snippet 3

Context: `crates/sui-graphql-rpc/src/server/builder.rs:949` (changes the branch that decides whether execution stops or continues)

Before
```rust
.map(|e| e.message)
            .collect();
        assert_eq!(
            err,
            vec!["Query has too many nodes 1. The maximum allowed is 0".to_string()]
        );

        let err: Vec<_> = exec_query_node_limit(
```
After
```rust
.map(|e| e.message)
            .collect();
        assert_eq!(err, vec!["Query has over 0 nodes".to_string()]);

        let err: Vec<_> = exec_query_node_limit(
```

## Snippet 4

Context: `crates/sui-graphql-rpc/src/server/builder.rs:898` (changes the branch that decides whether execution stops or continues)

Before
```rust
.collect();

        assert_eq!(
            errs,
            vec!["Query has too many levels of nesting 1. The maximum allowed is 0".to_string()]
        );
        let errs: Vec<_> = exec_query_depth_limit(
            2,
```
After
```rust
.collect();

        assert_eq!(errs, vec!["Query nesting is over 0".to_string()]);
        let errs: Vec<_> = exec_query_depth_limit(
            2,
```

# Fix Pattern

Reimplement resource-limit accounting with explicit budgets, refine GraphQL introspection exemption logic, and improve traversal of GraphQL connection and fragment structures.

## How It Was Fixed

The checker was rewritten to count down from predefined budgets, tighten __schema detection to a single-operation single-field request, estimate paginated output nodes more accurately, detect relevant fields through fragments and inline fragments, and update tests and metrics behavior around limit hits.

# Why It Matters

1. GraphQL query limits are operational safeguards against excessive request work.

2. Overflow-resistant accounting reduces fragility in limit enforcement.

3. A narrower introspection exemption avoids unintended limit skipping.

4. Fragment-aware traversal makes output estimation more complete.

5. The supplied evidence does not prove a security exploit.

# Evidence Notes

Primary evidence is the commit message plus supplied hunks from query_limits_checker.rs and builder.rs. The hunks show the new parse_query structure, the pure-introspection check shape, payload-size handling, and updated limit rejection tests. Claims about old overflow behavior, paginated connection over-estimation, fragment handling, and metrics behavior come from the commit message rather than visible before/after implementation hunks. No authentication, authorization, confidentiality, consensus, state-integrity, or demonstrated denial-of-service impact is shown. Protocol security invariant: No Sui protocol or consensus security invariant is demonstrated. The affected RPC-layer invariant is that GraphQL query parsing should enforce configured payload, depth, and node limits, and should exempt only genuinely pure __schema introspection requests. Verification notes: No concrete exploit path is proven by the provided patch evidence. No authentication, authorization, or data confidentiality failure is shown. No Sui protocol or consensus invariant is shown to be affected. No database corruption or state integrity issue is demonstrated. The evidence supports resource-limit hardening, not confirmed service-wide denial of service. No commands or file inspection were performed. Evidence is limited to the supplied commit metadata, snippets, mapper output, and draft. Classified as unclear because the patch may be security relevant, but the vulnerability thesis is not established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `graphql-query-limit-hardening`
Final impact type: `denial-of-service-risk-reduction`
Final confidence: `medium`
Final tags: `graphql, rpc, query-limits, resource-exhaustion, denial-of-service-hardening, introspection-bypass-hardening`

The evidence supports retaining this as security hardening rather than a confirmed security fix. The commit rewrites GraphQL query limit enforcement, addresses overflow-prone accounting, improves fragment-aware output estimation, and narrows the __schema introspection exemption so a request must be a single pure introspection operation to bypass normal limits. These are security-relevant resource guard improvements, but the supplied evidence does not prove an exploitable denial-of-service vulnerability or concrete attack path.

## Security Evidence

1. GraphQL query depth, node, and payload limits are runtime guards for externally supplied requests.
2. Commit metadata says previous __schema detection skipped requests that merely started with introspection; the new logic requires a single operation with a single __schema field.
3. Commit metadata says accounting changed from counting up with checked multiplication to counting down from a predefined budget to avoid overflow issues.
4. Tests exercise rejection behavior for node and nesting limits under configured zero budgets.

## Missing Evidence

1. No demonstrated exploit query or proof that the old behavior allowed service-wide denial of service.
2. No before/after hunk showing the exact old __schema bypass condition in full.
3. No evidence of authentication, authorization, confidentiality, consensus, or state-integrity impact.
4. No severity, advisory, CVE, or incident context is provided.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Impact should be limited to resource-exhaustion or denial-of-service risk reduction for GraphQL RPC.
3. Do not claim a proven exploitable vulnerability from the supplied evidence.
4. Do not claim blockchain consensus or protocol safety impact.
