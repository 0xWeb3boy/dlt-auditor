# Code-Shape Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-ef9f54b3d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-race`

## Code Shape Summary

The patch likely fixes a consensus-runtime race in Solana Bank tick registration. The grounded evidence is that tick_height was previously advanced before the blockhash/recent-blockhash sysvar boundary work completed, while the added comment states ReplayStage begins accounts delta hash calculation after observing the boundary tick height. The patch reorders tick publication after those updates and rejects tick registration once freezing has started.

## Search Motifs

- search for consensus state race checks near consensus entrypoints
- compare validation before and after the state-root-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Move publication of a consensus-observed boundary signal after the state it represents has been fully committed, and block concurrent mutation once freezing begins.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
