# Code-Shape Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-75e9e321de`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-publication-race`

## Code Shape Summary

The patch fixes a race in Bank::register_tick where tick_height could be published before boundary-related account updates completed, while ReplayStage uses that boundary tick as a signal to start accounts delta hash calculation. The evidence supports a consensus/account-hash ordering bug, but does not establish remote exploitability, fund theft, signature bypass, or hash forgery.

## Search Motifs

- search for consensus state publication race checks near consensus entrypoints
- compare validation before and after the state-root-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Move publication of a concurrency-visible boundary signal until after the state it represents has been fully committed, and strengthen the guard against interleaving with freeze processing.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
