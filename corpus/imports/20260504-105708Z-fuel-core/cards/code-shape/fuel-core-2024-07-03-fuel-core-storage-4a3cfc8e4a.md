# Code-Shape Card

## Metadata

- ID: `fuel-core-2024-07-03-fuel-core-storage-4a3cfc8e4a`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-consensus-parameter-validation`

## Code Shape Summary

- A checked transaction type carried validation status but not the consensus ruleset version, so executor code could not distinguish fresh checks from stale cache entries.

## Search Motifs

- CheckedTransaction without consensus_parameters_version
- MaybeCheckedTransaction trusted by executor
- parameter upgrade with cached txpool entries
- recheck transaction if version differs

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Attach consensus-parameter version metadata to checked transactions and force the executor to compare or revalidate when the block version differs.

## False Match Warnings

- No issue if cached validation is invalidated on every parameter update.
- No issue if executor always revalidates against block header parameters before inclusion.
