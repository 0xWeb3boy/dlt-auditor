# Code-Shape Card

## Metadata

- ID: `solana-2020-10-01-solana-staking-e3773d919c`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## Code Shape Summary

The provided evidence supports an overflow-prone rent distribution calculation in Solana runtime accounting, but it does not establish an exploitable security vulnerability. The patch replaces `u64` intermediate multiplication in validator rent-share calculation with feature-gated `u128` arithmetic and tightens leftover lamport handling. This is plausibly security-relevant consensus/economic hardening, but the vulnerability thesis is not proven from the...

## Search Motifs

- search for integer overflow checks near staking entrypoints
- compare validation before and after the checked-arithmetic-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Use widened integer arithmetic for proportional accounting calculations and enforce the post-distribution accounting invariant at the point where the distribution is computed.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
