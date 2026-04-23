# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-07-01-go-ethereum-p2p-networking-d6f2c0a76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The patch fixes a denial-of-service risk in go-ethereum's downloader hash-fetch path. It adds `maxQueuedHashes = 256 * 1024` with an explicit DOS-protection comment and changes `fetchHashes` so continuation depends on `d.queue.Pending() < maxQueuedHashes` instead of always continuing after a successful hash insert.

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
