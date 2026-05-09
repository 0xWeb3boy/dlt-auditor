# Root-Cause Card

## Metadata

- ID: `solana-2018-12-01-solana-cryptography-34c3a0cc1f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `gossip-signature-verification-hardening`
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

The provided evidence indicates that CRDS gossip records did not yet have uniform value-level signature support across the shown variants, and prune messages lacked the added structured freshness and destination-aware validation parameters. The excerpts do not prove exactly where unsigned records were accepted, so the root cause should be limited to missing or incomplete authentication/freshness validation support in the shown gossip paths.

## Impact Pattern

- Primary impact: gossip-message-integrity
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch is likely a security fix for Solana CRDS gossip. The strongest grounded evidence is that CRDS value variants gain signature-bearing data and `Signable` sign/verify dispatch, while prune-message handling gains destination, wallclock, current-time, expiration, and error-return behavior. The evidence supports missing signature-verification and freshness validation in the gossip subsystem, but it does not show a complete exploit path or every enfo...
