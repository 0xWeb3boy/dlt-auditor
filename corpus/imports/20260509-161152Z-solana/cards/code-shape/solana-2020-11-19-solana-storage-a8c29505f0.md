# Code-Shape Card

## Metadata

- ID: `solana-2020-11-19-solana-storage-a8c29505f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-dos`

## Code Shape Summary

The patch is a confirmed security fix for a remotely triggerable validator panic in Solana gossip pull handling. The evidence shows Bloom<T> sanitization changed from a no-op to rejecting empty bit vectors, matching the commit message that over-the-wire pull requests could cause division by zero in bloom filters.

## Search Motifs

- search for panic dos checks near storage entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Enforce structural invariants during sanitization of network-controlled data before arithmetic assumes those invariants hold.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
