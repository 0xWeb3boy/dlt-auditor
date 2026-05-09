# Code-Shape Card

## Metadata

- ID: `solana-2022-06-02-solana-cryptography-1c2ae470c5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-admission-control-hardening`

## Code Shape Summary

The draft correctly rejects the unsupported cryptography, replay, and signature-validation claims. The grounded change is that QUIC forwarding connection handling is now guarded by `stake != 0 || max_unstaked_connections > 0`, with related banking-stage forwarding plumbing through `ForwardOption`. However, the evidence does not prove a vulnerability or concrete exploit impact, so this should be classified as unclear rather than kept as a likely security...

## Search Motifs

- search for network admission control hardening checks near cryptography entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add an explicit stake-or-configured-unstaked-capacity gate around QUIC forwarding connection admission, and route forwarding behavior through an explicit forwarding-mode enum.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
