# Root-Cause Card

## Metadata

- ID: `solana-2020-10-28-solana-cryptography-ae91270961`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-amplification-via-source-spoofing`
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

The PullRequest path lacked endpoint reachability validation before generating larger UDP PullResponse packets, allowing a spoofed source address to be used as the response destination.

## Impact Pattern

- Primary impact: denial-of-service, traffic-amplification
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

Confirmed security fix for spoofed-source UDP amplification in Solana gossip pull handling. The commit body explicitly describes PullRequest source spoofing causing much larger PullResponse traffic to a victim, and the patch adds Ping/Pong handling plus a pull-request gate that filters requests before response generation unless the source address has passed the endpoint check.
