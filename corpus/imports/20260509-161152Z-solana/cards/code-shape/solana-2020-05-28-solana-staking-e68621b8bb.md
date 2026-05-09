# Code-Shape Card

## Metadata

- ID: `solana-2020-05-28-solana-staking-e68621b8bb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `denial-of-service`

## Code Shape Summary

Likely denial-of-service fix in Solana's orphan repair handling. The functional change in `core/src/serve_repair.rs` makes `ServeRepair::run_orphan` break when `repair_response::repair_response_packet(...)` returns `None`. The added regression test covers corrupted oversized shred data in the orphan repair path. The evidence supports a repair-service DoS fix, but does not establish consensus impact, cryptographic failure, or the exact exhausted resource.

## Search Motifs

- search for denial of service checks near staking entrypoints
- compare validation before and after the stake-accountability-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Fail closed on repair response construction failure by terminating the current orphan traversal.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
