# Code-Shape Card

## Metadata

- ID: `moonbeam-2026-01-08-moonbeam-staking-3c23690363`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-corruption`

## Code Shape Summary

- Validation checked a new decrease in isolation while reward snapshot code aggregated all pending decreases. The fix sums pending decreases during validation and caps accounting by actual bonded amount.

## Search Motifs

- multiple pending Decrease requests for same delegation
- uncounted_stake updated from pending amount without min(amount, bond)
- MinDelegation check ignores scheduled_requests total

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Apply cumulative pending-request validation and cap derived reward accounting at the actual bonded balance before payout math.

## False Match Warnings

- Single pending action per pair enforced by storage key uniqueness is safe
- Pending decreases not used in payout denominator are lower impact
- Capping at bond amount elsewhere may neutralize aggregation overflow
