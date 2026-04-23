# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-cd2fb0905`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-sync-no-progress-dos`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch prevents a peer from repeatedly sending only hashes already known to the downloader queue during hash synchronization. The fix makes queue insertion report forward progress and treats a non-final zero-progress hash batch as ErrBadPeer, which the sync manager then removes.
