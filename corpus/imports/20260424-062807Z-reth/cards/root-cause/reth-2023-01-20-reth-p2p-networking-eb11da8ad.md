# Root-Cause Card

## Metadata

- ID: `reth-2023-01-20-reth-p2p-networking-eb11da8ad`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-handshake-state-inconsistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: The relevant invariant is protocol consistency: the outbound ETH `Status` fields and the `ForkFilter` used during peer compatibility checks should be derived from the same `ChainSpec` and local head. The patch enforces that consistency, but the provided evidence does not establish a repaired security boundary or exploit path.

## Trust Boundary

- Boundary: remote peer -> pending session admission

## Attack Surface

- Entrypoint type: p2p-session-setup
- Sensitive sink: authenticated peer session table

## Impact Pattern

- Primary impact: peer-authentication-risk
- Secondary impact: state-integrity

## Short Reusable Lesson

- The relevant invariant is protocol consistency: the outbound ETH `Status` fields and the `ForkFilter` used during peer compatibility checks should be derived from the same `ChainSpec` and local head. The patch enforces that consistency, but the provided evidence does not establish a repaired security boundary or exploit path.
