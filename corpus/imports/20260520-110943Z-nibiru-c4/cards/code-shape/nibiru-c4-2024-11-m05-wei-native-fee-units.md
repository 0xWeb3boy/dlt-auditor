# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m05-wei-native-fee-units`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fee-unit-conversion-mismatch`

## Code Shape Summary

- Fee validation and transaction building wrapped txData.Fee directly as a native denom coin even though the value was denominated in wei.

## Search Motifs

- sdkmath.NewIntFromBigInt(txData.Fee())
- NewCoin EVMBankDenom feeAmt
- WeiToNative missing
- AuthInfo.Fee txData.Fee unit inconsistency

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Convert fee values through WeiToNative before constructing native denom coins in validation and transaction-building paths.

## False Match Warnings

- No issue if the denomination is actually wei-denominated.
- No issue if a helper already converts txData.Fee before coin creation.
- Beware examples with 1 wei gas price if minimum transferable unit rules forbid them.
