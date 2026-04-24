# Root-Cause Card

## Metadata

- ID: `sei-chain-2023-01-12-sei-chain-p2p-networking-e52126b92`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-invalid-tx-peer-abuse-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-abuse-enforcement`

## Violated Invariant

- Invariant: Repeated malformed or policy-invalid transaction traffic must be attributable to a peer and bounded by an enforceable penalty threshold.

## Trust Boundary

- Boundary: remote p2p transaction sender -> local mempool admission resources

## Attack Surface

- Entrypoint type: mempool-checktx-handler
- Sensitive sink: retaining peer connection and spending validation resources

## Impact Pattern

- Primary impact: resource-abuse-mitigation
- Secondary impact: liveness

## Short Reusable Lesson

- Add a configurable per-peer threshold to an existing failed-validation counter and invoke peer eviction when the threshold is exceeded, with basic validation for the new threshold setting. Adds an enforcement action to an existing per-peer failed CheckTx counter. May reduce repeated invalid-transaction load from a single peer when enabled.
