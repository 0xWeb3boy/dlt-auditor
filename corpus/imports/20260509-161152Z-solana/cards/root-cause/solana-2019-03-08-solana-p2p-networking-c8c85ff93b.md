# Root-Cause Card

## Metadata

- ID: `solana-2019-03-08-solana-p2p-networking-c8c85ff93b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `gossip-signature-integrity`
- Confidence tier: `tier_a_confirmed`

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

The self ContactInfo initialization path used a generic insertion function rather than a dedicated self-record path with an explicit identity match check and local signing step. Based on the shown diff and commit subject, this could allow propagation of self gossip data whose signature did not correspond cleanly to the advertised identity.

## Impact Pattern

- Primary impact: integrity
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Medium

## Short Reusable Lesson

The patch changes Solana gossip initialization so the local self ContactInfo is inserted through a dedicated insert_self path instead of the generic insert_info path. The new path checks that node_info.id matches the local node id, signs the ContactInfo with the local keypair, and only then inserts it into CRDS. This supports a likely security fix for preventing incorrectly signed self gossip records, though the provided evidence does not establish remo...
