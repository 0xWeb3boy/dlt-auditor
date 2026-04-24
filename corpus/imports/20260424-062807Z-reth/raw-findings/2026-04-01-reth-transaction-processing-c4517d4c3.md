---
case_id: case_20260401_c4517d4c3
project: reth
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-04-01
source_refs:
  - git:c4517d4c3ef92b97052f47fbc670c47169c6e69b
  - "crates/engine/tree/src/tree/precompile_cache.rs:375"
  - "crates/engine/tree/src/tree/precompile_cache.rs:184"
  - "crates/engine/tree/src/tree/precompile_cache.rs:88"
  - "crates/engine/tree/src/tree/precompile_cache.rs:10"
bug_class: gas-accounting-corruption
impact_type:
  - gas-accounting-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - precompile-cache
  - gas-accounting
  - resource-control
  - stale-state-reuse
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a correctness bug in production precompile-cache gas accounting: cache hits previously reused a cached `PrecompileOutputExt` wholesale, including its `GasTracker`, instead of rebuilding gas state from the current call. That establishes stale-state reuse and corrupted reservoir accounting on cache hits. The provided material does not, by itself, establish a concrete security impact beyond that accounting corruption.

## Observed Patch Facts

1. In `crates/engine/tree/src/tree/precompile_cache.rs`, the patch adds `/// Cache hits must return the *caller's current* gas_limit and reservoir,`.

2. In `crates/engine/tree/src/tree/precompile_cache.rs`, the patch replaces `return entry.to_precompile_result();` with `return entry.to_precompile_result(input.gas, input.reservoir);`.

3. In `crates/engine/tree/src/tree/precompile_cache.rs`, the patch replaces `fn to_precompile_result(&self) -> PrecompileResultExt {` with `/// Construct a result using the cached output bytes and regular gas cost,`.

