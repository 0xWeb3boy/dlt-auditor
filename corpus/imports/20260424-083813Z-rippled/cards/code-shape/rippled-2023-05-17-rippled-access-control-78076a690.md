# Code-Shape Card

## Metadata

- ID: `rippled-2023-05-17-rippled-access-control-78076a690`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-input-acceptance`

## Code Shape Summary

- The change hardens rippled RPC account parsing by removing legacy RPC::accountFromString handling from multiple account-query handlers and requiring parseBase58<AccountID> instead. Reusable shape: check for input-and-state-invariant-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact input-and-state-invariant-validation check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Replace permissive legacy credential-aware parsing at RPC boundaries with strict account-ID parsing, and remove obsolete strict controls once non-account identifiers are no longer accepted.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the input-and-state-invariant-validation gate runs before the state-changing branch.

## Patch Pattern

- Replace permissive legacy credential-aware parsing at RPC boundaries with strict account-ID parsing, and remove obsolete strict controls once non-account identifiers are no longer accepted.

## False Match Warnings

- No evidence shows secrets were actually written to logs, errors, or responses.
- No evidence shows an authorization bypass or access to protected account data.
