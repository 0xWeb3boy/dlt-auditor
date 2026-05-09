# Code-Shape Card

## Metadata

- ID: `solana-2020-11-20-solana-storage-0ad7b64961`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-input-validation`

## Code Shape Summary

The patch adds explicit sanitization for Bloom filters used in Solana gossip pull handling. Previously, `Bloom<T>` had a default no-op `Sanitize` implementation, allowing an empty `bits` vector to pass validation. The commit message states that over-the-wire pull requests could trigger a validator panic through division by zero in Bloom filter logic. The fix rejects empty Bloom filters with `SanitizeError::InvalidValue`.

## Search Motifs

- search for missing input validation checks near storage entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace default/no-op protocol data sanitization with an explicit structural invariant check that rejects malformed input before downstream calculations depend on invalid dimensions.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
