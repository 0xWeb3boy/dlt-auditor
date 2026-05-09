# Code-Shape Card

## Metadata

- ID: `nibiru-2022-08-03-nibiru-storage-8c6e9717`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-margin-validation`

## Code Shape Summary

- A leveraged trading flow failed to consistently validate the final position state after updates. The reusable shape is a state transition that mutates margin exposure before enforcing maintenance-margin and bad-debt invariants.

## Search Motifs

- post-update margin ratio checked only on some paths
- tests treating extreme leverage or bad debt as success
- position update helpers that mutate margin before validation
- liquidation threshold check absent after withdraw/remove/update operations

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Centralize post-update solvency validation, run it after all position mutations and funding effects, return a typed margin-too-low error, and remove tests that bless bad-debt states.

## False Match Warnings

- Margin tests alone are not security evidence unless runtime acceptance changed
- Do not claim exploitability if only test setup or TWAP timing changed
- A later liquidation mechanism may reduce but not replace pre-commit solvency checks
