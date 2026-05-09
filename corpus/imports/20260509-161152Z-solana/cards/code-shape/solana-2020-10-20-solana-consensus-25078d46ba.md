# Code-Shape Card

## Metadata

- ID: `solana-2020-10-20-solana-consensus-25078d46ba`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `gossip-stale-peer-fanout`

## Code Shape Summary

The patch hardens Solana CRDS gossip push target selection by filtering inactive peers out of normal push options. The evidence supports a gossip-layer availability hardening for redundant traffic toward offline or stale nodes, not a consensus, signature, or funds-loss vulnerability.

## Search Motifs

- search for gossip stale peer fanout checks near consensus entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add freshness-aware eligibility checks at the gossip push target-selection point, excluding stale peers from routine fanout while preserving bounded retry behavior for staked peers.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
