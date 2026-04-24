---
case_id: case_20250828_2ba747f98b
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: not-security
phase3_validated_as: not-security
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2025-08-28
source_refs:
  - git:2ba747f98b6dbf13d63c574a1e7e9d2a4b59a520
  - "crates/supervisor/core/src/syncnode/resetter.rs:53"
  - "crates/supervisor/core/src/syncnode/resetter.rs:278"
  - "crates/supervisor/core/src/syncnode/resetter.rs:529"
  - "crates/supervisor/core/src/syncnode/resetter.rs:468"
bug_class: missing-canonicality-validation
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - reorg
  - canonicality
  - state-validation
  - fail-closed
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is a reset-path correctness fix, not an established security fix. It adds a canonicality check for the L1 source of the chosen `local_safe` reset anchor and aborts reset when that source is no longer canonical.

## Observed Patch Facts

1. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `let SuperHead { cross_unsafe, cross_safe, finalized, .. } =` with `// check if the source of valid local_safe is canonical`.

2. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `client.expect_reset().returning(|_, _, _, _, _| Ok(()));` with `db.expect_derived_to_source()`.

3. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `db.expect_get_super_head().returning(move || Ok(super_head));` with `db.expect_derived_to_source()`.

4. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `db.expect_get_super_head().returning(move || Ok(super_head));` with `db.expect_derived_to_source()`.

## Project Context

The changed code sits primarily in `crates/supervisor/core/src/syncnode`, `crates/supervisor/core/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/supervisor/core/src/syncnode/node.rs`, `crates/supervisor/core/src/syncnode/client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/supervisor/core/src/reorg/task.rs`, `crates/supervisor/core/src/l1_watcher/watcher.rs`. The strongest project-level identifiers around this patch are `predicate::eq`, `Asserter::new`, `MockTransport::new`, and `returning`.

## Before/After Behavior

Before the patch, the resetter could continue using the latest valid `local_safe` block without first checking whether that block's recorded L1 source was still canonical. After the patch, it resolves `local_safe` back to its source with `derived_to_source(...)`, checks canonicality with `is_canonical(...)`, and returns `ResetFailed` if the source block is no longer canonical.

# Root Cause

The reset flow trusted stored derived state (`local_safe`) as a reset anchor without revalidating that its upstream L1 source still matched canonical chain state.

## Walkthrough

1. `reset()` obtains the latest valid `local_safe` block.

2. The new code maps that derived block back to an L1 source via `derived_to_source(local_safe.id())`.

3. It then checks whether that source block is canonical on L1 with `is_canonical(chain_id, source.id())`.

4. If the source is non-canonical, the resetter logs a warning and aborts with `ManagedNodeError::ResetFailed` instead of proceeding.

5. Updated tests add `derived_to_source(...)` expectations and mocked L1 RPC canonical-block responses to exercise this new guard.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/supervisor/core/src/syncnode/resetter.rs | 21 | managed-node reset flow fetches the latest valid local safe block and now validates its upstream L1 source before continuing |
| crates/supervisor/core/src/syncnode/resetter.rs | 53 | new canonicality guard aborts reset when the stored source block for `local_safe` is no longer canonical after an L1 reorg |
| crates/supervisor/core/src/syncnode/node.rs | 46 | syncnode wiring path that instantiates and uses the resetter inside the supervisor-managed node lifecycle |

## Code Snippets

## Snippet 1

Context: `crates/supervisor/core/src/syncnode/resetter.rs:53` (changes a sensitive control or state-update path)

Before
```rust
};

        let SuperHead { cross_unsafe, cross_safe, finalized, .. } =
            self.db_provider.get_super_head().inspect_err(
```
After
```rust
};

        // check if the source of valid local_safe is canonical
        // If the source block is not canonical, it mean there is a reorg on L1
        // this makes sure that we always reset to a valid state
        let source = self.db_provider.derived_to_source(local_safe.id())?;
        if !self.is_canonical(chain_id, source.id()).await? {
            warn!(target: "supervisor::syncnode_resetter", %chain_id, %source, "Source block for the valid local safe is not canonical");
```

## Snippet 2

Context: `crates/supervisor/core/src/syncnode/resetter.rs:278` (changes signature or replay validation logic)

Before
```rust
client.expect_block_ref_by_number().returning(move |_| Ok(super_head.local_safe.unwrap()));

        client.expect_reset().returning(|_, _, _, _, _| Ok(()));

        let resetter = Resetter::new(Arc::new(client), Arc::new(db));

        assert!(resetter.reset().await.is_ok());
    }
```
After
```rust
client.expect_block_ref_by_number().returning(move |_| Ok(super_head.local_safe.unwrap()));

        db.expect_derived_to_source()
            .with(predicate::eq(super_head.local_safe.unwrap().id()))
            .returning(move |_| Ok(super_head.l1_source.unwrap()));

        let asserter = Asserter::new();
        let transport = MockTransport::new(asserter.clone());
```

