# Code-Shape Card

## Metadata

- ID: `solana-2020-11-20-solana-storage-ff38a46af6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `remote-denial-of-service`

## Code Shape Summary

The patch fixes a validator panic reachable through over-the-wire pull requests by making Bloom<T>::sanitize() reject empty bit vectors. The supported vulnerability is denial of service through malformed Bloom filter input causing division by zero, not state corruption, cryptographic bypass, arbitrary code execution, or a proven consensus safety failure.

## Search Motifs

- search for remote denial of service checks near storage entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Validate untrusted structured input at the sanitize boundary and reject impossible internal dimensions before arithmetic depends on them.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
