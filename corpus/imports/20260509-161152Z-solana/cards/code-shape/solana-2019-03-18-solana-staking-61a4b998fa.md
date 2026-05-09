# Code-Shape Card

## Metadata

- ID: `solana-2019-03-18-solana-staking-61a4b998fa`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-safety-hardening`

## Code Shape Summary

The evidence supports that this commit implements Solana locktower voting and related VoteState helpers/tests. It replaces placeholder latest-slot voting with locktower-oriented bank selection inputs, but the provided evidence does not establish a concrete vulnerability, attacker path, or exploitable consensus failure. Treat this as security-relevant protocol mechanism work, not a validated vulnerability fix.

## Search Motifs

- search for consensus vote safety hardening checks near staking entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Implement consensus vote-selection support by adding fork ancestry data, integrating locktower voting into replay, and adding VoteState helper/test coverage.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
