# Code-Shape Card

## Metadata

- ID: `solana-2018-10-26-solana-transaction-processing-cda9ad8565`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `incomplete-signature-verification`

## Code Shape Summary

The patch likely fixes incomplete packet-level signature verification for transactions with multiple signatures. In src/sigverify.rs::verify_packet, the old code performed one Ed25519 signature::verify call, while the patched code loops over sig_len, checks each signature/public-key range against packet.meta.size, and verifies each pair over the message. The evidence supports a cryptographic authorization bug at the packet verifier level, but does not e...

## Search Motifs

- search for incomplete signature verification checks near transaction-processing entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace a single cryptographic authorization check with cardinality-aware verification over all declared authorization entries, with bounds checks before slicing untrusted packet data.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
