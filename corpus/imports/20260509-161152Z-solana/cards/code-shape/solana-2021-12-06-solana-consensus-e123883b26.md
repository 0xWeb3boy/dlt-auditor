# Code-Shape Card

## Metadata

- ID: `solana-2021-12-06-solana-consensus-e123883b26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-rent-exemption-check`

## Code Shape Summary

The patch hardens Solana vote-account withdrawal handling by adding feature-gated Rent sysvar plumbing and making the post-withdraw balance explicit. The provided evidence supports that the change is intended to reject withdrawals that would create non-rent-exempt vote accounts, but it does not establish unauthorized withdrawal, fund theft, lamport creation, or a concrete consensus failure.

## Search Motifs

- search for missing rent exemption check checks near consensus entrypoints
- compare validation before and after the rent-exemption-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Pass required sysvar context into the state-transition function and validate the post-withdraw account lifecycle state under a feature gate.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
