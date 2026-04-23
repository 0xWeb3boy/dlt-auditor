---
case_id: case_20260401_7c1a43bac
project: reth
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2026-04-01
source_refs:
  - git:7c1a43bac59268c92990aea67e4fc38cf1049b7d
  - "crates/engine/tree/src/tree/precompile_cache.rs:375"
  - "crates/engine/tree/src/tree/precompile_cache.rs:184"
  - "crates/engine/tree/src/tree/precompile_cache.rs:88"
  - "crates/engine/tree/src/tree/precompile_cache.rs:10"
bug_class: gas-accounting-state-reuse
impact_type:
  - resource-accounting
  - execution-integrity
confidence: medium
tags:
  - blockchain-core
  - engine
  - precompile-cache
  - gas-accounting
  - resource-control
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes incorrect reuse of cached gas-accounting state on precompile cache hits. The supplied evidence supports a runtime correctness bug in protocol-sensitive accounting, but it does not establish a concrete vulnerability or demonstrated security impact.

## Observed Patch Facts

1. In `crates/engine/tree/src/tree/precompile_cache.rs`, the patch adds `/// Cache hits must return the *caller's current* gas_limit and reservoir,`.

2. In `crates/engine/tree/src/tree/precompile_cache.rs`, the patch replaces `return entry.to_precompile_result();` with `return entry.to_precompile_result(input.gas, input.reservoir);`.

3. In `crates/engine/tree/src/tree/precompile_cache.rs`, the patch replaces `fn to_precompile_result(&self) -> PrecompileResultExt {` with `/// Construct a result using the cached output bytes and regular gas cost,`.

4. In `crates/engine/tree/src/tree/precompile_cache.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `crates/engine/tree/src/tree`, `crates/engine/tree/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/engine/tree/src/tree/tests.rs`, `crates/engine/tree/src/tree/payload_validator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/engine/tree/src/tree/tests.rs`, `crates/engine/tree/src/tree/payload_validator.rs`. The strongest project-level identifiers around this patch are `reservoir`, `to_precompile_result`, `gas_limit`, and `output`.

## Before/After Behavior

Before the patch, cache hits returned a cloned cached PrecompileOutputExt, including the original call's GasTracker. After the patch, cache hits rebuild GasTracker from the current caller's input.gas and input.reservoir while reusing only cached bytes, regular gas usage, and the reverted flag.

# Root Cause

The cache stored and replayed a composite output object that embedded per-invocation gas state. On cache hits, the code treated that full object as reusable instead of reconstructing caller-specific accounting fields.

## Walkthrough

1. On a cache hit, the fast path previously called `entry.to_precompile_result()` with no current caller gas state.

2. `to_precompile_result(&self)` previously returned `Ok(self.output.clone())`, so the cached `GasTracker` was reused verbatim.

3. The patch changes the call site to `entry.to_precompile_result(input.gas, input.reservoir)`.

4. The helper now computes cached regular gas used and constructs `GasTracker::new(gas_limit, gas_limit - gas_used, reservoir)`.

5. The helper still reuses cached output bytes and preserves the cached `reverted` flag.

6. An added test states that cache hits must return the caller's current gas limit and reservoir rather than stale cached values.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/engine/tree/src/tree/precompile_cache.rs | 181 | cache-hit fast path now passes the live caller gas/reservoir into cached result reconstruction |
| crates/engine/tree/src/tree/precompile_cache.rs | 85 | cached result reconstruction now rebuilds GasTracker from caller state instead of cloning stale execution state |
| crates/engine/tree/src/tree/precompile_cache.rs | 369 | regression test asserting cache hits preserve the caller's current reservoir rather than stale cached values |

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

When caching execution results, do not reuse embedded live accounting objects across invocations. Reconstruct invocation-specific state from current inputs and replay only stable cached data.

## How It Was Fixed

The cache-hit path now passes the current caller gas limit and reservoir into result reconstruction. Instead of cloning the entire cached output, the code rebuilds a fresh `GasTracker` from current inputs, subtracts only the cached regular gas cost, and preserves the cached output bytes and `reverted` bit.

# Why It Matters

1. Precompile cache hits should behave like execution in the current caller frame.

2. Reusing stale gas state can corrupt reservoir accounting for later calls.

3. The patch shows a correctness issue in a resource-accounting path.

4. The supplied evidence does not prove external exploitability or consensus impact.

# Evidence Notes

Grounded evidence is limited to the changed precompile-cache file: the cache-hit call site now passes `input.gas` and `input.reservoir`, the helper no longer returns `self.output.clone()`, `GasTracker` is explicitly reconstructed, and a regression test states the caller reservoir must be preserved. The commit message says stale cached tracker state corrupted EIP-8037 reservoir accounting. Related references to payload processing only place the code in a sensitive subsystem; they do not establish attacker reachability or concrete security consequences. Protocol security invariant: A precompile cache hit must preserve the current caller frame's gas accounting. Cached entries may reuse output bytes and regular gas usage, but must not replay a stale GasTracker carrying another call's reservoir or other live accounting state. Verification notes: The patch does not prove a consensus split, invalid block acceptance, or invalid block rejection in the field. The patch does not show attacker-controlled inputs can reliably force harmful cache-hit behavior beyond the corrected accounting path. The patch does not indicate memory corruption, privilege escalation, or code execution. The patch does not quantify whether the impact was denial of service, economic loss, or only correctness drift in execution accounting. Evidence directly shows stale `GasTracker` reuse and its replacement with caller-derived reconstruction. The commit message and new test support the intended invariant around `reservoir`. The provided material does not show attacker control, denial of service, consensus divergence, or economic loss. Security relevance is plausible, but the vulnerability thesis is not established from the supplied evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gas-accounting-state-reuse`
Final impact type: `resource-accounting, execution-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, engine, precompile-cache, gas-accounting, resource-control`

