# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-05-21-go-ethereum-core-logic-52db6d8be`
- Bug family: `authz_and_role_gates`
- Bug class: `cross-check-validation-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `exact-validation-gate`

## Violated Invariant

- Invariant: During downloader synchronization, a peer-supplied block selected for cross-check must have the exact expected parent from the advertised hash chain; it is not enough for the parent hash to merely exist somewhere in the local download queue.

## Trust Boundary

- Boundary: Peer-supplied synchronization or protocol data crossing into local validation and scheduling logic.

## Attack Surface

- Entrypoint type: `p2p message`
- Sensitive sink: `consensus-visible state transition or journal replay`

## Impact Pattern

- Primary impact: `sync-integrity`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch fixes a downloader validation weakness where forged blocks could satisfy cross-checks by pointing their parent hash at any known queued hash.
