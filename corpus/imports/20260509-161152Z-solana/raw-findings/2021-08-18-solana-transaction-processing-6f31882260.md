---
case_id: case_20210818_6f31882260
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2021-08-18
source_refs:
  - git:6f318822602385fb7fa09fe5fec558ca29231090
  - "sdk/src/feature_set.rs:232"
  - "programs/bpf_loader/src/syscalls.rs:1231"
  - "sdk/src/feature_set.rs:180"
  - "programs/bpf_loader/src/syscalls.rs:21"
bug_class: bpf-syscall-memory-overlap-validation
impact_type:
  - runtime-integrity
  - sandbox-validation
tags:
  - blockchain-core
  - bpf-loader
  - syscall-validation
  - memory-overlap
  - feature-gated-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes the overlap guard used by Solana's BPF loader `memcpy` syscall. The old inline predicate only checked one apparent address ordering; the patched code uses a feature-gated call to `check_overlapping(src_addr, dst_addr, n)` and adds/registers the `mem_overlap_fix` feature. The evidence supports a BPF syscall guard correctness fix, but not stronger claims such as theft, privilege escalation, host memory access, or validator crash.

## Observed Patch Facts

1. In `sdk/src/feature_set.rs`, the patch adds `(gate_large_block::id(), "validator checks block cost against max limit in realtime,...`.

2. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `// cannot be overlapping` with `if if self.mem_overlap_fix {`.

3. In `sdk/src/feature_set.rs`, the patch replaces `lazy_static! {` with `pub mod gate_large_block {`.

4. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `libsecp256k1_0_5_upgrade_enabled, memory_ops_syscalls, secp256k1_recover_syscall_enab...` with `libsecp256k1_0_5_upgrade_enabled, mem_overlap_fix, memory_ops_syscalls,`.

## Project Context

The changed code sits primarily in `sdk/src`, `programs/bpf_loader/src`, `programs/bpf_loader`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sdk/src/lib.rs`, `sdk/src/transport.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/lib.rs`. The strongest project-level identifiers around this patch are `solana_sdk::declare_id`, `dst_addr`, `src_addr`, and `mem_overlap_fix`.

## Before/After Behavior

Before the patch, `SyscallMemcpy::call` rejected overlap only when `dst_addr + n > src_addr && src_addr > dst_addr` was true. After the patch, when `self.mem_overlap_fix` is active, it delegates overlap detection to `check_overlapping(src_addr, dst_addr, n)`; otherwise it preserves the old predicate. The feature is declared and registered in `sdk/src/feature_set.rs`.

# Root Cause

The old BPF `memcpy` syscall guard used an incomplete inline overlap predicate. Based on the shown condition, it detected the case where `src_addr` fell inside the destination range but did not symmetrically model all overlapping source/destination range orderings.

## Walkthrough

1. A BPF program invokes the loader `memcpy` syscall with destination address, source address, and length arguments.

2. The old syscall guard checks `dst_addr + n > src_addr && src_addr > dst_addr`.

3. That condition rejects only one apparent ordering of overlapping ranges.

4. The patch imports and wires the `mem_overlap_fix` runtime feature.

5. With the feature active, the syscall calls `check_overlapping(src_addr, dst_addr, n)` instead of using the inline predicate.

6. If overlap is detected, the syscall returns `SyscallError::CopyOverlapping`.

7. Before feature activation, the prior behavior remains available for deterministic runtime rollout.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/syscalls.rs | 21 | imports `mem_overlap_fix` feature gate for BPF syscall behavior |
| programs/bpf_loader/src/syscalls.rs | 1223 | BPF `memcpy` syscall receives untrusted program-provided source, destination, and length arguments |
| programs/bpf_loader/src/syscalls.rs | 1231 | replaces one-sided overlap rejection with feature-gated `check_overlapping` validation |
| sdk/src/feature_set.rs | 180 | declares the `mem_overlap_fix` runtime feature id |
| sdk/src/feature_set.rs | 232 | registers `mem_overlap_fix` in the feature set for activation |

## Code Snippets

## Snippet 1

Context: `sdk/src/feature_set.rs:232` (changes bounds, limits, or capacity handling)

Before
```rust
(spl_token_v2_set_authority_fix::id(), "spl-token set_authority fix"),
        (stake_merge_with_unmatched_credits_observed::id(), "allow merging active stakes with unmatched credits_observed #18985"),
        /*************** ADD NEW FEATURES HERE ***************/
    ]
```
After
```rust
(spl_token_v2_set_authority_fix::id(), "spl-token set_authority fix"),
        (stake_merge_with_unmatched_credits_observed::id(), "allow merging active stakes with unmatched credits_observed #18985"),
        (gate_large_block::id(), "validator checks block cost against max limit in realtime, reject if exceeds."),
        (mem_overlap_fix::id(), "Memory overlap fix"),
        /*************** ADD NEW FEATURES HERE ***************/
    ]
