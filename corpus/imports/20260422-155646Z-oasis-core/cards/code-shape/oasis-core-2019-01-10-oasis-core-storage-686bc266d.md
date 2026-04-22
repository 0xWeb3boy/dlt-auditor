# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-01-10-oasis-core-storage-686bc266d`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports only a narrow conclusion: authorization and state validation were not enforced as early or as uniformly as the updated code now enforces them. It does not prove a concrete exploitable root cause beyond that.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: The code now rejects unauthorized peers at the P2P boundary, routes committee batch handling through queueExternalBatch with a returned error path, and makes handleExternalBatch fail when the node is not in the expected state. These changes tighten validation and make rejection explicit.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