## Snippet 3

Context: `crates/supervisor/core/src/syncnode/resetter.rs:529` (changes signature or replay validation logic)

Before
```rust
})
        });
        db.expect_get_super_head().returning(move || Ok(super_head));
```
After
```rust
})
        });

        db.expect_derived_to_source()
            .with(predicate::eq(super_head.local_safe.unwrap().id()))
            .returning(move |_| Ok(super_head.l1_source.unwrap()));

        let asserter = Asserter::new();
```

## Snippet 4

Context: `crates/supervisor/core/src/syncnode/resetter.rs:468` (changes signature or replay validation logic)

Before
```rust
.returning(move |_| Ok(last_valid_derived_block));

        db.expect_get_super_head().returning(move || Ok(super_head));

        client.expect_reset().times(1).returning(|_, _, _, _, _| Ok(()));

        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
```
After
```rust
.returning(move |_| Ok(last_valid_derived_block));

        db.expect_derived_to_source()
            .with(predicate::eq(last_valid_derived_block.id()))
            .returning(move |_| Ok(prev_source_block));

        let asserter = Asserter::new();
        let transport = MockTransport::new(asserter.clone());
```

# Fix Pattern

Revalidate persisted recovery anchors against current canonical upstream state before using them, and fail closed if the anchor's provenance is stale.

## How It Was Fixed

The fix inserts a pre-reset validation step in `crates/supervisor/core/src/syncnode/resetter.rs` that derives the L1 source for the selected `local_safe` block and rejects the reset when that source is not canonical. Tests were expanded to cover the new source lookup and canonicality check.

# Why It Matters

1. It prevents reset from reusing a stale derived anchor after an L1 reorg.

2. It improves state-consistency handling in supervisor recovery logic.

3. The evidence supports correctness hardening, not a demonstrated exploit or security-boundary bypass.

# Evidence Notes

The strongest evidence is the added logic and comments in `crates/supervisor/core/src/syncnode/resetter.rs` that explicitly check whether the source of `local_safe` is canonical and abort otherwise. The test changes support that interpretation by adding `derived_to_source(...)` expectations and mocked L1 canonical-block responses. `crates/supervisor/core/src/syncnode/node.rs` only provides surrounding wiring context. The commit subject mentions a race condition, but the provided diff more directly proves missing stale-source validation than the exact race mechanics. Protocol security invariant: A `local_safe` block used as a reset anchor must still map to a canonical L1 source block; if its recorded source is no longer canonical after an L1 reorg, reset should not proceed from that anchor. Verification notes: The patch does not prove an external attacker can trigger or control the race. The patch does not show fund loss, consensus split, or privilege escalation. Security impact beyond node state inconsistency is not demonstrated by the diff alone. The exact timing of `l1_exhaust` versus reorg handling is inferred from the commit subject and comments, not fully reconstructed from the patch. Tests were updated to model source lookup and canonical-L1 responses for reset behavior. The provided evidence does not show attacker control, privilege escalation, fund loss, or another concrete security impact. The exact `l1_exhaust` versus reorg timing is not reconstructed from the diff alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-canonicality-validation`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, reorg, canonicality, state-validation, fail-closed`

The patch is better classified as security hardening than non-security maintenance. It adds an explicit fail-closed canonicality check before reusing persisted `local_safe` state as a reset anchor, and aborts reset if that anchor's L1 source is no longer canonical after a reorg. In a blockchain supervisor/reset path, preventing recovery from stale non-canonical state is a security-sensitive integrity safeguard. The diff does not prove a concrete exploitable vulnerability or attacker-driven impact, so this should not be elevated to a full security-fix claim.

## Security Evidence

1. Adds a new guard that resolves `local_safe` back to its L1 source with `derived_to_source(local_safe.id())`.
2. Checks `is_canonical(chain_id, source.id())` before proceeding with reset.
3. Fails closed with `ManagedNodeError::ResetFailed` when the source block is non-canonical.
4. Patch comments explicitly tie the condition to L1 reorg handling and 'always reset to a valid state'.
5. Tests were expanded to cover source lookup and canonical/non-canonical L1 behavior in the reset path.

## Missing Evidence

1. No evidence of attacker control over the race or reorg timing.
2. No proof of fund loss, privilege escalation, consensus break, or remote code execution.
3. The patch does not show the full pre-patch exploitability or whether this was externally reachable beyond node-state inconsistency.

## Claim Boundaries

1. Supported claim: the commit hardens reset logic against using stale non-canonical chain state after an L1 reorg.
2. Supported claim: this is security-relevant integrity hardening in a blockchain-core recovery path.
3. Not supported: a confirmed exploitable vulnerability with demonstrated real-world impact.
4. Not supported: attacker-triggered compromise, theft, or privilege-boundary bypass from the patch alone.
