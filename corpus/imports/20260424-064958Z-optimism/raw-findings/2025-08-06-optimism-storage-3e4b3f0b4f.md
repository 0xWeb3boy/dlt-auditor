---
case_id: case_20250806_3e4b3f0b4f
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2025-08-06
source_refs:
  - git:3e4b3f0b4fb992873a6c423381f92c2cb17f7701
  - "crates/supervisor/storage/src/chaindb.rs:401"
  - "crates/supervisor/storage/src/chaindb.rs:1015"
  - "crates/supervisor/storage/src/traits.rs:422"
  - "crates/supervisor/storage/src/error.rs:43"
bug_class: unsafe-state-rewind
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain
  - storage
  - rewind
  - safety-boundary
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a boundary check so `rewind_log_storage` cannot rewind to or before the current `LocalSafe` head. That is well-supported as a storage-integrity fix, but the provided evidence does not establish a concrete security vulnerability or attacker-driven exploit path.

## Observed Patch Facts

1. In `crates/supervisor/storage/src/chaindb.rs`, the patch replaces `lp.rewind_to(to)?;` with `// Ensure we don't rewind to or before the LocalSafe head.`.

2. In `crates/supervisor/storage/src/chaindb.rs`, the patch replaces `fn test_rewind() {` with `fn test_rewind_log_storage_beyond_derivation_head_should_error() {`.

3. In `crates/supervisor/storage/src/traits.rs`, the patch adds `/// This method ensures that log storage is never rewound to(since it's inclusive) an...`.

4. In `crates/supervisor/storage/src/error.rs`, the patch adds `/// Represents an error that occurred when attempting to rewind log storage beyond th...`.

## Project Context

The changed code sits primarily in `crates/supervisor/storage/src`, `crates/supervisor/storage`, which anchors the finding in the `storage` area of the project. Historical context from `crates/supervisor/storage/src/metrics.rs`, `crates/supervisor/storage/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/supervisor/storage/src/metrics.rs`, `crates/supervisor/storage/src/lib.rs`. The strongest project-level identifiers around this patch are `head`, `safe`, `rewind`, and `block`.

## Before/After Behavior

Before the patch, `rewind_log_storage` instantiated `SafetyHeadRefProvider` but then called `lp.rewind_to(to)?;` without a visible `LocalSafe` guard. After the patch, it reads `SafetyLevel::LocalSafe` and returns `StorageError::RewindBeyondLocalSafeHead` when `to.number <= local_safe.number`, with matching docs and a regression test for the rejected case.

# Root Cause

The log-only rewind path did not enforce the invariant that rewinds must stay above the current `LocalSafe` head, so it could perform a partial rollback of logs without first coordinating the corresponding safety-state transition.

## Walkthrough

1. `crates/supervisor/storage/src/chaindb.rs` previously created both the log provider and safety-head provider, then immediately executed `lp.rewind_to(to)?;`.

2. The patch adds a `hp.get_safety_head_ref(SafetyLevel::LocalSafe)` lookup before any destructive rewind occurs.

3. If the requested target block number is less than or equal to the current local-safe block number, the function now returns `RewindBeyondLocalSafeHead` instead of mutating storage.

4. `crates/supervisor/storage/src/error.rs` adds that dedicated error variant, making the invalid boundary crossing explicit.

5. `crates/supervisor/storage/src/traits.rs` updates the API contract to state that `rewind_log_storage` must not cross the local-safe boundary and that broader rollback should use `rewind`.

6. The new test exercises the failure case and shows the intended behavior is now to reject that rewind request.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/supervisor/storage/src/chaindb.rs | 397 | enforces the local-safe boundary before log storage rewind deletes block logs |
| crates/supervisor/storage/src/traits.rs | 409 | defines the API invariant for log-only rewind versus full rewind behavior |
| crates/supervisor/storage/src/error.rs | 37 | surfaces an explicit failure when a caller attempts to rewind beyond the local-safe head |

## Code Snippets

## Snippet 1

Context: `crates/supervisor/storage/src/chaindb.rs:401` (changes a sensitive control or state-update path)

Before
```rust
let hp = SafetyHeadRefProvider::new(tx, self.chain_id);

                lp.rewind_to(to)?;
```
After
```rust
let hp = SafetyHeadRefProvider::new(tx, self.chain_id);

                // Ensure we don't rewind to or before the LocalSafe head.
                match hp.get_safety_head_ref(SafetyLevel::LocalSafe) {
                    Ok(local_safe) => {
                        // If the target block is less than or equal to the local safe head,
                        // we cannot rewind to it, as this would mean losing logs for the safe
                        // blocks. The check is inclusive since the rewind
```

## Snippet 2

Context: `crates/supervisor/storage/src/chaindb.rs:1015` (changes an authorization or privilege gate)

