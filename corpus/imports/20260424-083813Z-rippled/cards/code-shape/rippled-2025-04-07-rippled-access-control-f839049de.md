# Code-Shape Card

## Metadata

- ID: `rippled-2025-04-07-rippled-access-control-f839049de`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-recursion-boundary`

## Code Shape Summary

- The evidence supports a correctness and possible hardening change in rippled vault asset handling: requireAuth changes its recursion guard from depth > maxFreezeCheckDepth to depth >= maxFreezeCheckDepth, VaultCreate checks MPT assets for excessive recursive vault-share... Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact authorization check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Tighten a recursive boundary check and align vault create/deposit validation with existing authorization helpers, while keeping documented business-rule exceptions narrow.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Tighten a recursive boundary check and align vault create/deposit validation with existing authorization helpers, while keeping documented business-rule exceptions narrow.

## False Match Warnings

- No exploit scenario is shown.
- No proof that the old off-by-one caused denial of service, authorization bypass, or incorrect ledger acceptance.
