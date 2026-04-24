# Code-Shape Card

## Metadata

- ID: `rippled-2025-04-30-rippled-access-control-ceeb11aee`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-state-invariant-hardening`

## Code Shape Summary

- The patch strengthens an AccountRoot deletion invariant in rippled by adding a check that a deleted account must not have a non-zero owner count. Reusable shape: check for input-and-state-invariant-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact input-and-state-invariant-validation check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Extend an existing ledger invariant with an additional field-level consistency check for deleted AccountRoot state.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the input-and-state-invariant-validation gate runs before the state-changing branch.

## Patch Pattern

- Extend an existing ledger invariant with an additional field-level consistency check for deleted AccountRoot state.

## False Match Warnings

- No supplied evidence shows normal transaction processing could previously delete such an account.
- No concrete exploit path, attacker-controlled trigger, fund loss, or denial-of-service impact is shown.
