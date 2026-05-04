---
case_id: case_20240420_809c5fecc0
project: stacks-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
confidence: medium
source_quality: high
date: 2024-04-20
source_refs:
  - git:809c5fecc0d48589983e966e71d24cea496aa7e1
  - "clarity/src/vm/contexts.rs:1337"
  - "clarity/src/vm/contexts.rs:2126"
  - "clarity/src/vm/contexts.rs:1963"
bug_class: vm-error-propagation-transaction-validity
impact_type:
  - transaction-validity
  - state-integrity
  - consensus-integrity
tags:
  - blockchain-core
  - clarity-vm
  - stx-transfer
  - error-propagation
  - transaction-validity
  - consensus-sensitive
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a consensus-relevant STX transfer rollback bug in the Clarity VM. The grounded change is a one-character error-propagation fix in `Environment::stx_transfer`: `value.clone().expect_result()` became `value.clone().expect_result()?`. Given the surrounding code, this means the commit/rollback decision now matches the inner Clarity response result, committing only for inner `Ok(_)`. The added regression test is explicitly described as covering an STX transfer consolidation transaction invalidation bug from version `2.4.0.1.0`.

## Observed Patch Facts

1. In `clarity/src/vm/contexts.rs`, the patch replaces `Ok(value) => match value.clone().expect_result() {` with `Ok(value) => match value.clone().expect_result()? {`.

2. In `clarity/src/vm/contexts.rs`, the patch replaces `#[test]` with `/// Test the stx-transfer consolidation tx invalidation`.

3. In `clarity/src/vm/contexts.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `clarity/src/vm`, `clarity/src`, which anchors the finding in the `storage` area of the project. Historical context from `clarity/src/vm/events.rs`, `clarity/src/vm/variables.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `clarity/src/vm/events.rs`, `clarity/src/vm/types/mod.rs`. The strongest project-level identifiers around this patch are `value`, `match`, `crate::vm::callables::DefineType`, and `stacks_common::types::chainstate::StacksAddress`. Nearby tests or test-like files include `clarity/src/vm/tests/simple_apply_eval.rs`, `clarity/src/vm/tests/traits.rs`.

## Before/After Behavior

Before the patch, `Environment::stx_transfer` began a global context, called `stx_transfer_consolidated`, and matched `value.clone().expect_result()` directly at the commit/rollback decision point. That shape could cause the wrapper to branch on successful response extraction rather than the inner Clarity response result. After the patch, `expect_result()?` first propagates extraction failure, and the subsequent match is on the inner response; the shown code commits only for inner `Ok(_)`, with the adjacent `Err(_)` arm serving as the non-commit path.

# Root Cause

The root cause was an incorrect error-handling boundary in the STX transfer wrapper. The code omitted `?` when extracting the expected Clarity response, so the wrapper could make its commit decision at the outer extraction-result layer instead of the inner protocol-level ok/err layer.

## Walkthrough

1. `Environment::stx_transfer` starts a VM global context before invoking `stx_transfer_consolidated(self, from, to, amount, memo)`.

2. On the shown outer `Ok(value)` path, the old code matched `value.clone().expect_result()` directly.

3. The fixed code changes that expression to `value.clone().expect_result()?`, so extraction errors are propagated before the commit/rollback match.

4. The match then operates on the inner Clarity response result; the shown `Ok(_)` arm commits the global context.

5. The added regression test is named `stx_transfer_consolidate_regr_24010` and is documented as testing an STX transfer consolidation transaction invalidation bug from `2.4.0.1.0`.

6. The evidence supports STX transfer handling only; it does not establish non-STX asset impact or a concrete theft/balance-inflation exploit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| clarity/src/vm/contexts.rs | 1329 | STX transfer wrapper begins a global context, invokes consolidated transfer logic, and decides commit versus rollback from the returned Clarity response |
| clarity/src/vm/contexts.rs | 1337 | fixed decision point now unwraps the expected response and matches the inner ok/err result before committing |
| clarity/src/vm/contexts.rs | 2126 | regression test coverage for STX transfer consolidation transaction invalidation bug |

## Code Snippets

## Snippet 1

Context: `clarity/src/vm/contexts.rs:1337` (updates aggregate accounting or lifecycle state)

Before
```rust
let result = stx_transfer_consolidated(self, from, to, amount, memo);
        match result {
            Ok(value) => match value.clone().expect_result() {
                Ok(_) => {
                    self.global_context.commit()?;
```
After
```rust
let result = stx_transfer_consolidated(self, from, to, amount, memo);
        match result {
            Ok(value) => match value.clone().expect_result()? {
                Ok(_) => {
                    self.global_context.commit()?;
```

## Snippet 2

Context: `clarity/src/vm/contexts.rs:2126` (updates aggregate accounting or lifecycle state)

