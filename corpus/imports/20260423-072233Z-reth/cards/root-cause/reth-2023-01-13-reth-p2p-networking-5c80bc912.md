# Root-Cause Card

## Metadata

- ID: `reth-2023-01-13-reth-p2p-networking-5c80bc912`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-protocol-compatibility-validation`

## Violated Invariant

- Invariant: Peers discovered from an untrusted network source must pass protocol compatibility checks before they are admitted to the managed peer set.

## Trust Boundary

- Boundary: Discovery gossip and ENR metadata crossing into local peer admission state.

## Attack Surface

- Entrypoint type: p2p-discovery-event
- Sensitive sink: Peer-set insertion and future dialing/session scheduling.

## Impact Pattern

- Primary impact: Incompatible discovered peers are filtered before entering the peer set.
- Secondary impact: Reduces wasted dialing and exposure to peers on the wrong chain or fork.

## Short Reusable Lesson

- Discovery-sourced peers were inserted directly instead of flowing through the fork-id validation path. The patch queues a discovered-node action and admits the peer only when its advertised fork id is absent or compatible.
