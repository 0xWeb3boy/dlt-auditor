# Code-Shape Card

## Metadata

- ID: `solana-2020-04-02-solana-consensus-0139236464`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-guard-hardening`

## Code Shape Summary

The patch changes Solana `ReplayStage` fork-voting logic so `switch_threshold` is computed with `tower.check_switch_threshold(...)`, failure is recorded explicitly, and the final vote predicate requires `switch_threshold`. This is consensus-relevant logic, but the supplied evidence does not prove a security vulnerability, exploit path, network split, or finalized consensus divergence. Treat as unclear rather than a confirmed or likely security fix.

## Search Motifs

- search for consensus vote guard hardening checks near consensus entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Compute the switch-threshold decision before voting, surface threshold failure in fork-selection diagnostics, and include the threshold result in the final vote predicate.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
