# Code-Shape Card

## Metadata

- ID: `solana-2022-06-22-solana-consensus-5b864ef97d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `quic-ingress-resource-limiting`

## Code Shape Summary

The patch changes Solana's nonblocking QUIC server accept path to set per-connection concurrent unidirectional stream limits based on whether the remote IP is staked. Staked peers receive a calculated share based on stake and total stake, while unstaked peers receive a fixed cap. This may be availability or fairness hardening, but the supplied evidence does not prove an exploitable DoS issue or other security vulnerability.

## Search Motifs

- search for quic ingress resource limiting checks near consensus entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Apply the resource-control policy at the connection accept boundary after peer classification and before stream handling proceeds.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
