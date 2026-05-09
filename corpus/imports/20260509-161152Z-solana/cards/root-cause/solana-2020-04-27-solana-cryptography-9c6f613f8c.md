# Root-Cause Card

## Metadata

- ID: `solana-2020-04-27-solana-cryptography-9c6f613f8c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`
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

Missing type-level validation for deserialized protocol objects. The supplied evidence shows that malformed CRDS data, votes, epoch slots, or transactions could be represented unless equivalent validation occurred elsewhere; it does not show whether all deserialization paths actually accepted such values unchecked.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The evidence supports a likely security fix for missing sanitization of deserialized Solana protocol objects. The patch adds explicit `Sanitize` implementations and structural checks for `CrdsData`, `Vote`, `EpochSlots`, and `Transaction`. The commit subject claims financial impact, but the provided hunks do not establish the exact SOL-earning mechanism, exploit path, or affected call sites.
