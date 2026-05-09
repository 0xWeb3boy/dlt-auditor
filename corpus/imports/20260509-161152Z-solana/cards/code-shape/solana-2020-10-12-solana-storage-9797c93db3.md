# Code-Shape Card

## Metadata

- ID: `solana-2020-10-12-solana-storage-9797c93db3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-native-loader-input`

## Code Shape Summary

The patch hardens Solana's runtime native-loader path by replacing unchecked first-account access and several panic paths with explicit error returns. The evidence supports improved handling for empty account lists, invalid UTF-8 account data, empty or leading-NUL native names, executable path failures, missing entrypoints, and library load failures. However, the supplied material does not prove that these conditions were reachable by an untrusted trans...

## Search Motifs

- search for panic on invalid native loader input checks near storage entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Convert panic-prone native-loader failure handling into explicit Result propagation, and validate account-derived loader inputs before use.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
