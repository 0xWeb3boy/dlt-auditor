# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m09-bank-balance-parse-error-panic`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-parse-error-return-before-bank-read`

## Code Shape Summary

- bankBalance assigned addrEth, addrBech32, bankDenom, err but immediately called Bank.GetBalance without checking err.

## Search Motifs

- parseArgsBankBalance err ignored
- Bank.GetBalance after parse error
- HandleOutOfGasPanic only catches sdk.ErrorOutOfGas
- ErrInvalidArgs missing

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Check the parse error immediately, wrap it as ErrInvalidArgs, and return before any bank keeper lookup.

## False Match Warnings

- No issue if the parse helper cannot return malformed zero values.
- No issue if all panics are safely recovered and converted to EVM errors.
- No issue if err is checked before any bank keeper call.
