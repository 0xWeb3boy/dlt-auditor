# Root-Cause Card

## Metadata

- ID: `stellar-core-2015-09-22-stellar-core-core-logic-edd011e29`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `preauth-io-timeout-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `preauthentication-resource-timeout`

## Violated Invariant

- Invariant: Unauthenticated peer connections must have tighter resource timeouts than authenticated peers and timeout policy should be enforced at the shared peer lifecycle layer.

## Trust Boundary

- Boundary: unauthenticated-network-peer -> node-overlay-connection-resources

## Attack Surface

- Entrypoint type: p2p-connection-handshake
- Sensitive sink: open socket, timer, and peer IO resources before authentication
- Attacker capability: Open peer connections and delay or avoid completing authentication.
- Main precondition: Pre-authentication and authenticated peers share the same long idle timeout.

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-exhaustion, availability-hardening
- Severity guess: medium because Pre-auth connection stalls can consume node resources, but the evidence supports hardening rather than a demonstrated DoS exploit.

## Short Reusable Lesson

- Authentication state is a resource-control boundary; unauthenticated peers should not receive the same patience as trusted protocol participants.
