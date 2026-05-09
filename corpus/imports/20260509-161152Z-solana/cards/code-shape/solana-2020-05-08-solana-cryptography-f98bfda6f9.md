# Code-Shape Card

## Metadata

- ID: `solana-2020-05-08-solana-cryptography-f98bfda6f9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `disabled-signature-verification-path`

## Code Shape Summary

The supported finding is security hardening: the patch removes code paths that could disable signature verification in validator vote and shred processing. The evidence supports removal of unsafe bypass configuration, but not a proven remotely exploitable vulnerability or committed-state impact.

## Search Motifs

- search for disabled signature verification path checks near cryptography entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Remove disabled-verifier branches from validator packet verification paths and instantiate concrete signature verifiers unconditionally.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
