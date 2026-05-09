# Root-Cause Card

## Metadata

- ID: `solana-2020-05-28-solana-staking-e68621b8bb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `denial-of-service`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stake-accountability-invariant`

## Violated Invariant

- Protocol input must satisfy stake accountability invariant before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

The orphan repair loop did not treat failure to construct a repair response packet as terminal for the current traversal, so processing could continue after encountering invalid shred data.

## Impact Pattern

- Primary impact: availability
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

Likely denial-of-service fix in Solana's orphan repair handling. The functional change in `core/src/serve_repair.rs` makes `ServeRepair::run_orphan` break when `repair_response::repair_response_packet(...)` returns `None`. The added regression test covers corrupted oversized shred data in the orphan repair path. The evidence supports a repair-service DoS fix, but does not establish consensus impact, cryptographic failure, or the exact exhausted resource.
