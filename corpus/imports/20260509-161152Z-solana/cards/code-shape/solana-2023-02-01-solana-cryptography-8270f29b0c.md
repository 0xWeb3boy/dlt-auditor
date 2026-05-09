# Code-Shape Card

## Metadata

- ID: `solana-2023-02-01-solana-cryptography-8270f29b0c`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit`

## Code Shape Summary

The patch adds a feature-gated cap on total loaded account data during Solana transaction account loading. The evidence supports resource-consumption hardening in the runtime account-loading path, not cryptography, replay, signature validation, consensus divergence, or proven exploitability.

## Search Motifs

- search for missing resource limit checks near cryptography entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add a feature-gated runtime resource budget, account for usage while loading transaction accounts, and reject transactions that exceed the budget with a dedicated error.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
