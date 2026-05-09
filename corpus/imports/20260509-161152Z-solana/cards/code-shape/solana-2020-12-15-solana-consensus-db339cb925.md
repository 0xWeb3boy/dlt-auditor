# Code-Shape Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-db339cb925`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-ordering-race`

## Code Shape Summary

The patch likely fixes a consensus-relevant race in Solana's bank runtime. `Bank::register_tick` previously made the boundary tick height visible before completing blockhash queue and recent blockhashes sysvar updates, while ReplayStage could use that boundary tick height as the signal to begin accounts delta hash calculation. The patch reorders the tick-height increment after those updates and strengthens the guard to reject tick registration once free...

## Search Motifs

- search for consensus state ordering race checks near consensus entrypoints
- compare validation before and after the state-root-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Delay publication of the externally observed boundary state until dependent state updates are complete, and strengthen the lifecycle guard around freeze-sensitive mutation.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
