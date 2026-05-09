# Root-Cause Card

## Metadata

- ID: `solana-2022-06-22-solana-consensus-5b864ef97d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `quic-ingress-resource-limiting`
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

The provided before evidence shows connection-table accounting for staked and unstaked peers, but does not show per-connection concurrent unidirectional stream limits being applied in the accept path. The evidence supports an under-enforced resource allocation policy, not a proven vulnerability root cause.

## Impact Pattern

- Primary impact: denial-of-service-hardening, network-availability
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch changes Solana's nonblocking QUIC server accept path to set per-connection concurrent unidirectional stream limits based on whether the remote IP is staked. Staked peers receive a calculated share based on stake and total stake, while unstaked peers receive a fixed cap. This may be availability or fairness hardening, but the supplied evidence does not prove an exploitable DoS issue or other security vulnerability.
