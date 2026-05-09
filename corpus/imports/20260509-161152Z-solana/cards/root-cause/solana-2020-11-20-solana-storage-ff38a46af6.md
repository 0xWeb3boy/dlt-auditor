# Root-Cause Card

## Metadata

- ID: `solana-2020-11-20-solana-storage-ff38a46af6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `remote-denial-of-service`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `freshness-and-origin-validation`

## Violated Invariant

- Protocol input must satisfy freshness and origin validation before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

Bloom<T> did not validate that its bits vector was non-empty at the sanitization boundary, allowing malformed serialized or received Bloom filters to reach arithmetic that assumes a positive bit length.

## Impact Pattern

- Primary impact: availability
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch fixes a validator panic reachable through over-the-wire pull requests by making Bloom<T>::sanitize() reject empty bit vectors. The supported vulnerability is denial of service through malformed Bloom filter input causing division by zero, not state corruption, cryptographic bypass, arbitrary code execution, or a proven consensus safety failure.
