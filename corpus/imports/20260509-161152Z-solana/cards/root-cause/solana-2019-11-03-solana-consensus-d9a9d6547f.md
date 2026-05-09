# Root-Cause Card

## Metadata

- ID: `solana-2019-11-03-solana-consensus-d9a9d6547f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-identity-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

The supported root cause is an incorrect signing or identity-binding path for CRDS gossip values. The evidence indicates that signing logic was available through wrapper or per-variant `Signable` implementations and that at least one gossip identity check used a derived `pubkey()` accessor rather than the embedded `ContactInfo.id`. The exact replacement design and exploit path are not shown.

## Impact Pattern

- Primary impact: authenticity, identity-binding
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

Likely security fix for incorrect CRDS gossip signing. The evidence shows removal of `Signable` implementations for `CrdsValue`, `Vote`, and `EpochSlots`, and a related gossip pull-request identity check changed to compare `ContactInfo.id` directly. This supports a signature/identity-binding issue, but the supplied snippets do not prove exploitability, forged ledger state, economic impact, or direct consensus failure.
