# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-cd2fb0905`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-sync-no-progress-dos`

## Code Shape Summary

- The patch prevents a peer from repeatedly sending only hashes already known to the downloader queue during hash synchronization. The fix makes queue insertion report forward progress and treats a non-final zero-progress hash batch as ErrBadPeer, which the sync manager then removes.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
