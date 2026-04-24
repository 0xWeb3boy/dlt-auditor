---
case_id: case_20250828_b9dbd60602
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2025-08-28
source_refs:
  - git:b9dbd606021e5bd1d2180c51ed2e30c1b222f4ca
  - "kona/crates/supervisor/core/src/syncnode/resetter.rs:53"
  - "kona/crates/supervisor/core/src/syncnode/resetter.rs:278"
  - "kona/crates/supervisor/core/src/syncnode/resetter.rs:529"
  - "kona/crates/supervisor/core/src/syncnode/resetter.rs:468"
bug_class: state-validation
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - reorg
  - canonicality-check
  - recovery-path
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a canonicality check in the supervisor sync-node reset path so a chosen `local_safe` checkpoint is rejected if its mapped L1 source is no longer canonical. The evidence supports a reorg-handling correctness fix in reset/state recovery, but it does not establish a security vulnerability or attacker-driven impact.

## Observed Patch Facts

1. In `kona/crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `let SuperHead { cross_unsafe, cross_safe, finalized, .. } =` with `// check if the source of valid local_safe is canonical`.

2. In `kona/crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `client.expect_reset().returning(|_, _, _, _, _| Ok(()));` with `db.expect_derived_to_source()`.

3. In `kona/crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `db.expect_get_super_head().returning(move || Ok(super_head));` with `db.expect_derived_to_source()`.

4. In `kona/crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `db.expect_get_super_head().returning(move || Ok(super_head));` with `db.expect_derived_to_source()`.

## Project Context

The changed code sits primarily in `kona/crates/supervisor/core/src/syncnode`, `kona/crates/supervisor/core/src`, which anchors the finding in the `storage` area of the project. Historical context from `kona/crates/supervisor/core/src/syncnode/node.rs`, `kona/crates/supervisor/core/src/syncnode/client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `kona/crates/supervisor/core/src/reorg/task.rs`, `kona/crates/supervisor/core/src/l1_watcher/watcher.rs`. The strongest project-level identifiers around this patch are `predicate::eq`, `Asserter::new`, `MockTransport::new`, and `returning`.

## Before/After Behavior

Before the patch, `Resetter::reset` selected a latest valid `local_safe` block and proceeded without the shown check that the block's L1 source was still canonical. After the patch, it calls `derived_to_source(local_safe.id())`, checks `is_canonical(chain_id, source.id())`, and returns `ManagedNodeError::ResetFailed` if the source block is not canonical. The updated tests now expect the `derived_to_source(...)` lookup and mocked L1 canonicality responses, showing this validation is part of the reset flow.

# Root Cause

The reset path trusted stored derived state as a valid reset point without revalidating that its corresponding L1 source block was still canonical after reorg-sensitive events.

## Walkthrough

1. `Resetter::reset` obtains a candidate `local_safe` block for reset.

2. The patch maps that derived block back to its L1 source with `derived_to_source(local_safe.id())`.

3. It then checks whether that source block is canonical with `is_canonical(chain_id, source.id())`.

4. If the source is not canonical, the code logs a warning and aborts with `ManagedNodeError::ResetFailed` instead of continuing reset.

5. Tests were updated to require the source lookup and provide mocked canonical-chain RPC responses, confirming the new guard is expected behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| kona/crates/supervisor/core/src/syncnode/resetter.rs | 21 | Primary reset orchestration for managed sync nodes; selects the latest valid local-safe point before issuing reset. |
| kona/crates/supervisor/core/src/syncnode/resetter.rs | 53 | New canonicality guard that maps the chosen derived block back to its L1 source and aborts reset if the source block is not canonical. |
| kona/crates/supervisor/core/src/syncnode/node.rs | 46 | Wires the `Resetter` into the live supervisor sync-node path, showing the guard applies to runtime node recovery/reset behavior. |

## Code Snippets

## Snippet 1

Context: `kona/crates/supervisor/core/src/syncnode/resetter.rs:53` (changes a sensitive control or state-update path)

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

