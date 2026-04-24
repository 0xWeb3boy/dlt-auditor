# Code-Shape Card

## Metadata

- ID: `sui-2023-02-21-sui-transaction-processing-d965c19fd2`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## Code Shape Summary

- The patch fixes unchecked aggregation of pay transaction recipient amounts. Previously, check_total_coins() summed u64 amounts with amounts.iter().sum() before comparing the result to available coin value. The patch uses checked_add and returns TotalAmountOverflow if the aggregate exceeds u64.

## Search Motifs

- arithmetic-bounds enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- unchecked arithmetic on protocol-controlled values
- conversion or aggregation before range validation

## Typical Asymmetry

- The transaction-processing sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Replace unchecked monetary aggregation with checked accumulation and reject overflow as a validation error before balance comparison or state mutation.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
