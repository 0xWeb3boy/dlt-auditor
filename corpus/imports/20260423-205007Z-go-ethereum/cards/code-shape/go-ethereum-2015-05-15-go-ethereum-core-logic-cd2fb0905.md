# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-cd2fb0905`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-sync-no-progress-dos`

## Code Shape Summary

- The hash synchronization loop accepted any non-empty peer response as enough to continue, while the queue insertion API did not expose whether the response actually advanced queue state. This left duplicate-only responses from a peer unchecked before synchronization reached a terminal/common-hash condition.

## Search Motifs

- Motif 1: rpc method missing exact checks for p2p sync no progress dos
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Expose forward-progress information from queue mutation and enforce it at the peer-controlled protocol loop boundary before issuing more work to the same peer

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Expose forward-progress information from queue mutation and enforce it at the peer-controlled protocol loop boundary before issuing more work to the same peer.

## False Match Warnings

- Supported claim is limited to peer-driven duplicate-hash replay/no-progress behavior during sync.
- Supported impact is denial-of-service or sync disruption, not chain integrity compromise.
