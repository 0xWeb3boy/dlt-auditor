# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-07-01-go-ethereum-p2p-networking-d6f2c0a76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
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

- The patch fixes a denial-of-service risk in go-ethereum's downloader hash-fetch path. It adds `maxQueuedHashes = 256 * 1024` with an explicit DOS-protection comment and changes `fetchHashes` so continuation depends on `d.queue.Pending() < maxQueuedHashes` instead of always continuing after a successful hash insert.
