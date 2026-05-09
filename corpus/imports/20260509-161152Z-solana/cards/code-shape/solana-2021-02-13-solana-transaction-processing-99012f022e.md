# Code-Shape Card

## Metadata

- ID: `solana-2021-02-13-solana-transaction-processing-99012f022e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-size-validation`

## Code Shape Summary

The patch adds a maximum base58 string length check to Solana SDK Hash parsing. Hash::from_str now rejects strings longer than 44 characters with ParseHashError::WrongSize before calling bs58::decode. This is grounded as input-size validation and parser hardening, but the evidence does not prove a vulnerability or show that oversized input causes a security impact.

## Search Motifs

- search for input size validation checks near transaction-processing entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add an early encoded-input length guard before decoding fixed-size base58 data, while retaining the decoded-byte-length check.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
