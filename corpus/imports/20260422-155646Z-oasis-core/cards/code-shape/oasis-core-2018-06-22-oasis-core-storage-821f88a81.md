# Code-Shape Card

## Metadata

- ID: `oasis-core-2018-06-22-oasis-core-storage-821f88a81`
- Bug family: `authz_and_role_gates`
- Bug class: `consensus-role-accounting`

## Code Shape Summary

- Short description of what the buggy code looked like: The visible evidence suggests the aggregation logic depended on signer role, but the pre-patch path used a broad membership check and a generic aggregation flow. That likely made role-specific accounting fragile or incorrect under concurrent message handling.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: The patch first changes the verification-side code to locate the specific committee entry for the signing key. It then changes the aggregation handlers to branch on sender role and use role-specific queueing and thresholds instead of a single generic queue.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
