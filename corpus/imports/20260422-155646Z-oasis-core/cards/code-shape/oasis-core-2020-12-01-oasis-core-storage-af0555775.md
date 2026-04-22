# Code-Shape Card

## Metadata

- ID: `oasis-core-2020-12-01-oasis-core-storage-af0555775`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`

## Code Shape Summary

- Short description of what the buggy code looked like: A debug-only configuration path existed inside the 'CheckTx' admission entrypoint, allowing normal admission validation to be bypassed when locally enabled. The supplied evidence shows that this bypass mechanism was removed, but it does not show that the option was reachable by attackers, used in production, or led to invalid transactions being finalized.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: The patch removed the 'disableCheckTx' special case from the ABCI mux 'CheckTx' path, removed the related debug transaction-expiry state, removed test-runner support for enabling the option, and updated the oversized transaction workload to stop tolerating behavior caused by skipped 'CheckTx'.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
