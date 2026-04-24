# Root-Cause Card

## Metadata

- ID: `bor-2024-08-21-bor-p2p-networking-f88af2000`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation`
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

- Primary impact: denial-of-service
- Secondary impact: sync-disruption

## Short Reusable Lesson

- The termination path lacked an explicit final validation that a peer claiming a stronger chain had actually produced header progress before sync termination was accepted.
