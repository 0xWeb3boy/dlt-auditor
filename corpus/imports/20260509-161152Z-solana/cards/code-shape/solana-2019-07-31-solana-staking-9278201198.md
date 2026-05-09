# Code-Shape Card

## Metadata

- ID: `solana-2019-07-31-solana-staking-9278201198`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-withdrawal-state-guard`

## Code Shape Summary

The grounded security-relevant change is in the stake withdrawal path. The patch adds an explicit rejection when `stake.deactivated == std::u64::MAX`, described in-code as still activated, and changes the withdrawal stake calculation from `clock.epoch` to `clock.stakers_epoch`. The supplied bank changes are test evidence for epoch vote-account accounting, not production runtime logic.

## Search Motifs

- search for missing withdrawal state guard checks near staking entrypoints
- compare validation before and after the stake-accountability-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add an explicit state guard before withdrawal and align stake-balance evaluation with the stakers epoch used by epoch stake accounting.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
