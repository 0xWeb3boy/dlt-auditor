# Code-Shape Card

## Metadata

- ID: `fuel-core-2025-04-17-fuel-core-storage-103c019fa1`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `missing-utxo-consumption`

## Code Shape Summary

- The executor consumed standard coin inputs in storage but the match arm skipped DataCoinSigned and DataCoinPredicate variants, creating asymmetric spend cleanup.

## Search Motifs

- Input::DataCoinSigned missing from spend_input_utxos
- Input::DataCoinPredicate missing from utxo prune
- second data coin spend succeeds
- match arm covers coin but not data coin

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Add all data coin input variants to the spend-pruning match and add a regression test that commits one spend before rejecting or skipping the second.

## False Match Warnings

- No issue if data coin inputs are non-spendable metadata only.
- No issue if another storage layer consumes data coins before commit.
