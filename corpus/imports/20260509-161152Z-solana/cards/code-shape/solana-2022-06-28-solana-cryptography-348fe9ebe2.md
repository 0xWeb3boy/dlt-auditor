# Code-Shape Card

## Metadata

- ID: `solana-2022-06-28-solana-cryptography-348fe9ebe2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `late-network-input-validation`

## Code Shape Summary

The patch moves basic shred discard checks into the fetch stage so malformed, stale, out-of-range, wrong-version, or out-of-bounds-index shreds are dropped earlier. The evidence supports a resource-saving validation change on network input, but it does not establish a concrete vulnerability, exploit path, consensus bypass, or demonstrated denial-of-service condition.

## Search Motifs

- search for late network input validation checks near cryptography entrypoints
- compare validation before and after the stake-accountability-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Consolidate basic packet-header validation into an early fetch-stage discard predicate and return explicit reject decisions with stats counters for each failure mode.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
