# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-11-08-oasis-core-transaction-processing-ba88a37cf`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-validator-set-minimum-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The shown code enforced only a non-empty validator election result, not a configured lower bound on validator-set size, and it did not validate that lower bound during initialization.

## Search Motifs

- Motif 1: resource or gas accounting missing on one mutation path
- Motif 2: downstream queue failure logged but not returned to caller
- Motif 3: limits depend on metadata that is not preserved across stages

## Typical Asymmetry

- What was checked in one path but missing in another: One stage performed checking, but a later admission, batching, or execution stage skipped accounting or failed to propagate rejection.

## Patch Pattern

- What the fix changed structurally: The patch propagates 'MinValidators' from scheduler parameters into the validator-election routine, adds an explicit undersized-set rejection in 'electValidators', and rejects non-positive 'MinValidators' during 'InitChain'.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
