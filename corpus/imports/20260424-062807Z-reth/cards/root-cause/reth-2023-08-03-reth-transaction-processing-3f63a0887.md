# Root-Cause Card

## Metadata

- ID: `reth-2023-08-03-reth-transaction-processing-3f63a0887`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `policy-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-policy-gating`

## Violated Invariant

- Invariant: Pending-transaction notifications that feed propagation-sensitive listeners should preserve and honor each transaction's `propagate` policy instead of treating every pending transaction as equally propagatable.

## Trust Boundary

- Boundary: external transaction source -> mempool policy engine

## Attack Surface

- Entrypoint type: transaction-pool-handler
- Sensitive sink: mempool admission, eviction, or propagation decision

## Impact Pattern

- Primary impact: network-policy-bypass
- Secondary impact: none proven

## Short Reusable Lesson

- Pending-transaction notifications that feed propagation-sensitive listeners should preserve and honor each transaction's `propagate` policy instead of treating every pending transaction as equally propagatable.
