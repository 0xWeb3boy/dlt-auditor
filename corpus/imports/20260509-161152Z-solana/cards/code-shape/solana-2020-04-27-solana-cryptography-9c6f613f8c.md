# Code-Shape Card

## Metadata

- ID: `solana-2020-04-27-solana-cryptography-9c6f613f8c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`

## Code Shape Summary

The evidence supports a likely security fix for missing sanitization of deserialized Solana protocol objects. The patch adds explicit `Sanitize` implementations and structural checks for `CrdsData`, `Vote`, `EpochSlots`, and `Transaction`. The commit subject claims financial impact, but the provided hunks do not establish the exact SOL-earning mechanism, exploit path, or affected call sites.

## Search Motifs

- search for protocol input validation checks near cryptography entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit sanitization implementations at deserialization-facing protocol types, enforce scalar bounds and cross-field consistency, and recursively validate nested protocol values.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
