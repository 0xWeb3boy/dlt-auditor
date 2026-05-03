# Root-Cause Card

## Metadata

- ID: `firedancer-2024-05-01-firedancer-p2p-networking-30fb51e26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `wire-format-length-validation`

## Violated Invariant

- Invariant: Protocol state must reject wire-format identifiers whose lengths violate the handshake specification before state is updated.

## Trust Boundary

- Boundary: Peer-controlled Retry packet fields crossing into QUIC handshake processing.

## Attack Surface

- Entrypoint type: network handshake packet
- Sensitive sink: Retry packet acceptance and connection-state update

## Impact Pattern

- Primary impact: protocol hardening
- Secondary impact: none

## Short Reusable Lesson

- Handshake logic consumed Retry-related connection IDs before proving their encoded lengths matched protocol limits.
