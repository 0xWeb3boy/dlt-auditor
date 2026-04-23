# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-03-25-go-ethereum-cryptography-de7af720d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-reflection-amplification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-bounds`

## Violated Invariant

- Invariant: The discovery protocol should not process findnode requests or send larger neighbors responses unless the sender has an existing bond established through the discovery ping/pong flow. This is a bond requirement, not complete source-address validation.

## Trust Boundary

- Boundary: Unauthenticated network packets crossing into discovery request handling.

## Attack Surface

- Entrypoint type: `p2p message`
- Sensitive sink: `network response generation and peer table mutation`

## Impact Pattern

- Primary impact: `ddos-amplification`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch fixes a documented UDP discovery amplification vector in which an unbonded findnode request could cause the node to send a larger neighbors response to the packet source address, enabling spoofed-source reflection toward a victim.
