# Code-Shape Card

## Metadata

- ID: `fuel-core-2024-03-09-fuel-core-storage-a31f64be15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `txpool-blacklist-enforcement`

## Code Shape Summary

- Txpool insertion accepted structurally valid transactions before walking inputs and comparing referenced UTXO ids against a denylist.

## Search Motifs

- txpool insert before blacklist check
- Input::Coin utxo_id not compared to denylist
- blacklisted_utxo_id regression test
- NotInserted error handling hides policy failure

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Add a pre-insertion blacklist check over coin inputs, surface a specific insertion error, and cover rejection with regression tests.

## False Match Warnings

- A blacklist feature that is purely informational is not security-relevant.
- Consensus-valid transactions should not be rejected globally unless this is explicitly local policy.
