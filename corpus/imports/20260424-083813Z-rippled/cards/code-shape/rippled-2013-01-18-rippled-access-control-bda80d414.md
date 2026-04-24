# Code-Shape Card

## Metadata

- ID: `rippled-2013-01-18-rippled-access-control-bda80d414`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The patch is security-relevant and likely hardens RPC admin access, but the supplied evidence does not fully prove an exploitable authorization bypass. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact authorization check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Move RPC role assignment from connection/interface assumptions to request-time authorization checks, and reject forbidden requests before invoking the RPC command handler.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Move RPC role assignment from connection/interface assumptions to request-time authorization checks, and reject forbidden requests before invoking the RPC command handler.

## False Match Warnings

- No iAdminGet implementation is supplied to confirm exact credential or policy behavior.
- No evidence shows whether the affected RPC listeners were reachable by untrusted attackers.
