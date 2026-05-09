# Code-Shape Card

## Metadata

- ID: `solana-2021-08-18-solana-transaction-processing-6f31882260`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `bpf-syscall-memory-overlap-validation`

## Code Shape Summary

The patch fixes the overlap guard used by Solana's BPF loader `memcpy` syscall. The old inline predicate only checked one apparent address ordering; the patched code uses a feature-gated call to `check_overlapping(src_addr, dst_addr, n)` and adds/registers the `mem_overlap_fix` feature. The evidence supports a BPF syscall guard correctness fix, but not stronger claims such as theft, privilege escalation, host memory access, or validator crash.

## Search Motifs

- search for bpf syscall memory overlap validation checks near transaction-processing entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace a local one-sided range-overlap predicate with a centralized overlap checker, and gate the behavior change through the feature set.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
