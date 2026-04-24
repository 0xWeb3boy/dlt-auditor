# Root-Cause Card

## Metadata

- ID: `reth-2023-08-29-reth-p2p-networking-03afe376b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `listener-filter-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-policy-gating`

## Violated Invariant

- Invariant: `PropagateOnly` listeners should not receive transaction events for entries marked `propagate = false`. The diff shows this rule was enforced for related iterator paths and was added to the full transaction event stream in this patch.

## Trust Boundary

- Boundary: transaction pool policy -> network listener stream

## Attack Surface

- Entrypoint type: txpool-event-listener
- Sensitive sink: transaction propagation stream

## Impact Pattern

- Primary impact: policy-bypass
- Secondary impact: network-policy-bypass

## Short Reusable Lesson

- `PropagateOnly` listeners should not receive transaction events for entries marked `propagate = false`. The diff shows this rule was enforced for related iterator paths and was added to the full transaction event stream in this patch.
