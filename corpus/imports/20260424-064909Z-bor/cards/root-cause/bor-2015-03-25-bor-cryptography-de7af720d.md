# Root-Cause Card

## Metadata

- ID: `bor-2015-03-25-bor-cryptography-de7af720d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-amplification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource limit and input validity enforcement`

## Violated Invariant

- Invariant: A node must not send an amplified network response until the requester has proven protocol state, reachability, or authorization appropriate for that response.

## Trust Boundary

- Boundary: unauthenticated UDP discovery packet to node networking boundary

## Attack Surface

- Entrypoint type: inbound discovery request handler
- Sensitive sink: larger outbound reply generation and peer-table update

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: high severity conditions

## Short Reusable Lesson

- The discovery handler trusted an unbonded sender enough to process findnode and emit a larger UDP response, enabling spoofed-source reflection/amplification.
