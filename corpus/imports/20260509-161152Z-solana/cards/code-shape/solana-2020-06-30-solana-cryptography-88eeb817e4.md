# Code-Shape Card

## Metadata

- ID: `solana-2020-06-30-solana-cryptography-88eeb817e4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-restart-precondition-hardening`

## Code Shape Summary

The patch adds restart guard rails for Solana validator startup. `wait_for_supermajority` now returns an error signal when the configured wait slot is greater than the local bank slot, and startup exits on that signal. The validator config path also begins parsing `expected_bank_hash`. The evidence supports operational restart safety hardening, but does not establish a concrete vulnerability, attacker path, or exploitable consensus failure.

## Search Motifs

- search for validator restart precondition hardening checks near cryptography entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Convert a silent restart precondition helper into an explicit fail-fast guard, and propagate configured expected state into validator configuration.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
