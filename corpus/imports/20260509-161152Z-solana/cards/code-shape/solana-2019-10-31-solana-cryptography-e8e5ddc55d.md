# Code-Shape Card

## Metadata

- ID: `solana-2019-10-31-solana-cryptography-e8e5ddc55d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-ledger-validation`

## Code Shape Summary

The patch adds explicit PoH/tick validation in Solana replay and blocktree processing paths. The strongest grounded claim is that replayed or loaded entries were missing explicit checks for tick hash counts and slot tick counts in the shown paths, and the patch rejects mismatches with typed block errors. The evidence supports a consensus/ledger-integrity hardening or likely security fix, but not a proven exploit or demonstrated network-level compromise.

## Search Motifs

- search for consensus ledger validation checks near cryptography entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit pre-processing validation for PoH/tick invariants and reject mismatches through typed ledger/block errors before replay processing or bank freeze continues.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
