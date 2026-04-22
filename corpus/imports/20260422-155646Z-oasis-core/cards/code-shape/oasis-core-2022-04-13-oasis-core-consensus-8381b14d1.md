# Code-Shape Card

## Metadata

- ID: `oasis-core-2022-04-13-oasis-core-consensus-8381b14d1`
- Bug family: `resource_accounting_and_limits`
- Bug class: `insufficient-resource-limits`

## Code Shape Summary

- Short description of what the buggy code looked like: The txpool's checked-transaction state was missing sender metadata that later sender-aware queue logic could use, and the post-CheckTx scheduling stage did not retain enough index information to surface queue-admission failure back to the correct caller. That is a local admission-path consistency gap. The provided evidence does not by itself prove a security vulnerability beyond that.

## Search Motifs

- Motif 1: resource or gas accounting missing on one mutation path
- Motif 2: downstream queue failure logged but not returned to caller
- Motif 3: limits depend on metadata that is not preserved across stages

## Typical Asymmetry

- What was checked in one path but missing in another: One stage performed checking, but a later admission, batching, or execution stage skipped accounting or failed to propagate rejection.

## Patch Pattern

- What the fix changed structurally: The patch stores sender identity and sender sequence on checked txpool transactions, adds a unique fallback sender when the runtime provides none, and preserves original batch indices while processing checked transactions. That lets the code associate a later scheduling rejection with the correct transaction result and return a 'txpool' error to the submitter.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