Context: `kona/crates/supervisor/core/src/syncnode/resetter.rs:278` (changes signature or replay validation logic)

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

Context: `kona/crates/supervisor/core/src/syncnode/resetter.rs:529` (changes signature or replay validation logic)

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

Context: `kona/crates/supervisor/core/src/syncnode/resetter.rs:468` (changes signature or replay validation logic)

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

Add a fail-closed provenance check before reusing persisted derived state in recovery logic.

## How It Was Fixed

The resetter now validates the L1 provenance of the selected `local_safe` checkpoint before proceeding. If the stored checkpoint maps to a non-canonical L1 source, reset is refused rather than using that state.

# Why It Matters

1. Prevents reset from reusing a checkpoint tied to a reorged-out L1 source.

2. Reduces inconsistent recovery after `l1_exhaust` and reorg interactions.

3. Shows a correctness guard in live reset behavior, not just test cleanup.

4. The evidence does not prove broader security impact.

# Evidence Notes

Direct evidence shows new code in `resetter.rs` that resolves `derived_to_source(local_safe.id())`, checks canonicality with `is_canonical(...)`, and fails closed on non-canonical source. Tests in the same file were expanded to expect that lookup and mocked L1 canonical responses. `syncnode/node.rs` shows `Resetter` is used in runtime supervisor reset wiring. The provided material does not show exploitability, adversary control, privilege impact, or chain-wide security failure. Protocol security invariant: A reset checkpoint should only be used if its recorded L1 source block is still canonical on the current L1 chain; stale derived state from a reorged-out source must not be reused for reset. Verification notes: The patch does not prove a remote attacker can trigger the race on demand. The patch does not by itself show fund loss, privilege escalation, or a full consensus split. The evidence is strongest for invalid local reset/state recovery, not for broader chain-wide compromise. Other reorg-handling paths may already have separate protections; this patch only proves an added guard in the reset path. Supported: added canonical-source validation in the reset path. Supported: behavior changes from proceeding to failing closed on non-canonical source. Supported: runtime path involvement via `syncnode/node.rs`. Not established: attacker triggerability or concrete security exploit. Not established: fund loss, privilege escalation, or consensus compromise. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `state-validation`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, reorg, canonicality-check, recovery-path`

The patch adds a fail-closed canonicality check before the supervisor reuses persisted derived state during reset. In a blockchain reorg-sensitive recovery path, refusing to reset from a checkpoint whose L1 source is no longer canonical is a meaningful integrity hardening measure. However, the provided evidence does not prove a concrete exploitable vulnerability, attacker control, or direct security impact such as fund loss or privilege escalation, so this is better classified as security hardening rather than a confirmed security fix.

## Security Evidence

1. `Resetter::reset` now resolves `derived_to_source(local_safe.id())` before proceeding.
2. The new `is_canonical(chain_id, source.id())` check rejects non-canonical L1 provenance.
3. The code fails closed with `ManagedNodeError::ResetFailed` instead of continuing reset on stale state.
4. The changed path is runtime recovery/reset logic for a managed sync node, which is integrity-sensitive in a blockchain system.
5. Tests were updated to exercise source lookup and canonical-chain RPC behavior, confirming the guard is intentional behavior.

## Missing Evidence

1. No evidence that an external attacker can trigger the race or steer reset behavior.
2. No proof of concrete exploit outcomes such as consensus split, fund loss, or privilege gain.
3. No advisory, CVE, or commit text explicitly frames this as a security vulnerability.
4. The patch alone does not show that pre-fix behavior caused actual state corruption beyond incorrect recovery handling.

## Claim Boundaries

1. Supported: the patch hardens reset logic against using a checkpoint derived from a non-canonical L1 source.
2. Supported: the change protects state integrity in a reorg-sensitive runtime path.
3. Not established: a concrete attacker-driven vulnerability or exploitability.
4. Not established: impact beyond local reset/recovery correctness and integrity guarding.
