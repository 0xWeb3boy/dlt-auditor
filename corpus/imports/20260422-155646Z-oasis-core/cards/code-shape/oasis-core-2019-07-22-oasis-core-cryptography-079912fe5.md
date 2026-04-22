# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-07-22-oasis-core-cryptography-079912fe5`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-signer-authorization-check`

## Code Shape Summary

- Short description of what the buggy code looked like: Authorization of storage receipt signers was incomplete at the compute/storage boundary: the shown code treated attached signatures as acceptable without the demonstrated enforcement that the signer belonged to the current epoch's authorized storage committee.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: The fix introduced a helper on the epoch snapshot that checks whether each signature belongs to a current storage committee member, then wired that helper into the two shown compute-committee receipt paths so they reject non-member signers immediately.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
