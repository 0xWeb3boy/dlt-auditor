# Root-Cause Card

## Metadata

- ID: `solana-2020-10-28-solana-cryptography-f19778b7d9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-reflection-amplification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `network-endpoint-validation`

## Violated Invariant

- Protocol input must satisfy network endpoint validation before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

The gossip pull path accepted UDP PullRequest traffic without first proving that the apparent source address could receive packets sent to it. Because UDP source addresses can be spoofed, a node could be induced to send larger PullResponse traffic to a third-party address. Existing gossip signature checks did not establish endpoint reachability for the UDP response destination.

## Impact Pattern

- Primary impact: denial-of-service, traffic-amplification
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

Confirmed security fix for UDP gossip pull reflection/amplification. The patch adds ping-pong endpoint proof and gates gossip PullResponse generation on address validity plus prior ping response state, reducing the ability to spoof a PullRequest source address and induce larger responses to a victim.
