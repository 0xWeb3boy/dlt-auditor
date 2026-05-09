# Root-Cause Card

## Metadata

- ID: `solana-2020-10-29-solana-cryptography-06067dd823`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-amplification-missing-endpoint-validation`
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

The root cause was trusting the UDP source address associated with gossip PullRequest handling before the remote endpoint had proven reachability at that address. This allowed a spoofed source address to trigger larger PullResponse traffic toward a third party.

## Impact Pattern

- Primary impact: ddos-amplification, traffic-reflection
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch addresses a UDP gossip amplification issue in Solana pull-request handling. The commit explicitly cites a HackerOne report describing spoofed PullRequest source addresses causing larger PullResponse packets to be sent to victims, and the code evidence shows a new ping-pong endpoint check before pull responses are generated.
