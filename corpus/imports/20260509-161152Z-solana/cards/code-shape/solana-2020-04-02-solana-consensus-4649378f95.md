# Code-Shape Card

## Metadata

- ID: `solana-2020-04-02-solana-consensus-4649378f95`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-gating`

## Code Shape Summary

The patch changes Solana ReplayStage fork vote selection so `tower.check_switch_threshold(...)` is evaluated for the heaviest candidate bank and `switch_threshold` is required in the final vote condition. This is consensus-sensitive and may be security relevant, but the supplied evidence does not establish a concrete vulnerability, exploit path, or confirmed safety impact.

## Search Motifs

- search for consensus vote gating checks near consensus entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Make the consensus predicate an explicit gate at the vote decision point instead of relying on fork-classification shortcuts and post-vote bookkeeping.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
