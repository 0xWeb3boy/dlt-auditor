---
case_id: case_20250708_ebb9f7cfcc
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: not-security
phase3_validated_as: not-security
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2025-07-08
source_refs:
  - git:ebb9f7cfcc2abc2eb3da2e0c36d66f4d559ca3da
  - "crates/supervisor/core/src/syncnode/resetter.rs:220"
  - "crates/supervisor/core/src/syncnode/resetter.rs:284"
  - "crates/supervisor/core/src/syncnode/resetter.rs:195"
  - "crates/supervisor/storage/src/providers/derivation_provider.rs:274"
bug_class: derivation-state-consistency
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain
  - derivation
  - storage
  - reset
  - integrity-check
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports an internal correctness fix, not a demonstrated vulnerability fix. One production snippet changes derivation-state validation for non-newer derived blocks, and the resetter excerpts mainly strengthen tests to assert errors are returned on failure cases.

## Observed Patch Facts

1. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `client` with `client.expect_block_ref_by_number().returning(|_| {`.

2. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `client` with `client.expect_reset().returning(|_, _, _, _, _| {`.

3. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `resetter.reset().await;` with `assert!(resetter.reset().await.is_err());`.

4. In `crates/supervisor/storage/src/providers/derivation_provider.rs`, the patch replaces `// Latest source block must be same as the incoming source block` with `// If the incoming derived block is not newer than the latest stored derived block,`.

## Project Context

The changed code sits primarily in `crates/supervisor/core/src/syncnode`, `crates/supervisor/core/src`, `crates/supervisor/storage/src/providers`, which anchors the finding in the `storage` area of the project. Historical context from `crates/supervisor/core/src/syncnode/task.rs`, `crates/supervisor/core/src/syncnode/node.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/supervisor/core/src/syncnode/task.rs`, `crates/supervisor/core/src/syncnode/node.rs`. The strongest project-level identifiers around this patch are `Arc::new`, `Resetter::new`, `resetter`, and `MockClient::new`.

## Before/After Behavior

Before the patch, the shown storage logic compared incoming state against the latest derivation state via a latest-source equality check. After the patch, when the incoming derived block number is not newer than the latest stored one, it fetches the stored pair at that same derived height and treats inconsistency as an error. Separately, the resetter tests changed from generic database-error fixtures and non-asserting calls to authentication-error fixtures with explicit `is_err()` assertions.

# Root Cause

The evidence points to a state-validation bug in derivation replay/reset handling: non-newer incoming derived pairs were checked against the latest state rather than the stored pair at the same derived height. The resetter material mostly reflects missing explicit test coverage for error propagation, not a separate proven production vulnerability.

## Walkthrough

1. In `derivation_provider.rs`, the removed condition compared `latest_derivation_state.source` with `incoming_pair.source`.

2. The new logic instead handles the case where `latest_derivation_state.derived.number >= incoming_pair.derived.number` by loading the stored pair for `incoming_pair.derived.number`.

3. The added comments state the intended behavior directly: do not save a non-newer pair; verify it against saved state and error if inconsistent.

4. In `resetter.rs`, tests that previously used `ManagedNodeError::DatabaseNotInitialised` were changed to authentication-related errors for block lookup and reset RPC paths.

5. Those same resetter tests now assert `resetter.reset().await.is_err()` instead of only invoking the call without checking the result.

6. The supplied deep-context references show `Resetter` is wired into syncnode processing, but they do not by themselves establish a security boundary or exploit path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/supervisor/storage/src/providers/derivation_provider.rs | 238 | Derivation storage write path; validates consistency when reset/replay submits a non-newer derived block pair |
| crates/supervisor/core/src/syncnode/resetter.rs | 187 | Reset execution path; propagates database, block lookup, and reset RPC failures during derivation reset |
| crates/supervisor/core/src/syncnode/task.rs | 1 | Managed event processing path that routes into reset handling during sync/recovery |
| crates/supervisor/core/src/syncnode/node.rs | 15 | Managed-node lifecycle wiring for subscription and reset behavior |

## Code Snippets

## Snippet 1

Context: `crates/supervisor/core/src/syncnode/resetter.rs:220` (changes the branch that decides whether execution stops or continues)

Before
```rust
let mut client = MockClient::new();
        client
            .expect_block_ref_by_number()
            .returning(|_| Err(ManagedNodeError::DatabaseNotInitialised));

        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
```
After
```rust
let mut client = MockClient::new();
        client.expect_block_ref_by_number().returning(|_| {
            Err(ManagedNodeError::Authentication(AuthenticationError::InvalidHeader))
        });

        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
```

## Snippet 2

Context: `crates/supervisor/core/src/syncnode/resetter.rs:284` (changes the branch that decides whether execution stops or continues)

