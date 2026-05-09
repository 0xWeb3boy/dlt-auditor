# Code-Shape Card

## Metadata

- ID: `solana-2023-02-15-solana-cryptography-cf0a149add`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-commitment-hardening`

## Code Shape Summary

The patch removes the embedded Merkle root from serialized Merkle shred branch data, changes proof handling from root-plus-proof branches to proof-only data, and updates tests so signed data resolves to `SignedData::MerkleRoot`. This is plausibly security relevant because it changes cryptographic commitment handling, but the evidence does not prove a vulnerability in the previous behavior. Treat as unclear hardening/layout work rather than a validated s...

## Search Motifs

- search for signature commitment hardening checks near cryptography entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Change the serialized Merkle shred format so proof data no longer carries an embedded root, and use the Merkle root commitment as the canonical signed data.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
