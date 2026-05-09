# Root-Cause Card

## Metadata

- ID: `solana-2020-11-19-solana-storage-a8c29505f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-dos`
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

Bloom<T> lacked validation for the invariant that its bit vector must be non-empty. Malformed over-the-wire pull request data could therefore pass sanitization and later reach Bloom position logic that divides by the bit vector length, causing division by zero and a validator panic.

## Impact Pattern

- Primary impact: availability
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch is a confirmed security fix for a remotely triggerable validator panic in Solana gossip pull handling. The evidence shows Bloom<T> sanitization changed from a no-op to rejecting empty bit vectors, matching the commit message that over-the-wire pull requests could cause division by zero in bloom filters.
