# Root-Cause Card

## Metadata

- ID: `reth-2024-03-19-reth-p2p-networking-1ad50d148`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-handshake-timeout`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `session-timeout-enforcement`

## Violated Invariant

- Invariant: Pending session authentication should complete within a bounded time or fail; otherwise session setup can remain unresolved longer than intended. The provided evidence establishes timeout enforcement, but not a concrete security exploit.

## Trust Boundary

- Boundary: remote peer -> pending session admission

## Attack Surface

- Entrypoint type: p2p-session-setup
- Sensitive sink: authenticated peer session table

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- Pending session authentication should complete within a bounded time or fail; otherwise session setup can remain unresolved longer than intended. The provided evidence establishes timeout enforcement, but not a concrete security exploit.
