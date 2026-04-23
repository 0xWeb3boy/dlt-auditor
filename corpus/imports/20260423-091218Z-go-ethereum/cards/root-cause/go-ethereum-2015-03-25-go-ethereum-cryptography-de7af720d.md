# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-03-25-go-ethereum-cryptography-de7af720d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-reflection-amplification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch fixes a documented UDP discovery amplification vector in which an unbonded findnode request could cause the node to send a larger neighbors response to the packet source address, enabling spoofed-source reflection toward a victim.
