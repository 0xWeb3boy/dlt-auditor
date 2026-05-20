# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m05-wei-native-fee-units`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fee-unit-conversion-mismatch`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `denomination unit conversion`

## Violated Invariant

- Invariant: Fee amounts stored as native bank coins must be converted from wei into the native denomination before validation, display, or AuthInfo construction.

## Trust Boundary

- Boundary: EVM transaction fee data->Cosmos SDK fee validation and tx builder

## Attack Surface

- Entrypoint type: ante handler fee validation and BuildTx
- Sensitive sink: AuthInfo.Fee and ValidateBasic fee denomination checks

## Impact Pattern

- Primary impact: fee denomination mismatch
- Secondary impact: underpayment or overpayment depending on path

## Short Reusable Lesson

- Fee validation and transaction building wrapped txData.Fee directly as a native denom coin even though the value was denominated in wei.
