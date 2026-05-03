# Root-Cause Card

## Metadata

- ID: `firedancer-2024-01-24-firedancer-transaction-processing-d17e587ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-key-isolation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `keyguard-mediated-signing`

## Violated Invariant

- Invariant: Private keys should remain behind a dedicated keyguard boundary, and network-facing components should request signatures instead of signing directly.

## Trust Boundary

- Boundary: QUIC/TLS or shred-producing components crossing into the keyguard client boundary.

## Attack Surface

- Entrypoint type: network-facing signing request path
- Sensitive sink: private-key backed handshake or shred signature generation

## Impact Pattern

- Primary impact: key exposure risk reduction
- Secondary impact: unauthorized signing risk reduction

## Short Reusable Lesson

- The change reroutes protocol and shred signing through a keyguard client so key-holding behavior is removed from direct protocol handlers.
