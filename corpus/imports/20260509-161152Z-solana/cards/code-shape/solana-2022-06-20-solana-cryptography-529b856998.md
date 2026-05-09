# Code-Shape Card

## Metadata

- ID: `solana-2022-06-20-solana-cryptography-529b856998`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `packet-buffer-read-boundary-hardening`

## Code Shape Summary

The patch centralizes immutable Packet reads through Packet::data(), which the commit describes as bounded to Packet.meta.size, and separates full-buffer writes through Packet::buffer_mut(). The evidence supports an API-boundary cleanup or hardening against accidental reads past the valid packet length, including in shred signing and verification paths. It does not establish a concrete vulnerability, exploit path, signature bypass, replay acceptance, at...

## Search Motifs

- search for packet buffer read boundary hardening checks near cryptography entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Encapsulate backing-buffer access so immutable reads are constrained to the valid packet length and full-capacity mutation requires an explicit mutable-buffer API.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
