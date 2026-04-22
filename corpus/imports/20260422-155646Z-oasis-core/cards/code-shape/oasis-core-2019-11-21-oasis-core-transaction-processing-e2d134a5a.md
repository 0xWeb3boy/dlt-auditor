# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-11-21-oasis-core-transaction-processing-e2d134a5a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-gas-accounting`

## Code Shape Summary

- Short description of what the buggy code looked like: Some registry transaction handlers did not perform the now-shown explicit per-operation gas charge before continuing with stateful processing. The evidence supports inconsistent or absent handler-level metering, not a signature or replay-validation defect.

## Search Motifs

- Motif 1: resource or gas accounting missing on one mutation path
- Motif 2: downstream queue failure logged but not returned to caller
- Motif 3: limits depend on metadata that is not preserved across stages

## Typical Asymmetry

- What was checked in one path but missing in another: One stage performed checking, but a later admission, batching, or execution stage skipped accounting or failed to propagate rejection.

## Patch Pattern

- What the fix changed structurally: The fix inserts gas-accounting code into the affected registry handlers. Each added block fetches consensus parameters, returns on error, and invokes ctx.Gas().UseGas with the relevant registry gas operation. In registerNode, the charge is applied only when the registration is entity-signed, matching the comment that node-signed registrations are prepaid.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
