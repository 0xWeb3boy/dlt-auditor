---
case_id: case_20240831_fdc8325abf
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: resource-exhaustion
confidence: medium
source_quality: medium
date: 2024-08-31
source_refs:
  - git:fdc8325abfd62013c83fdee06034609ae60f4c7c
  - "crates/sui-graphql-rpc/src/server/builder.rs:1102"
  - "crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:540"
  - "crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:441"
  - "crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:172"
impact_type:
  - potential-remote-dos
tags:
  - graphql-rpc
  - payload-size-limit
  - transaction-payload
  - resource-exhaustion
  - availability-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best characterized as GraphQL RPC availability hardening for oversized transaction-bearing requests. The commit text states that mutation and dry-run transaction payloads can be much larger than ordinary query payloads and adds a max_tx_payload_size derived from protocol max_tx_bytes with Base64 overhead. The visible code evidence supports a dedicated transaction payload limit error path in query_limits_checker.rs and test support for limit-error assertions. The evidence does not establish a proven exploit, outage, consensus impact, transaction validity bypass, or state corruption.

## Observed Patch Facts

1. In `crates/sui-graphql-rpc/src/server/builder.rs`, the patch adds `/// Execute a GraphQL request with 'limits' in place, expecting an error to be returned.`.

2. In `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs`, the patch replaces `/// Error returned if output node estimate exceeds limit. Also sets the output budget...` with `/// Error returned if transaction payloads exceed limit. Also sets the transaction pa...`.

3. In `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs`, the patch replaces `let def = self.fragments.get(name).ok_or_else(|| {` with `let def = self`.

4. In `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs`, the patch replaces `return Err(graphql_error_at_pos(` with `return Err(self.reporter.graphql_error_at_pos(`.

## Project Context

