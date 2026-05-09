# Validation Card

## Metadata

- ID: `solana-2021-08-18-solana-transaction-processing-6f31882260`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `bpf-syscall-memory-overlap-validation`

## What Confirmed The Issue

- BPF loader memcpy syscall validation is changed from an inline predicate to `check_overlapping(src_addr, dst_addr, n)` when `mem_overlap_fix` is active.
- The old condition only visibly rejects one source/destination ordering: `dst_addr + n > src_addr && src_addr > dst_addr`.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
