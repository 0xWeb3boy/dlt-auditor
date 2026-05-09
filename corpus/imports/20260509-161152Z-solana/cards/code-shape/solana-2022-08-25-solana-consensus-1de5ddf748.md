# Code-Shape Card

## Metadata

- ID: `solana-2022-08-25-solana-consensus-1de5ddf748`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-overflow-hardening`

## Code Shape Summary

The patch adds checked arithmetic and fallible handling around Solana VoteStateUpdate and CompactVoteStateUpdate conversion. The evidence supports an arithmetic-overflow correctness and hardening change in vote-state compaction, but it does not establish a concrete vulnerability, exploit path, remote trigger, denial of service, or consensus divergence.

## Search Motifs

- search for arithmetic overflow hardening checks near consensus entrypoints
- compare validation before and after the checked-arithmetic-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace unchecked integer addition and infallible compact vote conversion with checked_add, Option/Result-returning conversion, and explicit caller-side failure handling.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
