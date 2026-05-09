# Code-Shape Card

## Metadata

- ID: `solana-2022-05-25-solana-cryptography-880684565c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `packet-payload-boundary-hardening`

## Code Shape Summary

The patch encapsulates Packet's backing buffer and migrates call sites to use Packet::data() for meta.size-bounded reads and Packet::buffer_mut() for full-buffer writes. This is plausibly security-relevant hardening because ledger shred signing and verification now read through the bounded accessor, but the supplied evidence does not establish a concrete vulnerability, exploit path, signature forgery, replay acceptance, consensus failure, or memory-safe...

## Search Motifs

- search for packet payload boundary hardening checks near cryptography entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Encapsulate the raw packet buffer and provide separate APIs for bounded immutable reads and full-capacity mutable writes, then migrate readers to the bounded accessor.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
