# Root-Cause Card

## Metadata

- ID: `firedancer-2024-07-15-firedancer-cryptography-22a0ab7f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `quic-packet-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `packet-length-and-number-validation`

## Violated Invariant

- Invariant: Wire-format packet lengths and packet-number state must be validated before they feed crypto, decoding, or stateful packet handling.

## Trust Boundary

- Boundary: Peer-controlled QUIC packet bytes crossing into crypto and decode logic.

## Attack Surface

- Entrypoint type: network packet decode path
- Sensitive sink: packet-number derivation and IPv4/UDP length-backed reads

## Impact Pattern

- Primary impact: protocol correctness
- Secondary impact: input validation hardening

## Short Reusable Lesson

- Protocol helpers consumed packet-number and packet-length state before proving the wire-format sizes and backing transport lengths were coherent.
