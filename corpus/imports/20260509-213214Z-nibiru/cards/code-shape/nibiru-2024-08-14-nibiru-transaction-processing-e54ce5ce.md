# Code-Shape Card

## Metadata

- ID: `nibiru-2024-08-14-nibiru-transaction-processing-e54ce5ce`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-or-state-drift`

## Code Shape Summary

- A bridge conversion path treated all token mappings the same and minted native coins where bank-origin mappings should burn representation and release backing.

## Search Motifs

- MintCoins inside ERC20-to-bank conversion
- mapping has IsMadeFromCoin or origin flag ignored
- module account balance checked in regression
- burn moved before SendCoinsFromModuleToAccount

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Branch conversion accounting by token origin: burn returned representation for bank-origin mappings and transfer existing module-held backing instead of minting new bank supply.

## False Match Warnings

- Do not flag ERC20-origin mappings that legitimately mint/burn native representation
- Need evidence of runtime mint/burn path, not only metadata setup
- Direct theft should not be claimed unless module balances are withdrawable by attacker
