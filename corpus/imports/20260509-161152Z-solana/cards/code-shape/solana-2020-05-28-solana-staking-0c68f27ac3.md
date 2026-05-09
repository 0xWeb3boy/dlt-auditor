# Code-Shape Card

## Metadata

- ID: `solana-2020-05-28-solana-staking-0c68f27ac3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `denial-of-service`

## Code Shape Summary

Commit 0c68f27ac3 changes `core/src/serve_repair.rs` in the orphan repair response path. The supported issue is a denial-of-service/resource-exhaustion risk where `ServeRepair::run_orphan` could keep walking parent slot metadata after packet construction failed, because no packet was pushed and the response-count limit did not advance.

## Search Motifs

- search for denial of service checks near staking entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Fail closed in bounded response-generation loops: if an outbound packet cannot be constructed, stop traversal instead of continuing with unchanged progress counters.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
