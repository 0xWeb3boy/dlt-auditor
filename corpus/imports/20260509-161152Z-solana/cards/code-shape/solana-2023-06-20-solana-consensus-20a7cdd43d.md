# Code-Shape Card

## Metadata

- ID: `solana-2023-06-20-solana-consensus-20a7cdd43d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-exposure`

## Code Shape Summary

The patch appears to harden Solana's Bank HardForks API by replacing direct lock-based access with copied hard-fork data and Bank-mediated mutation. The commit message says callers could previously obtain read/write access to HardForks and that this could cause inconsistent handling of valid hard forks. However, the supplied evidence does not establish that an untrusted actor could exploit this, that consensus divergence occurred, or that the changed ca...

## Search Motifs

- search for consensus state exposure checks near consensus entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Encapsulate mutable consensus-adjacent state behind an owning API; return copies for read access and route mutation through methods that can enforce checks.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