```

## Snippet 2

Context: `programs/bpf_loader/src/syscalls.rs:1231` (changes a sensitive control or state-update path)

Before
```rust
result: &mut Result<u64, EbpfError<BpfError>>,
    ) {
        // cannot be overlapping
        if dst_addr + n > src_addr && src_addr > dst_addr {
            *result = Err(SyscallError::CopyOverlapping.into());
            return;
```
After
```rust
result: &mut Result<u64, EbpfError<BpfError>>,
    ) {
        if if self.mem_overlap_fix {
            check_overlapping(src_addr, dst_addr, n)
        } else {
            dst_addr + n > src_addr && src_addr > dst_addr
        } {
            *result = Err(SyscallError::CopyOverlapping.into());
```

## Snippet 3

Context: `sdk/src/feature_set.rs:180` (changes a sensitive control or state-update path)

Before
```rust
}

lazy_static! {
    /// Map of feature identifiers to user-visible description
```
After
```rust
}

pub mod gate_large_block {
    solana_sdk::declare_id!("2ry7ygxiYURULZCrypHhveanvP5tzZ4toRwVp89oCNSj");
}

pub mod mem_overlap_fix {
    solana_sdk::declare_id!("vXDCFK7gphrEmyf5VnKgLmqbdJ4UxD2eZH1qbdouYKF");
```

## Snippet 4

Context: `programs/bpf_loader/src/syscalls.rs:21` (changes a sensitive control or state-update path)

Before
```rust
feature_set::{
        cpi_data_cost, enforce_aligned_host_addrs, keccak256_syscall_enabled,
        libsecp256k1_0_5_upgrade_enabled, memory_ops_syscalls, secp256k1_recover_syscall_enabled,
        set_upgrade_authority_via_cpi_enabled, sysvar_via_syscall, update_data_on_realloc,
    },
    hash::{Hasher, HASH_BYTES},
```
After
```rust
feature_set::{
        cpi_data_cost, enforce_aligned_host_addrs, keccak256_syscall_enabled,
        libsecp256k1_0_5_upgrade_enabled, mem_overlap_fix, memory_ops_syscalls,
        secp256k1_recover_syscall_enabled, set_upgrade_authority_via_cpi_enabled,
        sysvar_via_syscall, update_data_on_realloc,
    },
    hash::{Hasher, HASH_BYTES},
```

# Fix Pattern

Replace a local one-sided range-overlap predicate with a centralized overlap checker, and gate the behavior change through the feature set.

## How It Was Fixed

`programs/bpf_loader/src/syscalls.rs` now branches on `self.mem_overlap_fix` inside `SyscallMemcpy::call`; the fixed path calls `check_overlapping(src_addr, dst_addr, n)`. `sdk/src/feature_set.rs` declares `mem_overlap_fix` and registers it as `"Memory overlap fix"`.

# Why It Matters

1. Keeps BPF memory-copy syscall validation from accepting overlapping ranges missed by the old predicate.

2. Protects runtime syscall semantics for on-chain program execution.

3. Feature-gating preserves deterministic validator behavior during activation.

4. The supplied evidence does not prove a concrete exploit impact beyond the guard bypass/correctness issue.

# Evidence Notes

Primary evidence is the change in `programs/bpf_loader/src/syscalls.rs` around `SyscallMemcpy::call`, where the old predicate is replaced by a feature-gated `check_overlapping(src_addr, dst_addr, n)` path. Supporting evidence is the declaration and registration of `mem_overlap_fix` in `sdk/src/feature_set.rs`. The implementation of `check_overlapping` is not shown, so its exact algorithm should not be asserted. The heuristic transaction-processing panic narrative is unsupported and excluded. The nearby `gate_large_block` addition is unrelated to this finding. Protocol security invariant: BPF loader memory-copy syscalls should reject overlapping source and destination ranges before performing the copy, regardless of the relative ordering of the ranges, and any behavior-changing correction should be activated deterministically through the runtime feature set. Verification notes: No evidence here proves theft, privilege escalation, or arbitrary host memory access. No evidence here proves a remotely triggerable validator crash. The provided patch does not show the implementation of `check_overlapping`, only its use. The heuristic transaction-processing panic narrative is not supported by the shown hunks. The unrelated `gate_large_block` addition should not be treated as part of this bug shape. No tests are included in the provided evidence. `check_overlapping` implementation was not provided, so exact edge-case handling is unverified. No evidence establishes theft, privilege escalation, arbitrary host memory access, or validator crash. The finding is retained because the changed guard is in BPF loader syscall validation and fixes a concrete overlap-check gap. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `bpf-syscall-memory-overlap-validation`
Final impact type: `runtime-integrity, sandbox-validation`
Final tags: `blockchain-core, bpf-loader, syscall-validation, memory-overlap, feature-gated-hardening`

The supplied patch evidence supports retaining this as security hardening, not a proven security fix. The key change replaces an incomplete one-sided overlap predicate in the BPF loader memcpy syscall with a feature-gated centralized overlap check, which tightens validation of program-controlled memory copy arguments in a sensitive runtime path. The evidence does not prove a concrete exploit, liveness failure, validator crash, theft, privilege escalation, or host memory exposure, so the original liveness/security-fix framing is too strong.

## Security Evidence

1. BPF loader memcpy syscall validation is changed from an inline predicate to `check_overlapping(src_addr, dst_addr, n)` when `mem_overlap_fix` is active.
2. The old condition only visibly rejects one source/destination ordering: `dst_addr + n > src_addr && src_addr > dst_addr`.
3. The patch declares and registers a runtime feature named `mem_overlap_fix`, indicating a behavior-changing validation correction in consensus/runtime code.
4. On detected overlap, the syscall returns `SyscallError::CopyOverlapping`.

## Missing Evidence

1. No implementation of `check_overlapping` is provided, so exact coverage and edge-case behavior are not proven.
2. No test evidence or failing scenario is supplied.
3. No evidence proves validator crash, liveness failure, theft, privilege escalation, arbitrary host memory access, or consensus divergence.
4. No exploitability analysis is included beyond the guard correction itself.

## Claim Boundaries

1. Validate this as feature-gated BPF syscall memory-overlap validation hardening.
2. Do not claim a concrete exploitable vulnerability from the supplied evidence alone.
3. Do not retain the original `liveness-failure` impact framing.
4. Treat the nearby `gate_large_block` feature registration as unrelated to this finding.
