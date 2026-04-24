# Root-Cause Card

## Metadata

- ID: `bor-2023-01-03-bor-storage-fcf3d0048`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: A node must authenticate, correlate, and validate peer-controlled protocol data before using it to advance handshake, sync, or peer-state decisions.

## Trust Boundary

- Boundary: remote peer to node networking boundary

## Attack Surface

- Entrypoint type: inbound p2p message, handshake, or sync response handler
- Sensitive sink: peer table mutation, sync scheduling, or message acceptance

## Impact Pattern

- Primary impact: network-integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- Fork ID validation did not cleanly separate block-based versus time-based fork transitions and did not clearly anchor the full decision to one local snapshot, which could lead to incorrect compatibility results.
