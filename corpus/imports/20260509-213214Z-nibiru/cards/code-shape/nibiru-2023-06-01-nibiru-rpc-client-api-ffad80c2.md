# Code-Shape Card

## Metadata

- ID: `nibiru-2023-06-01-nibiru-rpc-client-api-ffad80c2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-margin-ratio-check`

## Code Shape Summary

- A margin-removal path needed a shared final-state collateralization check before vault withdrawal. The pattern is missing invariant enforcement after applying funding and margin deltas.

## Search Motifs

- RemoveMargin withdraws before final margin check
- helper computes margin ratio but not used on all mutation paths
- spot and TWAP notionals used inconsistently
- vault withdrawal follows local state mutation without validation

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Introduce one margin-ratio helper, call it from every position mutation path after all deltas are applied, and block vault withdrawals when the final position is liquidatable.

## False Match Warnings

- Do not flag read-only margin queries
- Do not overstate if the path only refactors existing equivalent checks
- A check before mutation is insufficient if funding or withdrawal changes the final state
