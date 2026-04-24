---
case_id: case_20250828_676b987dc4
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
impact_type:
  - state-integrity
source_quality: high
date: 2025-08-28
source_refs:
  - git:676b987dc400c2acf21f79c5ce95c0a3f4fa9786
  - "crates/supervisor/core/src/syncnode/resetter.rs:53"
  - "crates/supervisor/core/src/syncnode/resetter.rs:278"
  - "crates/supervisor/core/src/syncnode/resetter.rs:529"
  - "crates/supervisor/core/src/syncnode/resetter.rs:468"
bug_class: insufficient-state-validation
confidence: medium
tags:
  - blockchain-core
  - reorg
  - canonicality-check
  - state-integrity
  - recovery-path
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a correctness fix in the supervisor syncnode reset path: before resetting to `local_safe`, the code now checks whether that block's mapped L1 source is still canonical. The patch may be security-relevant in a broad protocol-integrity sense, but the provided material does not establish an actual vulnerability or attacker-reachable security issue.

## Observed Patch Facts

1. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `let SuperHead { cross_unsafe, cross_safe, finalized, .. } =` with `// check if the source of valid local_safe is canonical`.

2. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `client.expect_reset().returning(|_, _, _, _, _| Ok(()));` with `db.expect_derived_to_source()`.

3. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `db.expect_get_super_head().returning(move || Ok(super_head));` with `db.expect_derived_to_source()`.

4. In `crates/supervisor/core/src/syncnode/resetter.rs`, the patch replaces `db.expect_get_super_head().returning(move || Ok(super_head));` with `db.expect_derived_to_source()`.

## Project Context

The changed code sits primarily in `crates/supervisor/core/src/syncnode`, `crates/supervisor/core/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/supervisor/core/src/syncnode/node.rs`, `crates/supervisor/core/src/syncnode/client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/supervisor/core/src/reorg/task.rs`, `crates/supervisor/core/src/l1_watcher/watcher.rs`. The strongest project-level identifiers around this patch are `predicate::eq`, `Asserter::new`, `MockTransport::new`, and `returning`.

## Before/After Behavior

Before the patch, `Resetter::reset` could proceed with a selected `local_safe` block without first verifying that its associated L1 source block was still canonical. After the patch, it calls `derived_to_source(local_safe.id())`, checks `is_canonical(chain_id, source.id())`, and aborts with `ResetFailed` if the source is noncanonical.

# Root Cause

The reset flow trusted previously stored derived state as a reset point without rechecking whether that state's L1 source remained on the canonical chain at reset time.

## Walkthrough

1. `node.rs` now passes an `l1_provider` into `Resetter::new`, enabling reset-time L1 checks.

2. `Resetter::reset` still finds a latest valid `local_safe` block through existing logic.

3. The new code maps that derived block back to its source with `derived_to_source(local_safe.id())`.

4. It then calls `is_canonical(chain_id, source.id())` and returns `ManagedNodeError::ResetFailed` if the source block is not canonical.

5. Updated tests add `derived_to_source` expectations and mocked RPC-backed canonical-chain responses to exercise the new guard.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/supervisor/core/src/syncnode/resetter.rs | 21 | managed-node reset flow that selects the latest valid local-safe block and now validates its L1 ancestry before proceeding |
| crates/supervisor/core/src/syncnode/resetter.rs | 53 | new guard that maps derived state back to its L1 source and aborts if the source block is noncanonical after reorg |
| crates/supervisor/core/src/syncnode/node.rs | 46 | constructor wiring that passes the L1 provider into the resetter so canonical-chain checks are available during reset |

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

Revalidate stored or derived state against live canonical chain state before reusing it in recovery or reset logic.

## How It Was Fixed

The fix adds an explicit canonicality check in `Resetter::reset`: after choosing `local_safe`, it resolves the corresponding L1 source and rejects the reset if that source is no longer canonical. Supporting constructor and test changes wire in the L1 provider and exercise canonical/noncanonical cases.

# Why It Matters

1. Prevents reset from proceeding based on stale derived state after an L1 reorg.

2. Makes reset decisions depend on current canonical ancestry rather than stored state alone.

3. Improves recovery correctness in a race-prone path.

# Evidence Notes

Grounded evidence is limited to `resetter.rs` and constructor wiring in `node.rs`. The strongest direct support is the added `derived_to_source` lookup, the `is_canonical` check, and the early `ResetFailed` return when the source block is noncanonical. The tests confirm intended behavior around canonicality checks. The provided evidence does not show confidentiality, authorization, remote exploitability, or concrete impact beyond incorrect reset behavior. Protocol security invariant: A reset target chosen from stored derivation state should still map to a canonical L1 source block at the time of reset. Verification notes: The patch does not prove a remote or adversarial trigger; the race may be purely operational. It does not show a confidentiality or authorization failure. It does not prove consensus split, fund loss, or permanent state corruption beyond potential reset to stale/noncanonical state. It does not show that every reorg hit this bug; only the checked reset path is evidenced. It does not prove exploitability beyond violating the canonical-source invariant during a timing window. The commit subject explicitly mentions an `l1_exhaust` and `reorg` race condition, supporting the race-condition classification. The code clearly adds a runtime guard for noncanonical source blocks. Security impact is not demonstrated by the provided diff and context alone, so the verdict is downgraded to `unclear`. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-state-validation`
Final confidence: `medium`
Final tags: `blockchain-core, reorg, canonicality-check, state-integrity, recovery-path`

The patch does not prove an exploitable vulnerability, but it clearly hardens a security-sensitive blockchain reset path by refusing to reset from derived state whose mapped L1 source is no longer canonical. In this project context, canonical-chain validation is part of protocol/state-integrity protection, and the new guard removes a risky condition during a reorg race. That supports retaining this as security-hardening rather than a confirmed security fix.

## Security Evidence

1. `Resetter::reset` now resolves `local_safe` back to its L1 source before reuse.
2. The new `is_canonical(chain_id, source.id())` check aborts reset on noncanonical ancestry.
3. The added behavior prevents reuse of stale derived state after an L1 reorg.
4. `node.rs` wiring adds an L1 provider specifically to enable runtime canonicality validation.
5. Tests were updated to cover canonical and noncanonical source-block cases in the reset flow.

## Missing Evidence

1. No proof of attacker control or externally triggerable exploitation beyond the race window.
2. No evidence of confidentiality, authentication, or authorization impact.
3. No demonstrated consensus split, fund loss, or permanent corruption caused by the old behavior.
4. No advisory, CVE, or explicit security statement from maintainers in the supplied material.

## Claim Boundaries

1. Validate this as hardening of protocol/state-integrity checks, not as a proven exploitable vulnerability.
2. Do not claim concrete state corruption or fund impact from the patch alone.
3. Do not overstate the root cause beyond a missing canonicality recheck in a reorg-sensitive reset path.
4. Do not claim broad remote exploitability; the evidence supports a race-prone integrity condition only.
