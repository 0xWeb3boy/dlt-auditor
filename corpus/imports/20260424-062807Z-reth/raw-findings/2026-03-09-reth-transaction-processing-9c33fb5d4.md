---
case_id: case_20260309_9c33fb5d4
project: reth
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-03-09
source_refs:
  - git:9c33fb5d455aba92f8a0042bede9897d862b6335
  - "crates/engine/tree/src/tree/payload_processor/mod.rs:1144"
  - "crates/engine/tree/src/tree/payload_processor/mod.rs:956"
  - "crates/engine/tree/src/tree/payload_processor/mod.rs:1379"
  - "crates/engine/tree/src/tree/payload_processor/mod.rs:445"
bug_class: cache-state-isolation
impact_type:
  - state-integrity
confidence: medium
tags:
  - engine
  - execution-cache
  - fork-handling
  - validator
  - state-isolation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a correctness bug in execution-cache reuse, not a confirmed vulnerability. The patch changes mismatched-parent cache reuse to clear the cache and update its stored hash before cloning, and the added tests show this prevents stale fork-related cache state from remaining associated with the old hash.

## Observed Patch Facts

1. In `crates/engine/tree/src/tree/payload_processor/mod.rs`, the patch replaces `// When the parent hash doesn't match, the cache is cleared and returned for reuse` with `// When the parent hash doesn't match (fork block), the cache is cleared,`.

2. In `crates/engine/tree/src/tree/payload_processor/mod.rs`, the patch replaces `// If the has is available (no other threads are using it), but has a mismatching` with `// Fork block: clear and update the hash on the ORIGINAL before cloning.`.

3. In `crates/engine/tree/src/tree/payload_processor/mod.rs`, the patch adds `/// Tests the full prewarm lifecycle for a fork block:`.

4. In `crates/engine/tree/src/tree/payload_processor/mod.rs`, the patch replaces `while let Some(entry) = queue.first_entry() &&` with `while let Some(entry) = queue.first_entry()`.

## Project Context

The changed code sits primarily in `crates/engine/tree/src/tree/payload_processor`, `crates/engine/tree/src/tree`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/engine/tree/src/tree/payload_processor/sparse_trie.rs`, `crates/engine/tree/src/tree/payload_processor/prewarm.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/engine/tree/src/tree/tests.rs`, `crates/engine/tree/src/tree/state.rs`. The strongest project-level identifiers around this patch are `cache`, `hash`, `block`, and `parent`.

## Before/After Behavior

Before the patch, `get_cache_for` cleared a reusable cache on parent-hash mismatch with `c.clear()` and then returned a clone, with no shown hash rebinding in that path. After the patch, the mismatch path uses `c.clear_with_hash(parent_hash)` before cloning, and tests were added or expanded to verify that fork-path reuse does not leave the original cache slot appearing bound to the old hash.

# Root Cause

When reusing an available cache slot for a different parent hash, the code cleared cached contents but did not update the stored cache hash before reuse. That allowed the slot's identity to remain stale even after fork-related reuse.

## Walkthrough

1. `PayloadExecutionCache::get_cache_for` checks the existing cache slot's stored hash against the requested `parent_hash` and whether the slot is available for reuse.

2. In the pre-fix mismatch path, the slot was cleared with `c.clear()` and then cloned, but the provided evidence does not show the stored hash being updated at that point.

3. The patch changes that mismatch path to `c.clear_with_hash(parent_hash)`, with an inline comment stating this prevents later matching on a stale hash.

4. The updated regression test shows a mismatched-parent lookup returning a reusable cache, then after that clone is dropped, a lookup by the original hash now goes through mismatch-and-clear behavior instead of treating the old hash as still valid.

5. The new fork lifecycle test documents the intended invariant: after fork prewarm work is abandoned, canonical execution must not inherit stale fork cache state.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/engine/tree/src/tree/payload_processor/mod.rs | 920 | Core cache-selection path that clears and rebinds execution cache entries to the requested parent hash before reuse |
| crates/engine/tree/src/tree/payload_processor/mod.rs | 1140 | Regression test for parent-hash mismatch handling and cache reuse after clear |
| crates/engine/tree/src/tree/payload_processor/mod.rs | 1373 | End-to-end fork-prewarm lifecycle test asserting canonical execution does not inherit stale fork cache state |

## Code Snippets

## Snippet 1

Context: `crates/engine/tree/src/tree/payload_processor/mod.rs:1144` (changes signature or replay validation logic)

Before
```rust
execution_cache.update_with_guard(|slot| *slot = Some(make_saved_cache(hash)));

        // When the parent hash doesn't match, the cache is cleared and returned for reuse
        let different_hash = B256::from([4u8; 32]);
        let cache = execution_cache.get_cache_for(different_hash);
        assert!(cache.is_some(), "cache should be returned for reuse after clearing")
    }
```
After
```rust
execution_cache.update_with_guard(|slot| *slot = Some(make_saved_cache(hash)));

        // When the parent hash doesn't match (fork block), the cache is cleared,
        // hash updated on the original, and clone returned for reuse
        let different_hash = B256::from([4u8; 32]);
        let cache = execution_cache.get_cache_for(different_hash);
        assert!(cache.is_some(), "cache should be returned for reuse after clearing");
