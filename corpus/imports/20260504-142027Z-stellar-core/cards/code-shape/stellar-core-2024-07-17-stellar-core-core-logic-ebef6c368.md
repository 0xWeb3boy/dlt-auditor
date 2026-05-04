# Code-Shape Card

## Metadata

- ID: `stellar-core-2024-07-17-stellar-core-core-logic-ebef6c368`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hash-collision-dos-hardening`

## Code Shape Summary

- A collision-sensitive filter used predictable hash mixing and an unbounded construction retry loop before switching to SipHash24 and capped retries.

## Search Motifs

- Murmur hash in collision sensitive filter
- for loop retrying population without bound
- SipHash24 added with seed
- population retry capped after collisions

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Replace predictable hash mixing with keyed SipHash for placement and lookup, and cap collision-retry loops with failure handling.

## False Match Warnings

- Non-adversarial offline filters may not require keyed hashing.
- Bounded input sizes can limit collision impact.
- Cryptographic hashing is not always required for internal deterministic structures.
