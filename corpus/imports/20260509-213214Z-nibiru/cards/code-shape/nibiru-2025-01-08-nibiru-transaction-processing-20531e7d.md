# Code-Shape Card

## Metadata

- ID: `nibiru-2025-01-08-nibiru-transaction-processing-20531e7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-or-state-drift`

## Code Shape Summary

- A conversion path burned native bank representation based on a token-reported received amount instead of the original input amount, allowing fee-on-transfer behavior to skew supply accounting.

## Search Motifs

- actualSentAmount used as burn amount
- fee-charging ERC20 regression test
- convertCoinToEvmBornERC20 burns transfer result
- input coin amount differs from ERC20 transfer output

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Burn or debit the full original input amount for native accounting, while treating token transfer return values only as ERC20-side execution results.

## False Match Warnings

- Do not flag ordinary ERC20 transfers where output amount is intentionally the asset delivered
- Need a native supply burn/debit tied to token callback result
- Fee-on-transfer support may intentionally account for net amount if no native supply was pre-accepted