Before
```rust
let mut client = MockClient::new();
        client.expect_block_ref_by_number().returning(move |_| Ok(super_head.local_safe));
        client
            .expect_reset()
            .returning(|_, _, _, _, _| Err(ManagedNodeError::DatabaseNotInitialised));

        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
```
After
```rust
let mut client = MockClient::new();
        client.expect_block_ref_by_number().returning(move |_| Ok(super_head.local_safe));
        client.expect_reset().returning(|_, _, _, _, _| {
            Err(ManagedNodeError::Authentication(AuthenticationError::InvalidJwt))
        });

        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
```

## Snippet 3

Context: `crates/supervisor/core/src/syncnode/resetter.rs:195` (changes the branch that decides whether execution stops or continues)

Before
```rust
let resetter = Resetter::new(Arc::new(client), Arc::new(db));

        resetter.reset().await;
        // Should return early, no panic
    }
```
After
```rust
let resetter = Resetter::new(Arc::new(client), Arc::new(db));

        assert!(resetter.reset().await.is_err());
    }
```

## Snippet 4

Context: `crates/supervisor/storage/src/providers/derivation_provider.rs:274` (changes a sensitive control or state-update path)

Before
```rust
};

        // Latest source block must be same as the incoming source block
        if latest_derivation_state.source != incoming_pair.source {
```
After
```rust
};

        // If the incoming derived block is not newer than the latest stored derived block,
        // we do not save it, check if it is consistent with the saved state.
        // If it is not consistent, we return an error.
        if latest_derivation_state.derived.number >= incoming_pair.derived.number {
            let stored_pair = self
                .get_derived_block_pair_by_number(incoming_pair.derived.number)
```

# Fix Pattern

Correctness hardening: validate replayed/non-newer state against the exact stored record for that height, and make error-path expectations explicit in tests.

## How It Was Fixed

The patch changes derivation consistency checking to use the stored pair at the incoming derived block number when the incoming block is not newer. It also updates reset-related tests so failure cases are modeled with authentication errors and the contract is explicit that `reset()` returns an error.

# Why It Matters

1. Reduces the chance of accepting inconsistent derived-state replay during reset or recovery.

2. Clarifies expected error propagation in reset paths.

3. Improves reliability and diagnosability of supervisor recovery behavior.

4. Does not, from the provided evidence, show an authorization, cryptographic, or privilege-boundary fix.

# Evidence Notes

The strongest production evidence is the `save_derived_block_pair` change in `crates/supervisor/storage/src/providers/derivation_provider.rs`. The `resetter.rs` excerpts shown are test changes, so they support expected behavior but do not by themselves prove a production security flaw or security fix. The authentication-themed error variants in those tests show error handling coverage, not an authentication bypass remediation. Protocol security invariant: No security-specific invariant is established by the provided evidence. The visible invariant is operational: when processing a non-newer derived block pair, the supervisor should compare against stored state at that same derived height, and reset-related errors should be surfaced rather than ignored. Verification notes: The provided patch evidence does not prove attacker-controlled input can reach the inconsistent-state path. Authentication-related changes here show error handling on auth failure, not an authentication bypass fix. The diff alone does not establish consensus compromise, fund impact, or privilege escalation. It is not proven that the prior behavior was externally exploitable rather than an operational reset bug. Only one visible production hunk directly changes runtime logic. The resetter evidence is largely test-only and should not be overstated. No attacker-controlled input path is established in the provided material. No evidence shows privilege escalation, auth bypass, replay protection failure, or fund/consensus impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `derivation-state-consistency`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain, derivation, storage, reset, integrity-check`

The patch evidence supports a conservative security-hardening classification. The only clear production change tightens validation in the supervisor's derivation storage path by checking a non-newer incoming derived pair against the stored pair at the same height and erroring on inconsistency, which is an integrity-sensitive safeguard in chain reset/derivation handling. However, the diff does not prove a concrete exploitable vulnerability, and the authentication-related changes shown are primarily tests for error propagation rather than a demonstrated auth bug fix.

## Security Evidence

1. Production logic now rejects inconsistent non-newer derived block pairs by loading the stored pair at the same derived height.
2. The changed code is in supervisor derivation/reset state handling, which is an integrity-sensitive path for chain state.
3. Tests were strengthened to require reset paths to return errors on authentication/RPC failures instead of merely avoiding panics.

## Missing Evidence

1. No evidence shows attacker control over the incoming derived pair or reset inputs.
2. No patch evidence demonstrates concrete exploitation, privilege gain, auth bypass, or direct fund impact.
3. The authentication-themed changes shown are test-only and do not prove a production authentication flaw was fixed.

## Claim Boundaries

1. Supported: the commit hardens derivation/reset state consistency checks.
2. Not supported: this was a confirmed exploitable security vulnerability.
3. Not supported: the patch proves an authentication bypass, replay exploit, or consensus-compromise bug.