The changed code sits primarily in `crates/sui-graphql-rpc/src/server`, `crates/sui-graphql-rpc/src`, `crates/sui-graphql-rpc/src/extensions`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-graphql-rpc/src/extensions/timeout.rs`, `crates/sui-graphql-rpc/src/extensions/directive_checker.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-graphql-rpc/src/types/transaction_block/mod.rs`, `crates/sui-graphql-rpc/src/types/suins_registration.rs`. The strongest project-level identifiers around this patch are `name`, `limits`, `returned`, and `reqwest::StatusCode::GATEWAY_TIMEOUT`.

## Before/After Behavior

Before the patch, the provided snippets show generic GraphQL input and output/query limit traversal, including query depth, node count, selection, and fragment handling. The provided before-state does not show a dedicated transaction payload budget for transaction bytes embedded in mutations or dry-run queries. After the patch, query_limits_checker.rs includes tx_payload_size_error, which reports Transaction payload too large and sets tx_payload_budget to zero after an oversized transaction payload is detected. The commit text states that executeTransactionBlock txBytes plus signatures and dryRunTransactionBlock txBytes are checked against max_tx_payload_size, and that overall query size is checked against max_tx_payload_size plus max_query_payload_size.

# Root Cause

The supported root cause is insufficiently specific payload-size accounting for GraphQL operations that include transaction material. Generic query-size or node-count limits did not directly model the larger transaction byte payloads allowed by mutations or dry-run transaction queries.

## Walkthrough

1. A GraphQL request is processed with configured service limits.

2. Existing traversal enforces generic input limits such as maximum query depth and node count.

3. Existing output traversal walks fields and fragments to apply output/query limits.

4. The patch adds a transaction payload budget distinct from ordinary query payload accounting, according to the commit description.

5. For transaction-bearing operations, transaction bytes and signatures are intended to be charged against max_tx_payload_size.

6. If the transaction payload budget is exceeded, tx_payload_size_error reports Transaction payload too large.

7. That error path also sets tx_payload_budget to zero so the request cannot later succeed on smaller transaction arguments after an oversized one has failed.

8. A test helper in server/builder.rs supports executing requests under configured limits and collecting expected errors.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs | 540 | Adds transaction payload limit failure handling and spends the tx payload budget after an oversized payload is detected. |
| crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs | 151 | Runs request input limit traversal for GraphQL operations, part of the request budget enforcement path. |
| crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs | 395 | Traverses selections and fragments while applying output/query limit checks in the GraphQL limits extension. |
| crates/sui-graphql-rpc/src/server/builder.rs | 1102 | Adds test helper coverage for executing GraphQL requests under configured limits and expecting limit errors. |

## Code Snippets

## Snippet 1

Context: `crates/sui-graphql-rpc/src/server/builder.rs:1102` (changes the branch that decides whether execution stops or continues)

Before
```rust
assert_eq!(resp.status(), reqwest::StatusCode::GATEWAY_TIMEOUT);
    }
}
```
After
```rust
assert_eq!(resp.status(), reqwest::StatusCode::GATEWAY_TIMEOUT);
    }

    /// Execute a GraphQL request with `limits` in place, expecting an error to be returned.
    /// Returns the list of errors returned.
    async fn execute_for_error(limits: Limits, request: Request) -> String {
        let service_config = ServiceConfig {
            limits,
```

## Snippet 2

Context: `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:540` (changes a sensitive control or state-update path)

Before
```rust
}

    /// Error returned if output node estimate exceeds limit. Also sets the output budget to zero,
    /// to indicate that it has been spent (This is done because unlike other budgets, the output
```
After
```rust
}

    /// Error returned if transaction payloads exceed limit. Also sets the transaction payload
    /// budget to zero to indicate it has been spent (This is done to prevent future checks for
    /// smaller arguments from succeeding even though a previous larger argument has already
    /// failed).
    fn tx_payload_size_error(&mut self) -> ServerError {
        self.tx_payload_budget = 0;
```

## Snippet 3

Context: `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:441` (changes a sensitive control or state-update path)

Before
```rust
Selection::FragmentSpread(fs) => {
                let name = &fs.node.fragment_name.node;
                let def = self.fragments.get(name).ok_or_else(|| {
                    graphql_error_at_pos(
                        code::INTERNAL_SERVER_ERROR,
                        format!("Fragment {name} referred to but not found in document"),
                        fs.pos,
                    )
```
After
```rust
Selection::FragmentSpread(fs) => {
                let name = &fs.node.fragment_name.node;
                let def = self
                    .fragments
                    .get(name)
                    .ok_or_else(|| self.reporter.fragment_not_found_error(name, fs.pos))?;

                for selection in &def.node.selection_set.node.items {
```

## Snippet 4

Context: `crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs:172` (changes a sensitive control or state-update path)

Before
```rust
for selection in curr_level.drain(..) {
                if self.input_budget == 0 {
                    return Err(graphql_error_at_pos(
                        code::BAD_USER_INPUT,
                        format!("Query has over {} nodes", self.max_input_nodes),
                        selection.pos,
                    ));
```
After
```rust
for selection in curr_level.drain(..) {
                if self.input_budget == 0 {
                    return Err(self.reporter.graphql_error_at_pos(
                        code::BAD_USER_INPUT,
                        format!("Query has over {} nodes", limits.max_query_nodes),
                        selection.pos,
                    ));
```

# Fix Pattern

Introduce a specialized resource budget for transaction-bearing GraphQL payloads, derive it from the protocol transaction byte limit plus encoding overhead, enforce it during GraphQL limit checking, and fail closed when the budget is exceeded.

## How It Was Fixed

The patch added max_tx_payload_size for GraphQL transaction payloads and a dedicated tx_payload_size_error path in the query limits checker. The error path emits Transaction payload too large and spends the remaining transaction payload budget by setting it to zero. The commit description also states that total GraphQL request size is checked against the combined read-query and transaction-payload budgets, with tests added for mutations and dry-run transaction requests.

# Why It Matters

1. Bounds unusually large transaction-bearing GraphQL requests separately from ordinary read queries.

2. Reduces risk of excessive resource use from oversized transaction payloads.

3. Keeps the limit aligned with protocol max transaction bytes and Base64 overhead.

4. Does not prove a concrete exploit or incident from the supplied evidence.

# Evidence Notes

The strongest evidence is the commit message and release note text describing max_tx_payload_size, transaction payload accounting, and combined request-size checks. The strongest visible code evidence is tx_payload_size_error in crates/sui-graphql-rpc/src/extensions/query_limits_checker.rs, which zeroes tx_payload_budget and reports Transaction payload too large. The server/builder.rs change appears to be test support. The supplied snippets do not independently show all enforcement sites for executeTransactionBlock or dryRunTransactionBlock, so confidence is medium rather than high. Protocol security invariant: GraphQL requests carrying transaction material should be bounded by a transaction-payload budget separate from ordinary read-query limits. The transaction payload portion, including executeTransactionBlock txBytes plus signatures and dryRunTransactionBlock txBytes, should not exceed a protocol-derived maximum transaction byte budget with Base64 overhead, and the total request should remain within the combined query and transaction payload limits. Verification notes: The patch does not prove remote exploitability or unauthenticated denial of service by itself. The patch does not show transaction validity or consensus safety being bypassed. The patch does not indicate state corruption despite transaction-related code paths. The fragment and error-reporting changes appear ancillary to the main payload-size invariant. No CVE, incident, or measured resource exhaustion impact is provided in the input. No command execution or file inspection was performed. Remote exploitability is not established by the provided evidence. Consensus safety, transaction validity bypass, and state corruption claims are unsupported. Classification is security hardening for possible resource exhaustion, not a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `potential-remote-dos`
Final tags: `graphql-rpc, payload-size-limit, transaction-payload, resource-exhaustion, availability-hardening`

The supplied evidence supports retaining this as security hardening, not a confirmed vulnerability fix. The commit explicitly adds a protocol-derived maximum transaction payload size for GraphQL mutations and dry-run transaction queries, describes the change as protection against large transaction queries, and the code evidence shows a dedicated transaction payload budget error path that fails oversized payloads and spends the budget. The evidence does not prove an exploit, outage, unauthenticated attack path, or concrete denial-of-service incident, so the final corpus framing should stay conservative.

## Security Evidence

1. Commit text says mutation payloads can be much larger due to transaction data and adds max_tx_payload_size.
2. Release notes state the limit is added to protect against large transaction queries.
3. Patch adds tx_payload_size_error that reports Transaction payload too large and sets tx_payload_budget to zero.
4. Tests were added for mutation and dry-run transaction limit behavior according to the commit body.

## Missing Evidence

1. No CVE, advisory, incident, or exploit scenario is provided.
2. Supplied snippets do not show all enforcement call sites for executeTransactionBlock or dryRunTransactionBlock.
3. No evidence proves unauthenticated reachability or measured resource exhaustion impact.
4. No consensus, transaction validity, or state corruption security issue is shown.

## Claim Boundaries

1. Classify as GraphQL RPC availability hardening for oversized transaction-bearing payloads.
2. Do not claim a confirmed remotely exploitable DoS from the provided evidence alone.
3. Do not claim transaction validation bypass, consensus compromise, or state corruption.
4. Fragment and reporter refactors appear ancillary and should not be treated as the core security fix.
