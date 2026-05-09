# Code-Shape Card

## Metadata

- ID: `solana-2019-06-20-solana-cryptography-aacb38864c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-fork-replay-handling`

## Code Shape Summary

The patch improves Solana replay-stage dead-fork handling by classifying some replay failures as fatal, marking the affected slot dead, and skipping forks already marked dead in replay progress. The evidence supports consensus-replay correctness and possible security relevance, but it does not establish an exploitable vulnerability, finalized consensus divergence, fund loss, or attacker control.

## Search Motifs

- search for invalid fork replay handling checks near cryptography entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Detect fatal replay failures, record the affected slot as dead, and avoid replaying slots already marked dead.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
