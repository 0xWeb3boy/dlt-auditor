# Code-Shape Card

## Metadata

- ID: `solana-2020-04-27-solana-cryptography-8ef097bf6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-input-validation`

## Code Shape Summary

The patch is best characterized as a likely security fix for missing structural validation after deserialization. The provided evidence shows new `Sanitize` implementations for CRDS payloads, gossip votes, epoch slots, and transactions, with bounds and consistency checks added before nested values are trusted. The exact exploit path or monetary impact is not established by the supplied snippets.

## Search Motifs

- search for missing input validation checks near cryptography entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit post-deserialization sanitization on protocol data types, reject out-of-range or structurally inconsistent fields, and recursively sanitize nested values before downstream processing.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