Before
```rust
}

    #[test]
    fn test_rewind() {
```
After
```rust
}

    #[test]
    fn test_rewind_log_storage_beyond_derivation_head_should_error() {
        let tmp_dir = tempfile::TempDir::new().unwrap();
        let db_path = tmp_dir.path().join("chaindb_rewind_beyond_derivation");
        let db = ChainDb::new(1, &db_path).unwrap();
```

## Snippet 3

Context: `crates/supervisor/storage/src/traits.rs:422` (changes a sensitive control or state-update path)

Before
```rust
pub trait StorageRewinder {
    /// Rewinds the log storage from the latest block down to the specified block (inclusive).
    ///
    /// # Arguments
```
After
```rust
pub trait StorageRewinder {
    /// Rewinds the log storage from the latest block down to the specified block (inclusive).
    /// This method ensures that log storage is never rewound to(since it's inclusive) and beyond
    /// the local safe head. If the target block is beyond the local safe head, an error is
    /// returned. Use [`StorageRewinder::rewind`] to rewind to and beyond the local safe head.
    ///
    /// # Arguments
```

## Snippet 4

Context: `crates/supervisor/storage/src/error.rs:43` (changes a sensitive control or state-update path)

Before
```rust
#[error("reorg required due to inconsistent storage state")]
    ReorgRequired,
}
```
After
```rust
#[error("reorg required due to inconsistent storage state")]
    ReorgRequired,

    /// Represents an error that occurred when attempting to rewind log storage beyond the local
    /// safe head.
    #[error("rewinding log storage beyond local safe head. to: {to}, local_safe: {local_safe}")]
    RewindBeyondLocalSafeHead {
        /// The target block number to rewind to.
```

# Fix Pattern

Add a pre-mutation invariant check to a destructive rollback path, reject invalid boundary-crossing requests with a typed error, and document the intended API split.

## How It Was Fixed

The fix reads the current `LocalSafe` head at the start of `rewind_log_storage` and blocks requests whose target is at or below that head. It also adds a specific storage error, updates the trait documentation, and adds a regression test for the forbidden rewind case.

# Why It Matters

1. It prevents deletion of logs for blocks the system still considers locally safe.

2. It reduces the chance of log storage and safety-head state drifting out of sync.

3. It turns an invalid partial rollback into an explicit failure instead of silently mutating state.

# Evidence Notes

The strongest direct evidence is the new guard in `crates/supervisor/storage/src/chaindb.rs`, the matching `RewindBeyondLocalSafeHead` variant in `crates/supervisor/storage/src/error.rs`, the updated `StorageRewinder` documentation in `crates/supervisor/storage/src/traits.rs`, and the added regression test. The evidence supports a state-integrity bug fix. It does not show who can invoke this path, whether the trigger is attacker-controlled, or any demonstrated impact such as privilege escalation, fund loss, consensus failure, or cross-chain forgery. Protocol security invariant: A log-only rewind must not delete logs at or below the current LocalSafe head, because that would let persisted logs diverge from the recorded safety state. Verification notes: The patch does not show who can trigger `rewind_log_storage` or whether the path is attacker-reachable. It does not prove direct consensus failure, fund loss, or privilege escalation. It does not show that remote exploitation or cross-chain message forgery was possible. The evidence supports storage/safety-state integrity impact, but not a fully demonstrated exploit chain. The added test covers the rejected rewind case at the local-safe boundary. The docs now describe that `rewind_log_storage` is not the API for crossing the safe boundary. The provided evidence does not include an exploit path or attacker reachability proof. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unsafe-state-rewind`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain, storage, rewind, safety-boundary`

The patch adds an explicit guard that blocks a destructive log-rewind operation from crossing the `LocalSafe` boundary, returns a typed error, updates the API contract, and adds a regression test. In this supervisor/storage context, preventing deletion of logs for blocks already considered locally safe is a security-sensitive integrity hardening measure because it protects a safety-state invariant. The evidence does not prove a concrete exploitable vulnerability or attacker-controlled trigger, so this is better retained as `security-hardening` rather than a confirmed `security-fix`.

## Security Evidence

1. The main code path now rejects rewinds where `to.number <= local_safe.number`.
2. The new error `RewindBeyondLocalSafeHead` makes the forbidden boundary crossing explicit.
3. The trait documentation now states that `rewind_log_storage` must not cross the local-safe head.
4. A regression test was added for the rejected rewind-beyond-safe-head case.
5. The prevented behavior would delete logs for blocks the system still marks as locally safe, creating safety-state inconsistency risk.

## Missing Evidence

1. No proof that untrusted or remote actors can invoke this rewind path.
2. No demonstrated exploit chain from invalid rewind to consensus failure, forgery, or fund loss.
3. No evidence that this bug was previously reachable in production deployments.
4. No advisory, CVE, or security report tying the issue to an attacker scenario.

## Claim Boundaries

1. The patch supports a security-sensitive integrity hardening claim, not a proven exploitable vulnerability claim.
2. The evidence shows protection of log/safety-head consistency around the `LocalSafe` boundary.
3. The evidence does not establish remote exploitability, privilege escalation, or direct financial impact.
