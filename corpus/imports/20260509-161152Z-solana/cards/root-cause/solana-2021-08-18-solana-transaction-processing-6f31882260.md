# Root-Cause Card

## Metadata

- ID: `solana-2021-08-18-solana-transaction-processing-6f31882260`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `bpf-syscall-memory-overlap-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The old BPF `memcpy` syscall guard used an incomplete inline overlap predicate. Based on the shown condition, it detected the case where `src_addr` fell inside the destination range but did not symmetrically model all overlapping source/destination range orderings.

## Impact Pattern

- Primary impact: runtime-integrity, sandbox-validation
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch fixes the overlap guard used by Solana's BPF loader `memcpy` syscall. The old inline predicate only checked one apparent address ordering; the patched code uses a feature-gated call to `check_overlapping(src_addr, dst_addr, n)` and adds/registers the `mem_overlap_fix` feature. The evidence supports a BPF syscall guard correctness fix, but not stronger claims such as theft, privilege escalation, host memory access, or validator crash.
