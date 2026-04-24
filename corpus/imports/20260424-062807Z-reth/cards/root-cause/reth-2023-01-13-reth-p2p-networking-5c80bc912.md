# Root-Cause Card

## Metadata

- ID: `reth-2023-01-13-reth-p2p-networking-5c80bc912`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-policy-gating`

## Violated Invariant

- Invariant: Discovered peers should only be added through the path that checks an advertised fork ID for compatibility; peers with no fork ID are still allowed.

## Trust Boundary

- Boundary: remote peer -> node networking stack

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: peer admission, scoring, or block/transaction import

## Impact Pattern

- Primary impact: peer-admission-bypass
- Secondary impact: network-exposure-reduction

## Short Reusable Lesson

- Discovered peers should only be added through the path that checks an advertised fork ID for compatibility; peers with no fork ID are still allowed.
