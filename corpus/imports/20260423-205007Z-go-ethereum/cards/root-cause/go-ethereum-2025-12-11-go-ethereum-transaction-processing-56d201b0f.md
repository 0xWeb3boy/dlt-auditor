# Root-Cause Card

## Metadata

- ID: `go-ethereum-2025-12-11-go-ethereum-transaction-processing-56d201b0f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-metadata-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Remote peers should not be able to make a node schedule or request transaction bodies for announced transaction types that the local txpool does not support. This invariant is limited to early fetch scheduling; final fetched-body validation still applies.

## Trust Boundary

- Boundary: Untrusted transaction submissions crossing into shared mempool resource accounting.

## Attack Surface

- Entrypoint type: `transaction admission path`
- Sensitive sink: `shared txpool reservation, scheduling, or eviction state`

## Impact Pattern

- Primary impact: `bandwidth-waste`
- Secondary impact: `resource-consumption`

## Short Reusable Lesson

- The patch hardens go-ethereum's transaction announcement handling by validating peer-supplied transaction type metadata before scheduling transaction body fetches.
