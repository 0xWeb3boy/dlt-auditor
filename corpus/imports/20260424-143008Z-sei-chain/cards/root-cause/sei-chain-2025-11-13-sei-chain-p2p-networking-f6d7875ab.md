# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-11-13-sei-chain-p2p-networking-f6d7875ab`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-invalid-peer-accountability`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-accountability-for-invalid-input`

## Violated Invariant

- Invariant: Protocol handlers must attribute invalid peer input to the peer and disconnect or penalize when the input violates handler invariants.

## Trust Boundary

- Boundary: remote peer message -> local consensus/blocksync/statesync handler

## Attack Surface

- Entrypoint type: p2p-reactor-message-handler
- Sensitive sink: retaining peer connection after invalid protocol data

## Impact Pattern

- Primary impact: protocol-abuse-mitigation
- Secondary impact: peer-isolation

## Short Reusable Lesson

- Replace passive peer-error reporting with active peer eviction for selected p2p handler failures and invalid state-sync block data, guarded by context checks. Invalid peer responses are less likely to be tolerated indefinitely. Consensus-adjacent p2p handlers apply stricter peer accountability. State sync evicts a peer that serves a light block inconsistent with trusted state.
