# Code-Shape Card

## Metadata

- ID: `solana-2021-03-16-solana-staking-999f81c56d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-resource-metering`

## Code Shape Summary

The patch is a resource-metering hardening change in Solana's BPF loader CPI path. It adds the `cpi_data_cost` feature gate and, when active, charges the compute meter for CPI account data bytes in both Rust and C account translation paths. The evidence supports CPI byte-accounting hardening, but not an access-control, staking, privilege-escalation, funds-loss, or proven denial-of-service finding.

## Search Motifs

- search for missing resource metering checks near staking entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add feature-gated resource accounting at the point where CPI account data length is known, and apply the same accounting across equivalent Rust and C CPI translation paths by threading shared runtime context into the helper.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
