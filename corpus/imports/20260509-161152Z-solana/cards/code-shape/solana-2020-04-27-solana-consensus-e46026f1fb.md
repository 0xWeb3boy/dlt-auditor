# Code-Shape Card

## Metadata

- ID: `solana-2020-04-27-solana-consensus-e46026f1fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-deserialization-validation`

## Code Shape Summary

The patch is best classified as a likely security fix for missing post-deserialization validation. The provided hunks show new `Sanitize` implementations for CRDS slot-related values, votes, and transactions, adding bounds checks and structural consistency checks that were not shown before. The commit subject directly frames the issue as unsanitized deserialized input with SOL-impacting consequences, but the supplied evidence does not establish the full...

## Search Motifs

- search for missing deserialization validation checks near consensus entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit `Sanitize` implementations at deserialization-facing protocol data boundaries, reject invalid values with `SanitizeError`, and recursively validate nested protocol objects before downstream use.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
