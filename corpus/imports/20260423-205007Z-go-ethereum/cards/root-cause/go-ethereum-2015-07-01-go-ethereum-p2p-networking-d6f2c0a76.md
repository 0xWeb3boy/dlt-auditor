# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-07-01-go-ethereum-p2p-networking-d6f2c0a76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-bounds`

## Violated Invariant

- Invariant: During eth synchronization, remotely supplied hash batches must not cause the downloader's pending hash queue to grow past an explicit capacity limit; fetching should stop once queued hash work reaches that limit.

## Trust Boundary

- Boundary: Peer-supplied synchronization or protocol data crossing into local validation and scheduling logic.

## Attack Surface

- Entrypoint type: `p2p message`
- Sensitive sink: `bounded work queue, fetch scheduling, or peer-driven validation/import logic`

## Impact Pattern

- Primary impact: `security-impact`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch fixes a denial-of-service risk in go-ethereum's downloader hash-fetch path.
