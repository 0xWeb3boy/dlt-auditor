# Validation Card

## Metadata

- ID: `oasis-core-2021-05-24-oasis-core-transaction-processing-25f10e879`
- Bug family: `resource_accounting_and_limits`
- Bug class: `improper-resource-limit-enforcement`

## What Confirmed The Issue

- Evidence 1: The patch changes txpool admission checks to consume CheckedTransaction objects, enforces configured weight limits through tx.Weight(w), updates the add path to validate the checked transaction directly, and adjusts scheduler/test code to batch checked transactions and remove them by hash.
- Evidence 2: The source finding states the invariant explicitly: Txpool admission and batching should enforce configured transaction resource limits using the runtime's checked transaction metadata, not just raw byte length.

## What Could Have Invalidated It

- Compensating control 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Compensating control 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Caution 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.
