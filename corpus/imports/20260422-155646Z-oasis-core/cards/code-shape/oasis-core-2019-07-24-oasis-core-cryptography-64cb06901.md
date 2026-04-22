# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-07-24-oasis-core-cryptography-64cb06901`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-signer-authorization`

## Code Shape Summary

- Short description of what the buggy code looked like: Compute-commitment admission validated the transaction-scheduler signature's cryptographic correctness but did not verify that the signer belonged to the active transaction scheduler committee.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: The fix replaced the old transaction-scheduler signature check with a call that verifies the signature against the active 'scheduler.KindTransactionScheduler' committee. It also introduced a generalized verifier interface so callers specify which committee kind a signature must belong to, and updated related storage call sites to use that interface.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
