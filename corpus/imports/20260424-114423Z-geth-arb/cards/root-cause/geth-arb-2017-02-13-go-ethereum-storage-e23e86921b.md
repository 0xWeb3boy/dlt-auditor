# Root-Cause Card

## Metadata

- ID: `geth-arb-2017-02-13-go-ethereum-storage-e23e86921b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-content-integrity-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `content-address-integrity`

## Violated Invariant

- Invariant: Content-addressed data received from a peer must hash to the requested key before it is cached, stored, or forwarded.

## Trust Boundary

- Boundary: untrusted content store request -> local content-addressed storage

## Attack Surface

- Entrypoint type: p2p storage/chunk request handler
- Sensitive sink: local store/cache insertion and replication

## Impact Pattern

- Primary impact: data-integrity
- Secondary impact: storage-poisoning-prevention
- Severity guide: low-medium

## Short Reusable Lesson

- Incoming chunk data could be processed under a claimed key before recomputing and comparing its content hash. Hash incoming content at admission and reject it when the computed digest does not equal the requested key.
