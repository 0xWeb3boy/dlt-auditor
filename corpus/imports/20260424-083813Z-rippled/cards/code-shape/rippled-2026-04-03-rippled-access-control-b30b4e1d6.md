# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-03-rippled-access-control-b30b4e1d6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-accounting-invariant`

## Code Shape Summary

- The grounded finding is lending protocol accounting hardening, not access control. The strongest supported change is in LoanBrokerInvariant.cpp, where the invariant now computes the pseudo-account balance once and, under fixSecurity3_1_3, rejects non-delete LoanBroker states... Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact accounting-integrity check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Add an amendment-gated invariant check that constrains recorded protocol accounting to the actual backing pseudo-account balance, with an explicit lifecycle exception for deletion.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Add an amendment-gated invariant check that constrains recorded protocol accounting to the actual backing pseudo-account balance, with an explicit lifecycle exception for deletion.

## False Match Warnings

- No concrete transaction sequence is shown that creates sfCoverAvailable greater than pseudoBalance.
- No advisory, issue text, or vulnerability description is supplied.
