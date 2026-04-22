# Code-Shape Card

## Metadata

- ID: `oasis-core-2024-04-05-oasis-core-transaction-processing-7d649f96d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-gas-accounting`

## Code Shape Summary

- Short description of what the buggy code looked like: Several key manager transaction handlers appear to have omitted explicit per-operation gas charging at the start of handler execution. The fix standardizes that charging pattern and aligns simulation behavior with live gas accounting.

## Search Motifs

- Motif 1: resource or gas accounting missing on one mutation path
- Motif 2: downstream queue failure logged but not returned to caller
- Motif 3: limits depend on metadata that is not preserved across stages

## Typical Asymmetry

- What was checked in one path but missing in another: One stage performed checking, but a later admission, batching, or execution stage skipped accounting or failed to propagate rejection.

## Patch Pattern

- What the fix changed structurally: The patch inserts the same sequence into each affected handler: load consensus gas parameters, debit gas with the matching 'GasOp' constant, fail on charging error, then return early for simulation. This makes the handlers consistently enforce their configured gas cost before further processing.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
