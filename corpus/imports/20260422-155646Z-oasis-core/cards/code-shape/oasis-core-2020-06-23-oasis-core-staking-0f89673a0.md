# Code-Shape Card

## Metadata

- ID: `oasis-core-2020-06-23-oasis-core-staking-0f89673a0`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-update-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The update-verification check was attached to the wrong control-flow condition. The code keyed verification on the non-new, non-expired branch instead of on the existence of a prior stored node record.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: 'registerNode' now calls 'registry.VerifyNodeUpdate(...)' whenever a prior node record exists, including when that record is expired, before accepting the new descriptor and writing it to state. The tests were adjusted to keep prior registrations around for later update-oriented cases.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
