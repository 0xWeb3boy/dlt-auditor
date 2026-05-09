# Code-Shape Card

## Metadata

- ID: `solana-2021-01-20-solana-transaction-processing-2783aee483`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

The patch adds an early maximum-length check to Solana SDK signature parsing before calling `bs58::decode`. This is grounded as input validation and parser resource-bound hardening, but the provided evidence does not establish a concrete vulnerability such as authentication bypass, replay, consensus failure, or demonstrated denial of service.

## Search Motifs

- search for input validation checks near transaction-processing entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add a pre-decode length bound at the parser boundary, using explicit constants for the expected byte size and maximum encoded length while preserving the existing decoded-size validation.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
