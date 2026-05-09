# Root-Cause Card

## Metadata

- ID: `solana-2020-04-27-solana-cryptography-8ef097bf6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-input-validation`
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

Deserialized protocol and transaction objects lacked the structural validation now required by the patch. The grounded issue is missing post-deserialization sanitization, not a proven cryptographic bypass, memory corruption issue, or fully demonstrated SOL-earning exploit path.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch is best characterized as a likely security fix for missing structural validation after deserialization. The provided evidence shows new `Sanitize` implementations for CRDS payloads, gossip votes, epoch slots, and transactions, with bounds and consistency checks added before nested values are trusted. The exact exploit path or monetary impact is not established by the supplied snippets.
