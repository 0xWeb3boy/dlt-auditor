# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-08-23-oasis-core-rpc-client-api-4333549d8`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`

## Code Shape Summary

- Short description of what the buggy code looked like: A security-sensitive RPC handler relied on comments describing required authorization and attestation-policy checks instead of enforcing those checks in code after parsing the request.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: The fix adds a mandatory authenticator call in the VerifyEvidence handler using the request signer key and decoded evidence, and aborts the RPC when that validation fails. Related proxy changes centralize endpoint/authenticator creation and make the development skip-auth mode explicit rather than leaving enforcement absent in the normal handler path.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
