# Code-Shape Card

## Metadata

- ID: `oasis-core-2024-07-04-oasis-core-cryptography-8e2f08bb2`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- Short description of what the buggy code looked like: The shown code indicates an under-specified authorization boundary for key-share queries and missing admission-time validation for a policy field related to query authorization semantics.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: The patch tightens worker-side authorization for CHURP key-share queries by consulting runtime descriptor information, and it adds consensus-side validation so 'MayQuery' cannot be set before the feature release that supports it.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
