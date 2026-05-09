# Root-Cause Card

## Metadata

- ID: `solana-2020-10-20-solana-consensus-25078d46ba`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `gossip-stale-peer-fanout`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `freshness-and-origin-validation`

## Violated Invariant

- Protocol input must satisfy freshness and origin validation before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

The root cause supported by the evidence is missing freshness filtering in CRDS gossip push target selection. Stale or offline peers could remain eligible push targets, which the commit message says caused redundant duplicate gossip traffic to be pushed toward nodes that were no longer active.

## Impact Pattern

- Primary impact: availability
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch hardens Solana CRDS gossip push target selection by filtering inactive peers out of normal push options. The evidence supports a gossip-layer availability hardening for redundant traffic toward offline or stale nodes, not a consensus, signature, or funds-loss vulnerability.
