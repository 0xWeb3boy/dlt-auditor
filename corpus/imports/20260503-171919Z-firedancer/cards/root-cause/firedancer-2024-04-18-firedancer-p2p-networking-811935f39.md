# Root-Cause Card

## Metadata

- ID: `firedancer-2024-04-18-firedancer-p2p-networking-811935f39`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `null-dereference`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-presence-validation`

## Violated Invariant

- Invariant: Protocol handlers must fail closed when required connection state is absent before dereferencing peer or connection pointers.

## Trust Boundary

- Boundary: Unauthenticated network Retry packets crossing into the QUIC state machine.

## Attack Surface

- Entrypoint type: network handshake packet handler
- Sensitive sink: connection-state dereference in Retry handling

## Impact Pattern

- Primary impact: availability
- Secondary impact: denial of service

## Short Reusable Lesson

- The Retry handler continued into a peer/connection dereference even when the surrounding connection object was missing.
