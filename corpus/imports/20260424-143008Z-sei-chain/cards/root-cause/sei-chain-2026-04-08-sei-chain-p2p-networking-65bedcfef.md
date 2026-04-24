# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-04-08-sei-chain-p2p-networking-65bedcfef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-peer-abuse-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-counter-lifecycle-ownership`

## Violated Invariant

- Invariant: Peer abuse counters must be owned by the component that observes peer identity and peer lifecycle events.

## Trust Boundary

- Boundary: p2p mempool sender identity -> peer penalty accounting state

## Attack Surface

- Entrypoint type: mempool-reactor-checktx-handler
- Sensitive sink: incrementing, cleaning, and applying peer failure counters

## Impact Pattern

- Primary impact: peer-abuse-mitigation
- Secondary impact: liveness

## Short Reusable Lesson

- Move peer failure accounting from generic mempool validation code into the p2p reactor, where peer identity and lifecycle are available. Filter counted failures to selected CheckTx error classes and add regression coverage for counter behavior and cleanup. Keeps peer penalty accounting closer to the p2p layer that knows sender identity.