The patch clearly fixes reuse of stale per-invocation gas-accounting state in a precompile cache hit path, and the code/comments tie that bug to corrupted `reservoir` and `state_gas_spent` accounting. In a blockchain execution engine, gas and reservoir accounting are security-sensitive resource-control mechanisms, so tightening this behavior fits security hardening. However, the supplied patch does not prove attacker reachability, exploitable impact, or a concrete consensus failure, so it is better retained as hardening rather than a confirmed security fix.

## Security Evidence

1. The cache-hit path changed from returning a cloned cached result to reconstructing the result with the caller's current `input.gas` and `input.reservoir`.
2. `to_precompile_result` no longer returns `self.output.clone()` and instead builds a fresh `GasTracker`, indicating the old behavior reused stale execution state across invocations.
3. The new helper comment explicitly says the change avoids overwriting live state-gas accounting, naming `reservoir` and `state_gas_spent`.
4. The commit message states stale cached tracker state corrupted EIP-8037 reservoir accounting.
5. A regression test was added asserting cache hits must preserve the caller's current gas limit and reservoir, confirming the intended security-sensitive invariant.

## Missing Evidence

1. No proof that an external attacker can reliably trigger the faulty cache-hit path in a harmful way.
2. No demonstrated impact such as consensus split, invalid block acceptance/rejection, denial of service, or economic exploit.
3. No evidence quantifying whether the bug was reachable across trust boundaries or only affected internal correctness.

## Claim Boundaries

1. The patch supports a gas-accounting and resource-control hardening claim, not a proven exploitable vulnerability claim.
2. It is justified to say stale cached execution state could corrupt live accounting on cache hits.
3. It is not justified from this evidence alone to claim confirmed consensus compromise, fund loss, privilege escalation, or remote code execution.
4. Tags and labels should stay focused on execution-engine gas accounting and precompile caching, not storage/database issues.
