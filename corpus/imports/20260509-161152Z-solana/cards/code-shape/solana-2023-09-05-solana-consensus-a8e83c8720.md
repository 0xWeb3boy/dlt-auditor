# Code-Shape Card

## Metadata

- ID: `solana-2023-09-05-solana-consensus-a8e83c8720`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-duplicate-slot-state-recovery`

## Code Shape Summary

Likely consensus security fix in Solana replay handling. The patch makes ReplayStage recover duplicate-slot records from Blockstore and feed them into duplicate-slot state checking and fork-choice invalidation. The evidence supports a consensus-state synchronization issue, but does not prove exploitability, finality failure, fund loss, or attacker control.

## Search Motifs

- search for consensus duplicate slot state recovery checks near consensus entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Recover persisted duplicate-slot evidence from durable storage at replay initialization and state-transition boundaries, then apply the existing duplicate-state validation and fork-choice invalidation paths.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
