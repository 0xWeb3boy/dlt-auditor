# Code-Shape Card

## Metadata

- ID: `solana-2023-01-31-solana-cryptography-a5af54669a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit`

## Code Shape Summary

The patch adds a feature-gated 64 MiB cap on total loaded account data during Solana transaction account loading and introduces a dedicated transaction error when the cap is exceeded. The evidence supports resource-control hardening in a critical runtime path, but does not establish a concrete exploit, crash, or network denial-of-service scenario.

## Search Motifs

- search for missing resource limit checks near cryptography entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add feature-gated resource accounting in the transaction account-loading path, enforce a fixed upper bound, and return a dedicated transaction error on violation.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
