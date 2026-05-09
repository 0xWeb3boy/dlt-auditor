# Root-Cause Card

## Metadata

- ID: `solana-2020-11-20-solana-storage-0ad7b64961`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-input-validation`
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

Missing validation at the wire-input sanitization boundary for Bloom filters. A malformed Bloom filter with an empty bit vector could be accepted and later used by Bloom position logic that depended on the bit-vector length, leading to division by zero and validator panic.

## Impact Pattern

- Primary impact: denial-of-service
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch adds explicit sanitization for Bloom filters used in Solana gossip pull handling. Previously, `Bloom<T>` had a default no-op `Sanitize` implementation, allowing an empty `bits` vector to pass validation. The commit message states that over-the-wire pull requests could trigger a validator panic through division by zero in Bloom filter logic. The fix rejects empty Bloom filters with `SanitizeError::InvalidValue`.
