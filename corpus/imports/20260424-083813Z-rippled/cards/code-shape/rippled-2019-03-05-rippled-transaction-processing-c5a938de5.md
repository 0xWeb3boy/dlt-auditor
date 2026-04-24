# Code-Shape Card

## Metadata

- ID: `rippled-2019-03-05-rippled-transaction-processing-c5a938de5`
- Bug family: `authz_and_role_gates`
- Bug class: `regular-key-authorization-hardening`

## Code Shape Summary

- The patch changes transaction authorization and SetRegularKey validation so that, under the fixMasterKeyAsRegularKey amendment, an account cannot set sfRegularKey to the same account ID as sfAccount and master-key disable handling is separated from regular-key authorization. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact authorization check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Add explicit preflight validation for an invalid key configuration and separate master-key disable checks from regular-key authorization in the single-sign path.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Add explicit preflight validation for an invalid key configuration and separate master-key disable checks from regular-key authorization in the single-sign path.

## False Match Warnings

- No evidence shows an unauthorized third party could set another account's regular key.
- No evidence demonstrates transaction forgery, account takeover, or direct fund loss.
