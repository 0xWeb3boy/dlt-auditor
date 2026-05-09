# Root-Cause Card

## Metadata

- ID: `solana-2020-04-27-solana-consensus-e46026f1fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-deserialization-validation`
- Confidence tier: `tier_b_likely`

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

Protocol objects could be deserialized without the specific local invariant checks shown in the patch. The supported root cause is missing or incomplete sanitization after deserialization, not a proven cryptographic bypass or a fully demonstrated balance-manipulation exploit.

## Impact Pattern

- Primary impact: protocol-integrity, input-validation
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch is best classified as a likely security fix for missing post-deserialization validation. The provided hunks show new `Sanitize` implementations for CRDS slot-related values, votes, and transactions, adding bounds checks and structural consistency checks that were not shown before. The commit subject directly frames the issue as unsanitized deserialized input with SOL-impacting consequences, but the supplied evidence does not establish the full...
