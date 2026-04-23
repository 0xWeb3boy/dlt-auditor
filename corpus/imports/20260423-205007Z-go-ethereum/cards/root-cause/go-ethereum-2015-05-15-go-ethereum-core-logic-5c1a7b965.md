# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-5c1a7b965`
- Bug family: `authz_and_role_gates`
- Bug class: `p2p-sync-validation-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `exact-validation-gate`

## Violated Invariant

- Invariant: During downloader hash-chain synchronization, a block returned for a pending random cross-check must be linked to the queued hash chain: matching the sampled block hash is not enough if the block's parent hash is absent from the downloader queue.

## Trust Boundary

- Boundary: Peer-supplied synchronization or protocol data crossing into local validation and scheduling logic.

## Attack Surface

- Entrypoint type: `p2p message`
- Sensitive sink: `bounded work queue, fetch scheduling, or peer-driven validation/import logic`

## Impact Pattern

- Primary impact: `p2p-sync-disruption`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch fixes a downloader validation flaw for a fake blockchain attack.
