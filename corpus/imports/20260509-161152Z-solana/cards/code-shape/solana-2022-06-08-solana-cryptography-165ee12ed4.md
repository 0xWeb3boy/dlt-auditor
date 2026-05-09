# Code-Shape Card

## Metadata

- ID: `solana-2022-06-08-solana-cryptography-165ee12ed4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-authority-validation`

## Code Shape Summary

The commit message states that durable nonce transactions not signed by the nonce authority are rejected. The shown code evidence supports part of that fix: nonce account verification now returns Option<Data> instead of a boolean, preserving initialized nonce account state for downstream validation. The exact authority-signature rejection branch is not present in the provided snippets, so this should be treated as a likely security fix rather than a ful...

## Search Motifs

- search for nonce authority validation checks near cryptography entrypoints
- compare validation before and after the nonce-state-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Return validated nonce account state instead of a lossy boolean so downstream code can enforce additional nonce-account invariants such as authority authorization.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