```

## Snippet 2

Context: `crates/engine/tree/src/tree/payload_processor/mod.rs:956` (changes a sensitive control or state-update path)

Before
```rust
if available {
                // If the has is available (no other threads are using it), but has a mismatching
                // parent hash, we can just clear it and keep using without re-creating from
                // scratch.
                if !hash_matches {
                    c.clear();
                }
```
After
```rust
if available {
                if !hash_matches {
                    // Fork block: clear and update the hash on the ORIGINAL before cloning.
                    // This prevents the canonical chain from matching on the stale hash
                    // and picking up polluted data if the fork block fails.
                    c.clear_with_hash(parent_hash);
                }
```

## Snippet 3

Context: `crates/engine/tree/src/tree/payload_processor/mod.rs:1379` (changes signature or replay validation logic)

Before
```rust
);
    }
}
```
After
```rust
);
    }

    /// Tests the full prewarm lifecycle for a fork block:
    ///
    /// 1. Cache is at canonical block 4.
    /// 2. Fork block (parent = block 2) checks out the cache via `get_cache_for`, simulating what
    ///    `PrewarmCacheTask` does when it receives a `SavedCache`.
```

## Snippet 4

Context: `crates/engine/tree/src/tree/payload_processor/mod.rs:445` (changes bounds, limits, or capacity handling)

Before
```rust
next_for_execution += 1;

                    while let Some(entry) = queue.first_entry() &&
                        *entry.key() == next_for_execution
                    {
                        let _ = execute_tx.send(entry.remove());
```
After
```rust
next_for_execution += 1;

                    while let Some(entry) = queue.first_entry()
                        && *entry.key() == next_for_execution
                    {
                        let _ = execute_tx.send(entry.remove());
```

# Fix Pattern

When reusing a keyed cache across divergent parents or branches, clear-and-rebind the cache key on the shared slot before cloning or handing it out, and add regression tests for failed fork-side reuse.

## How It Was Fixed

The implementation replaced `c.clear()` with `c.clear_with_hash(parent_hash)` in the reusable mismatched-parent branch of `PayloadExecutionCache::get_cache_for`. Test coverage was strengthened to check both direct mismatch reuse and a fork-prewarm lifecycle where stale fork state must not remain associated with the original hash.

# Why It Matters

1. The patch affects a cache used in engine execution flow where parent-hash identity matters.

2. The evidence shows a concrete state-isolation problem: cache contents could be reset without rebinding the cache's hash.

3. The new tests indicate the maintainers were protecting against stale fork-derived state being seen by later canonical work.

4. The provided material does not establish external exploitability, invalid block acceptance, or a demonstrated consensus failure.

# Evidence Notes

Strongest evidence is the code change in `crates/engine/tree/src/tree/payload_processor/mod.rs` replacing `c.clear()` with `c.clear_with_hash(parent_hash)` and the added comment explaining the stale-hash risk. Supporting evidence is the expanded mismatch-parent test and the new fork-prewarm lifecycle test, both of which describe or check that canonical execution should not observe stale fork cache state. The formatting-only `while let Some(entry)` hunk does not contribute to the finding. The evidence supports a cache correctness and isolation issue; it does not, by itself, prove a security vulnerability. Protocol security invariant: An execution cache entry must remain correctly bound to the parent or executed-block hash it represents. If a cache slot is reused for a different parent hash, both its contents and its stored hash must be updated together before reuse so later lookups do not treat fork-derived cache state as valid for the old chain context. Verification notes: The patch does not prove an externally triggerable vulnerability. The patch does not by itself prove consensus failure or acceptance of an invalid block. No memory-safety issue, cryptographic break, or authentication bypass is shown in the provided evidence. The impact may be limited to incorrect cache reuse or stale prewarm state rather than a directly exploitable security flaw. The code excerpts directly support stale cache-hash handling as the bug. The tests support the intended invariant around fork and canonical cache reuse. Security impact remains unproven from the provided evidence alone. Classification is therefore `unclear`, and this should not be kept in a security corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cache-state-isolation`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `engine, execution-cache, fork-handling, validator, state-isolation`

The patch evidence supports a security-hardening classification in a security-sensitive validator/execution path, not a confirmed exploitable vulnerability. The implementation changes cache reuse across divergent parent hashes so the shared cache is cleared and rebound to the new hash before cloning, and the added tests explicitly guard against canonical execution observing stale fork-derived state after a failed fork prewarm. That is a meaningful integrity hardening measure for consensus-related processing, even though the patch alone does not prove invalid block acceptance, consensus breakage, or an externally triggerable attack.

## Security Evidence

1. `get_cache_for` now uses `clear_with_hash(parent_hash)` instead of `clear()` on parent-hash mismatch.
2. Inline comment says the change prevents the canonical chain from matching a stale hash and using polluted data after a fork failure.
3. New tests model a fork-prewarm lifecycle and assert canonical execution must not inherit stale fork state.
4. The affected code is in engine tree payload processing, a validator/execution subsystem where state isolation matters.

## Missing Evidence

1. No proof that stale cache reuse led to invalid block acceptance or consensus divergence.
2. No evidence of attacker control, remote triggerability, or practical exploit steps.
3. No demonstration that the bug crossed from cache pollution into externally visible incorrect execution results.

## Claim Boundaries

1. The evidence supports hardening of cache/state isolation across fork and canonical paths.
2. The evidence does not justify claiming a confirmed security vulnerability or concrete exploit.
3. The formatting-only queue hunk should not be treated as security-relevant evidence.
