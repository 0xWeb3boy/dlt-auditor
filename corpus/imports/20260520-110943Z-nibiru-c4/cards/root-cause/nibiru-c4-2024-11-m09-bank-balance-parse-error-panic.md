# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m09-bank-balance-parse-error-panic`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-parse-error-return-before-bank-read`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `error propagation before sensitive lookup`

## Violated Invariant

- Invariant: A precompile must stop on argument parse errors before passing decoded address or denom values into bank keeper state lookups.

## Trust Boundary

- Boundary: EVM caller ABI args->native bank keeper

## Attack Surface

- Entrypoint type: FunToken bankBalance precompile query
- Sensitive sink: BankKeeper.GetBalance with malformed address or denom arguments

## Impact Pattern

- Primary impact: panic from malformed precompile args
- Secondary impact: query/execution DoS for the affected path

## Short Reusable Lesson

- bankBalance assigned addrEth, addrBech32, bankDenom, err but immediately called Bank.GetBalance without checking err.
