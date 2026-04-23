# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-cd2fb0905`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-sync-no-progress-dos`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-bounds`

## Violated Invariant

- Invariant: During downloader hash synchronization, a non-terminal response from the active peer must contribute at least one previously unseen hash to the queue before the downloader requests more hashes from that peer.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch prevents a peer from repeatedly sending only hashes already known to the downloader queue during hash synchronization.
