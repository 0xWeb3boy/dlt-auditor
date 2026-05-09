# Code-Shape Card

## Metadata

- ID: `solana-2019-11-03-solana-consensus-d9a9d6547f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-identity-binding`

## Code Shape Summary

Likely security fix for incorrect CRDS gossip signing. The evidence shows removal of `Signable` implementations for `CrdsValue`, `Vote`, and `EpochSlots`, and a related gossip pull-request identity check changed to compare `ContactInfo.id` directly. This supports a signature/identity-binding issue, but the supplied snippets do not prove exploitability, forged ledger state, economic impact, or direct consensus failure.

## Search Motifs

- search for signature identity binding checks near consensus entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Remove incorrect CRDS signing paths and use the concrete embedded identity for identity-sensitive gossip checks.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
