# Root-Cause Card

## Metadata

- ID: `solana-2022-06-02-solana-cryptography-1c2ae470c5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-admission-control-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

The provided evidence suggests the prior QUIC forwarding path lacked the newly visible stake-or-unstaked-capacity admission guard. It does not establish whether that omission was exploitable or only an implementation-policy correction.

## Impact Pattern

- Primary impact: resource-exhaustion-mitigation
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The draft correctly rejects the unsupported cryptography, replay, and signature-validation claims. The grounded change is that QUIC forwarding connection handling is now guarded by `stake != 0 || max_unstaked_connections > 0`, with related banking-stage forwarding plumbing through `ForwardOption`. However, the evidence does not prove a vulnerability or concrete exploit impact, so this should be classified as unclear rather than kept as a likely security...
