# Root-Cause Card

## Metadata

- ID: `geth-arb-2018-02-12-go-ethereum-p2p-networking-9123eceb0f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reply-correlation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `request-reply-correlation`

## Violated Invariant

- Invariant: A protocol reply must be correlated to the exact request token or packet hash, not only to the peer identity, before liveness or bonding state is updated.

## Trust Boundary

- Boundary: untrusted p2p reply -> request/liveness state machine

## Attack Surface

- Entrypoint type: p2p ping/pong handler
- Sensitive sink: node bonding, liveness confirmation, or request completion

## Impact Pattern

- Primary impact: peer-identity-integrity
- Secondary impact: protocol-state-integrity
- Severity guide: low-medium

## Short Reusable Lesson

- The pong path accepted replies by node identity without checking that the reply token matched the outstanding ping packet. Store the encoded request token and compare the reply token before marking the request complete.
