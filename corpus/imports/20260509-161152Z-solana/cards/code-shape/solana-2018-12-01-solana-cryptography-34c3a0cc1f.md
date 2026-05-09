# Code-Shape Card

## Metadata

- ID: `solana-2018-12-01-solana-cryptography-34c3a0cc1f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `gossip-signature-verification-hardening`

## Code Shape Summary

The patch is likely a security fix for Solana CRDS gossip. The strongest grounded evidence is that CRDS value variants gain signature-bearing data and `Signable` sign/verify dispatch, while prune-message handling gains destination, wallclock, current-time, expiration, and error-return behavior. The evidence supports missing signature-verification and freshness validation in the gossip subsystem, but it does not show a complete exploit path or every enfo...

## Search Motifs

- search for gossip signature verification hardening checks near cryptography entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add authentication and freshness validation support at the CRDS gossip value and prune-message boundaries.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
