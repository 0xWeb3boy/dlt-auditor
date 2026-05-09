# Code-Shape Card

## Metadata

- ID: `solana-2020-08-17-solana-staking-d9ae092637`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-recheck-bypass`

## Code Shape Summary

The patch likely fixes a protocol accounting issue in Solana's runtime rent handling. Previously, an existing account that was rent-exempt during collection could have `rent_epoch` advanced to the next epoch even though no rent was collected. The new behavior keeps exempt accounts at the current epoch, allowing exemption to be checked again later in that epoch.

## Search Motifs

- search for rent exemption recheck bypass checks near staking entrypoints
- compare validation before and after the rent-exemption-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Separate eligibility-state advancement for actual rent collection from the handling of accounts that are only currently rent-exempt.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
