# Code-Shape Card

## Metadata

- ID: `sui-2023-02-27-sui-transaction-processing-f88a9a6cb6`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## Code Shape Summary

- The patch hardens Sui pay transaction accounting against u64 overflow when summing coin balances. The strongest supported claim is integer-overflow hardening in coin payment execution, not a proven exploit, denial of service, theft, or consensus failure.

## Search Motifs

- arithmetic-bounds enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- unchecked arithmetic on protocol-controlled values
- conversion or aggregation before range validation

## Typical Asymmetry

- The transaction-processing sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Replace unchecked monetary aggregate arithmetic with checked_add accumulation and return explicit execution errors for unrepresentable totals. Split failure statuses so requested payment amount overflow and aggregate coin balance overflow are distinguishable.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
