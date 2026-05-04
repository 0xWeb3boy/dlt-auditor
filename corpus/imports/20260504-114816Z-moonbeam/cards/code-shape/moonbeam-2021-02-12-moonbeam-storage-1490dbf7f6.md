# Code-Shape Card

## Metadata

- ID: `moonbeam-2021-02-12-moonbeam-storage-1490dbf7f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `historical-reward-accounting`

## Code Shape Summary

- A delayed payout function read live candidate/delegator state while settling rewards for an earlier round. The fix introduced/used round-indexed AtStake snapshots for payout weighting.

## Search Motifs

- pay_stakers reads live Candidates for round_to_payout
- reward payout delayed by BondDuration without snapshot use
- AtStake or exposure snapshot created but not consumed by settlement

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Record immutable per-round exposure and consume that snapshot during delayed settlement instead of querying mutable candidate state.

## False Match Warnings

- Live state reads are fine for same-block/current-round rewards
- Snapshots used only for reporting do not imply a payout bug
- Reward recalculation may be harmless if all recipients are recomputed from immutable events
