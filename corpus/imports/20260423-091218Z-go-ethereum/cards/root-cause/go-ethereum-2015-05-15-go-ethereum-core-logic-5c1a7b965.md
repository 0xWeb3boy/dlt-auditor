# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-5c1a7b965`
- Bug family: `authz_and_role_gates`
- Bug class: `p2p-sync-validation-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `chain-lineage validation`

## Violated Invariant

- Invariant: A sampled sync response must prove continuity with the locally queued chain segment before it can satisfy a trust check.

## Trust Boundary

- Boundary: Untrusted remote downloader peer -> local chain-sync validation state.

## Attack Surface

- Entrypoint type: P2P block-sync response.
- Sensitive sink: Clearing a pending cross-check and continuing sync against a peer-advertised branch.

## Impact Pattern

- Primary impact: Sync-integrity failure against malicious peers.
- Secondary impact: Availability degradation through wasted or misdirected sync effort.

## Short Reusable Lesson

- Matching the sampled object is not enough when trust depends on graph membership. In sync protocols, the verifier must also confirm that the returned object links back to the locally tracked chain context before clearing the validation token.