4. In `crates/engine/tree/src/tree/precompile_cache.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `crates/engine/tree/src/tree`, `crates/engine/tree/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/engine/tree/src/tree/tests.rs`, `crates/engine/tree/src/tree/payload_validator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/engine/tree/src/tree/tests.rs`, `crates/engine/tree/src/backfill.rs`. The strongest project-level identifiers around this patch are `reservoir`, `to_precompile_result`, `gas_limit`, and `output`.

## Before/After Behavior

Before the patch, the cache-hit branch returned `entry.to_precompile_result()` and `to_precompile_result(&self)` returned `Ok(self.output.clone())`, so the cached `PrecompileOutputExt` and embedded gas tracker were replayed unchanged. After the patch, the cache-hit path calls `entry.to_precompile_result(input.gas, input.reservoir)`, and `to_precompile_result` now rebuilds a fresh `GasTracker` from the caller's current gas limit and reservoir while reusing only cached output bytes, cached regular gas usage, and the cached `reverted` flag.

# Root Cause

The cache stored and replayed execution-stateful gas metadata from a prior precompile execution. On a later cache hit, returning that stored object reused stale gas-accounting state instead of deriving the result from the current caller context.

## Walkthrough

1. `crates/engine/tree/src/tree/precompile_cache.rs:181` changed the cache-hit return path from `entry.to_precompile_result()` to `entry.to_precompile_result(input.gas, input.reservoir)`.

2. `crates/engine/tree/src/tree/precompile_cache.rs:85` replaced `Ok(self.output.clone())` with logic that computes cached regular gas used and constructs a new `PrecompileOutputExt`.

3. The new result construction uses `GasTracker::new(gas_limit, gas_limit - gas_used, reservoir)`, showing that current-call gas state is now supplied explicitly rather than copied from the cached object.

4. The same hunk preserves `bytes` and `reverted`, which narrows the cache payload to replay-safe fields instead of replaying the full prior gas tracker.

5. The added test at `crates/engine/tree/src/tree/precompile_cache.rs:375` states the intended invariant directly: cache hits must use the caller's current `gas_limit` and `reservoir`, not stale values captured during the original miss.

6. The example-file changes mentioned in the commit message are supportive, but the primary evidence for the bug and fix is in the production `precompile_cache.rs` path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/engine/tree/src/tree/precompile_cache.rs | 181 | Cache-hit execution path; now reconstructs cached results using the caller's current gas state instead of returning a stale tracker. |
| crates/engine/tree/src/tree/precompile_cache.rs | 85 | Cached-result materialization; rebuilds GasTracker from live gas_limit and reservoir while replaying only regular gas usage and reverted status. |
| crates/engine/tree/src/tree/precompile_cache.rs | 375 | Regression test documenting the invariant that cache hits must preserve the caller's current reservoir and not reuse stale accounting state. |

## Code Snippets

## Snippet 1

Context: `crates/engine/tree/src/tree/precompile_cache.rs:375` (changes bounds, limits, or capacity handling)

Before
```rust
assert_eq!(result3.as_ref(), b"output_from_precompile_1");
    }
}
```
After
```rust
assert_eq!(result3.as_ref(), b"output_from_precompile_1");
    }

    /// Cache hits must return the *caller's current* gas_limit and reservoir,
    /// not the stale values captured during the original (miss) execution.
    #[test]
    fn test_cache_hit_preserves_caller_reservoir() {
        let precompile_gas_cost = 5000u64;
```

## Snippet 2

Context: `crates/engine/tree/src/tree/precompile_cache.rs:184` (changes a sensitive control or state-update path)

Before
```rust
{
            self.increment_by_one_precompile_cache_hits();
            return entry.to_precompile_result();
        }
```
After
```rust
{
            self.increment_by_one_precompile_cache_hits();
            return entry.to_precompile_result(input.gas, input.reservoir);
        }
```

## Snippet 3

Context: `crates/engine/tree/src/tree/precompile_cache.rs:88` (changes a sensitive control or state-update path)

Before
```rust
}

    fn to_precompile_result(&self) -> PrecompileResultExt {
        Ok(self.output.clone())
    }
}
```
After
```rust
}

    /// Construct a result using the cached output bytes and regular gas cost,
    /// but with the *caller's current* gas limit and reservoir so we don't
    /// overwrite live state-gas accounting (`reservoir`, `state_gas_spent`).
    fn to_precompile_result(&self, gas_limit: u64, reservoir: u64) -> PrecompileResultExt {
        let gas_used = self.regular_gas_used();
        Ok(PrecompileOutputExt {
```

## Snippet 4

Context: `crates/engine/tree/src/tree/precompile_cache.rs:10` (changes a sensitive control or state-update path)

Before
```rust
};
use reth_primitives_traits::dashmap::DashMap;
use revm::precompile::PrecompileId;
use revm_primitives::Address;
use std::{hash::Hash, sync::Arc};
```
After
```rust
};
use reth_primitives_traits::dashmap::DashMap;
use revm::{interpreter::gas::GasTracker, precompile::PrecompileId};
use revm_primitives::Address;
use std::{hash::Hash, sync::Arc};
```

# Fix Pattern

Do not cache and replay mutable per-call accounting state. Cache only replay-safe result components, and reconstruct caller-scoped execution metadata from the live invocation when serving a cache hit.

## How It Was Fixed

The patch changed cache-hit materialization to take the current input gas and reservoir, compute gas used from the cached entry, and build a fresh `GasTracker` for the returned result. It also preserves only cached output bytes and the cached `reverted` flag instead of cloning the entire previously stored output object.

# Why It Matters

1. The bug sits in a production execution path, not only in test code.

2. Stale gas-accounting state on cache hits can make current-call accounting depend on an earlier execution.

3. The fix restores a clear invariant: cache reuse must not overwrite caller-scoped gas state.

4. The supplied evidence does not prove a specific exploit outcome such as consensus failure, undercharging, or denial of service.

# Evidence Notes

Direct code evidence shows the old cache-hit path returned the cached output object unchanged and the new path rebuilds the result using `input.gas` and `input.reservoir`. The added regression test explicitly documents reservoir preservation as the expected behavior. The commit body states that the stale cached tracker included `reservoir` and `state_gas_spent` and corrupted EIP-8037 reservoir accounting, which is consistent with the code change. However, the provided evidence does not independently demonstrate attacker control, exploitability, or a concrete security consequence beyond accounting corruption. Protocol security invariant: A precompile cache hit must not reuse caller-scoped gas-accounting state from an earlier execution. Cached entries may replay deterministic output bytes, reverted status, and regular gas cost, but the current call's gas limit and reservoir must remain authoritative. Verification notes: The patch does not prove a remotely triggerable exploit or attacker control over cache-hit timing. The patch does not by itself establish whether the impact is consensus divergence, local validation failure, or only incorrect internal accounting. The patch does not quantify whether the stale tracker caused undercharging, overcharging, denial of service, or all of these in practice. The example-code update supports the diagnosis but is not independent evidence of production exploitability. The functional bug is well supported by the changed call site, the new result-construction logic, and the added regression test. Security impact remains unproven from the provided excerpts alone. The example update should be treated as corroborating support code, not primary proof of production impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gas-accounting-corruption`
Final impact type: `gas-accounting-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, precompile-cache, gas-accounting, resource-control, stale-state-reuse`

The patch evidence shows a real flaw in a security-sensitive execution path: cached precompile results were reusing a stale `GasTracker`, including caller-scoped reservoir state, and cache hits now rebuild gas state from the live caller context instead. That is strong evidence of hardening around protocol/resource accounting integrity in blockchain transaction processing. The excerpts do not prove a concrete exploitable vulnerability such as consensus failure, undercharging, or denial of service, so this is better retained as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. Cache hits previously returned the cached output object unchanged, including its embedded gas tracker.
2. The fix changes the cache-hit path to pass `input.gas` and `input.reservoir` into result reconstruction.
3. `to_precompile_result` now creates a fresh `GasTracker` from the caller's current gas limit and reservoir.
4. The new code reuses only replay-safe fields like output bytes, regular gas cost, and reverted flag.
5. The added regression test explicitly states that cache hits must preserve the caller's current reservoir and not reuse stale values.
6. The commit message describes corruption of EIP-8037 reservoir accounting, matching the code change in a resource-control subsystem.

## Missing Evidence

1. No proof that an attacker can reliably trigger the vulnerable cache-hit pattern for security impact.
2. No demonstrated outcome such as gas undercharge, overcharge, consensus divergence, or denial of service.
3. No evidence quantifying whether the bug crosses a trust boundary or is remotely exploitable.
4. No reproduction showing impact beyond incorrect internal accounting state.

## Claim Boundaries

1. Supported claim: the patch fixes stale per-call gas state reuse on precompile cache hits.
2. Supported claim: this hardens security-sensitive gas and reservoir accounting behavior.
3. Not supported: a concrete exploitable vulnerability with demonstrated attacker impact.
4. Not supported: specific downstream effects such as consensus break, economic loss, or network-wide DoS.
