# Code-Shape Card

## Metadata

- ID: `moonbeam-2026-01-08-moonbeam-staking-5f3e4b30c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-corruption`

## Code Shape Summary

- Request acceptance and reward accounting used inconsistent views of pending decreases. The patch aggregates scheduled decreases and clamps accounting to the real bond.

## Search Motifs

- bonded_amount - decrease_amount check ignores queued decreases
- pending decrease amount added to uncounted_stake unchecked
- regression test for stacked decreases breaking reward accounting

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Use one cumulative invariant for pending stake decreases across request admission and reward snapshot aggregation.

## False Match Warnings

- If request queue enforces one active decrease, cumulative validation is redundant
- If rewards are recomputed from actual balances only, denominator corruption may be non-security
- Administrative migration of stake requests has a different threat model
