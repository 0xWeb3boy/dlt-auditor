# Code-Shape Card

## Metadata

- ID: `oasis-core-2021-05-24-oasis-core-transaction-processing-25f10e879`
- Bug family: `resource_accounting_and_limits`
- Bug class: `improper-resource-limit-enforcement`

## Code Shape Summary

- Short description of what the buggy code looked like: Txpool admission logic was still tied to an older raw-byte interface and only the visible size-based check, so configured CheckedTransaction metadata such as per-weight limits was not enforced in that admission path.

## Search Motifs

- Motif 1: resource or gas accounting missing on one mutation path
- Motif 2: downstream queue failure logged but not returned to caller
- Motif 3: limits depend on metadata that is not preserved across stages

## Typical Asymmetry

- What was checked in one path but missing in another: One stage performed checking, but a later admission, batching, or execution stage skipped accounting or failed to propagate rejection.

## Patch Pattern

- What the fix changed structurally: The patch changes txpool admission checks to consume CheckedTransaction objects, enforces configured weight limits through tx.Weight(w), updates the add path to validate the checked transaction directly, and adjusts scheduler/test code to batch checked transactions and remove them by hash.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
