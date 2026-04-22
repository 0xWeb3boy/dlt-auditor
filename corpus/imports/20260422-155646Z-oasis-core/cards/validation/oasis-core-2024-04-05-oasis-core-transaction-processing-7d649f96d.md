# Validation Card

## Metadata

- ID: `oasis-core-2024-04-05-oasis-core-transaction-processing-7d649f96d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-gas-accounting`

## What Confirmed The Issue

- Evidence 1: The patch inserts the same sequence into each affected handler: load consensus gas parameters, debit gas with the matching 'GasOp' constant, fail on charging error, then return early for simulation. This makes the handlers consistently enforce their configured gas cost before further processing.
- Evidence 2: The source finding states the invariant explicitly: These consensus handlers are expected to account for operation-specific gas before deeper processing, and simulation should reflect the same accounting for fee estimation.

## What Could Have Invalidated It

- Compensating control 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Compensating control 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Caution 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.
