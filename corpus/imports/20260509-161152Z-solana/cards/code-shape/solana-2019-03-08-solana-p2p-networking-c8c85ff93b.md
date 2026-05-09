# Code-Shape Card

## Metadata

- ID: `solana-2019-03-08-solana-p2p-networking-c8c85ff93b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `gossip-signature-integrity`

## Code Shape Summary

The patch changes Solana gossip initialization so the local self ContactInfo is inserted through a dedicated insert_self path instead of the generic insert_info path. The new path checks that node_info.id matches the local node id, signs the ContactInfo with the local keypair, and only then inserts it into CRDS. This supports a likely security fix for preventing incorrectly signed self gossip records, though the provided evidence does not establish remo...

## Search Motifs

- search for gossip signature integrity checks near p2p-networking entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Use a self-specific insertion path for identity-bearing gossip records. Enforce the local identity match before signing, sign with the local keypair, and reject mismatched self records instead of passing them through generic CRDS insertion.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