Before
```rust
}

    #[test]
    fn test_canonicalize_contract_context() {
```
After
```rust
}

    /// Test the stx-transfer consolidation tx invalidation
    ///  bug from 2.4.0.1.0
    #[apply(test_epochs)]
    fn stx_transfer_consolidate_regr_24010(
        epoch: StacksEpochId,
        mut tl_env_factory: TopLevelMemoryEnvironmentGenerator,
```

## Snippet 3

Context: `clarity/src/vm/contexts.rs:1963` (updates aggregate accounting or lifecycle state)

Before
```rust
#[cfg(test)]
mod test {
    use super::*;
    use crate::vm::callables::DefineType;
    use crate::vm::types::signatures::CallableSubtype;
    use crate::vm::types::{FixedFunction, FunctionArg, FunctionType, StandardPrincipalData};
```
After
```rust
#[cfg(test)]
mod test {
    use stacks_common::types::chainstate::StacksAddress;
    use stacks_common::util::hash::Hash160;

    use super::*;
    use crate::vm::callables::DefineType;
    use crate::vm::tests::{
```

# Fix Pattern

Use Rust error propagation when extracting the expected Clarity response, then base commit versus rollback on the inner ok/err response value.

## How It Was Fixed

The implementation added `?` to the `expect_result` call in `Environment::stx_transfer`, changing `value.clone().expect_result()` to `value.clone().expect_result()?`. The patch also added epoch-parameterized regression coverage for the STX transfer consolidation transaction invalidation case.

# Why It Matters

1. Failed STX transfers should not commit VM global-context state.

2. The affected wrapper directly controls commit versus rollback for STX transfer execution.

3. The regression test references transaction invalidation, which is consensus-sensitive in a blockchain VM.

4. The evidence does not prove theft, balance inflation, or impact outside STX transfers.

# Evidence Notes

Primary evidence is the one-line implementation change in `clarity/src/vm/contexts.rs` inside `Environment::stx_transfer`, where the decision point changed from `value.clone().expect_result()` to `value.clone().expect_result()?`. The surrounding excerpt shows a global context begin, a call to `stx_transfer_consolidated`, and a commit in the inner `Ok(_)` arm. Additional evidence is the added regression test comment describing an STX transfer consolidation transaction invalidation bug from `2.4.0.1.0`. The full body of `stx_transfer_consolidated` and full regression assertions are not provided, so exploitability and broader asset impact are not established. Protocol security invariant: A Clarity STX transfer executed inside a VM global context should commit only when the returned Clarity response is an ok result; an err result should take the rollback path rather than committing partial transfer-related state. Verification notes: The patch does not prove a remotely exploitable theft or balance inflation path by itself. The evidence does not show the full internals of `stx_transfer_consolidated`. The patch does not establish that non-STX asset transfers are affected. The imports for address and hash types are test support, not independent cryptographic changes. Downgraded confidence from high to medium because the provided evidence does not include the full transfer implementation or test assertions. Kept the verdict as likely security-fix because the changed path controls commit/rollback for STX transfers and the regression is transaction-invalidation related. Removed unsupported claims about storage accounting, non-STX assets, theft, and balance inflation. Treated added address/hash imports as test support, not cryptographic logic changes. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `vm-error-propagation-transaction-validity`
Final impact type: `transaction-validity, state-integrity, consensus-integrity`
Final tags: `blockchain-core, clarity-vm, stx-transfer, error-propagation, transaction-validity, consensus-sensitive`

The supplied patch supports a security-relevant hardening classification, but not a confident concrete security-fix claim. The one-line change affects STX transfer execution in the Clarity VM by propagating `expect_result()` errors before the commit/rollback decision, and the added regression test explicitly references an STX transfer consolidation transaction invalidation bug. In a blockchain VM this is consensus-sensitive, but the provided evidence does not prove exploitability, theft, balance inflation, or the exact invalidation failure mode.

## Security Evidence

1. Patch changes STX transfer VM logic at the commit/rollback decision point.
2. `expect_result()` changed to `expect_result()?`, making extraction errors propagate instead of being matched at the wrong layer.
3. Regression test is explicitly labeled as covering an STX transfer consolidation transaction invalidation bug from version 2.4.0.1.0.
4. The affected path handles STX transfer state inside a global context, which is consensus-sensitive in a blockchain runtime.

## Missing Evidence

1. Full body of `stx_transfer_consolidated` is not provided.
2. Full regression test assertions are not provided.
3. No evidence shows a concrete exploitable attack path.
4. No evidence proves theft, balance inflation, or non-STX asset impact.
5. No direct evidence of network-wide consensus divergence is supplied.

## Claim Boundaries

1. Keep the finding scoped to Clarity VM STX transfer error propagation and transaction validity.
2. Do not claim cryptographic or replay-sensitive changes based only on test imports.
3. Do not classify this as storage/database accounting from the supplied evidence.
4. Do not claim concrete economic exploitation beyond possible state or transaction-validity impact.
5. Treat this as security-hardening rather than a proven security-fix.
