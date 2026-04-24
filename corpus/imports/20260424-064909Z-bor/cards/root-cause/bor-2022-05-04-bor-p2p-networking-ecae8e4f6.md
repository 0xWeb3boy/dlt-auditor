# Root-Cause Card

## Metadata

- ID: `bor-2022-05-04-bor-p2p-networking-ecae8e4f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation-regression`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `network peer authenticity and protocol state validation`

## Violated Invariant

- Invariant: A node must authenticate, correlate, and validate peer-controlled protocol data before using it to advance handshake, sync, or peer-state decisions.

## Trust Boundary

- Boundary: remote peer to node networking boundary

## Attack Surface

- Entrypoint type: inbound p2p message, handshake, or sync response handler
- Sensitive sink: peer table mutation, sync scheduling, or message acceptance

## Impact Pattern

- Primary impact: reduced-peer-validation
- Secondary impact: low severity conditions

## Short Reusable Lesson

- A regression left required-block handling wired to an older PeerRequiredBlocks path instead of the current RequiredBlocks path, causing inconsistent propagation of configured required-block data into peer startup logic.
