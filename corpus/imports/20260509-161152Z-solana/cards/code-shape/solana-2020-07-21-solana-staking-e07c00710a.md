# Code-Shape Card

## Metadata

- ID: `solana-2020-07-21-solana-staking-e07c00710a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reward-accounting-invariant`

## Code Shape Summary

The patch fixes reward-accounting correctness in Solana's staking reward path. The evidence supports changes to reward value representation, staker/voter reward ordering, reward point calculation support, and post-payment assertions that compare observed paid rewards with recorded and allocated rewards. It does not establish an exploitable vulnerability or attacker-controlled path, so the security classification should remain unclear rather than confirm...

## Search Motifs

- search for reward accounting invariant checks near staking entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Tighten reward accounting by using structured reward value handling, correcting reward tuple ordering, deriving/checking reward amounts explicitly, and adding assertions for post-payment consistency.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
